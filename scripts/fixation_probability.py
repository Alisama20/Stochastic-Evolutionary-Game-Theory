"""
Stochastic Evolutionary Game Theory Simulation
Fixation probability and fixation time under environmental switching

Simulates evolutionary dynamics of two strategies in a finite population
with environmental fluctuations affecting payoffs.
"""

import numpy as np
from numba import jit, prange
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================================
# Core simulation functions (JIT-compiled for speed)
# ============================================================================

@jit(nopython=True)
def uniform(min_val, max_val):
    """Generate uniform random number in [min_val, max_val]"""
    return min_val + np.random.random() * (max_val - min_val)


@jit(nopython=True)
def single_realization(
    N, beta, p_plus, p_minus, sigma_init, n_gens
):
    """
    Run a single realization of the evolutionary game.
    
    Parameters
    ----------
    N : int
        Population size
    beta : float
        Selection strength (inverse temperature)
    p_plus : float
        Probability of environment switching from sigma=+1 to sigma=-1
    p_minus : float
        Probability of environment switching from sigma=-1 to sigma=+1
    sigma_init : float
        Initial environment (+1 or -1)
    n_gens : int
        Number of generations to simulate
        
    Returns
    -------
    fixated : bool
        True if mutant strategy fixed (Na reached N)
    time_to_fixation : int
        Number of generations until fixation (or extinction)
    """
    
    # Payoff matrix constants
    as_ = 1.0
    ds = 1.0
    
    Na = 1  # Start with 1 mutant
    sigma = sigma_init
    
    fixated = False
    time_to_fixation = 0
    
    for t in range(n_gens):
        # ===== Environment switching =====
        u = uniform(0.0, 1.0)
        if sigma == 1.0 and u < p_plus:
            sigma = -1.0
        elif sigma == -1.0 and 1.0 - u < p_minus:
            sigma = 1.0
        
        # ===== Payoff recalculation =====
        bs = 1.0 + 0.5 * sigma
        cs = 1.0 + 0.9 * sigma
        
        # Average payoffs
        if N > 1:
            piA = (Na - 1) * as_ / (N - 1) + (N - Na) * bs / (N - 1)
            piB = Na * cs / (N - 1) + (N - Na - 1) * ds / (N - 1)
        else:
            piA = as_
            piB = ds
        
        # Fitness
        fA = np.exp(beta * piA)
        fB = np.exp(beta * piB)
        fm = (Na * fA + (N - Na) * fB) / N
        
        if fm > 0:
            # Substitution probabilities (Moran process)
            omega_plus = Na * (N - Na) * fA / (N * N * fm)
            omega_minus = Na * (N - Na) * fB / (N * N * fm)
        else:
            omega_plus = 0.0
            omega_minus = 0.0
        
        # ===== Update population =====
        u = uniform(0.0, 1.0)
        if u < omega_plus:
            Na += 1
        elif 1.0 - u < omega_minus:
            Na -= 1
        
        # ===== Check for fixation or extinction =====
        if Na >= N:
            fixated = True
            time_to_fixation = t
            break
        elif Na <= 0:
            time_to_fixation = t
            break
    
    return fixated, time_to_fixation


@jit(nopython=True, parallel=True)
def parallel_simulation(
    N, beta, p_plus, p_minus, sigma_init, n_realizations, n_gens
):
    """
    Run many realizations in parallel.
    
    Returns
    -------
    fixation_prob : float
        Probability of mutant fixation
    avg_fixation_time : float
        Average time to fixation (among fixed realizations)
    """
    
    n_fixed = 0
    total_fixation_time = 0.0
    
    for r in prange(n_realizations):
        fixed, t_fix = single_realization(N, beta, p_plus, p_minus, sigma_init, n_gens)
        if fixed:
            n_fixed += 1
            total_fixation_time += t_fix
    
    fixation_prob = n_fixed / n_realizations
    
    if n_fixed > 0:
        avg_fixation_time = total_fixation_time / (n_fixed * N)
    else:
        avg_fixation_time = 0.0
    
    return fixation_prob, avg_fixation_time


# ============================================================================
# Main simulation
# ============================================================================

def run_simulation():
    """Run the full fixation probability sweep."""
    
    # Parameters
    N = 50
    beta = 0.5
    p_minus = 0.01
    n_realizations = int(1e3)
    n_gens = int(1e3)
    
    # Generate p_plus values (logarithmically spaced)
    p_plus_values = np.logspace(-4, 0, 100)
    
    # Output arrays
    results_sigma_minus = {'p_plus': [], 'fixation_prob': [], 'fixation_time': []}
    results_sigma_plus = {'p_plus': [], 'fixation_prob': [], 'fixation_time': []}
    
    print("Running evolutionary game theory simulation...")
    print(f"Population size: {N}, Selection strength: {beta}")
    print(f"Realizations per p_plus: {int(n_realizations)}")
    print()
    
    for i, p_plus in enumerate(p_plus_values):
        # For each p_plus, simulate both initial environments
        for sigma_init_idx, sigma_init in enumerate([-1.0, 1.0]):
            prob, time = parallel_simulation(
                N, beta, p_plus, p_minus, sigma_init, 
                int(n_realizations), int(n_gens)
            )
            
            if sigma_init_idx == 0:  # sigma = -1
                results_sigma_minus['p_plus'].append(p_plus)
                results_sigma_minus['fixation_prob'].append(prob)
                results_sigma_minus['fixation_time'].append(time)
            else:  # sigma = +1
                results_sigma_plus['p_plus'].append(p_plus)
                results_sigma_plus['fixation_prob'].append(prob)
                results_sigma_plus['fixation_time'].append(time)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i+1}/{len(p_plus_values)} p_plus values completed")
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'figures'
    output_dir.mkdir(exist_ok=True)
    
    np.savez(
        str(output_dir / 'fixation_results.npz'),
        **results_sigma_minus,
        **results_sigma_plus
    )
    
    return results_sigma_minus, results_sigma_plus


def plot_results(results_sigma_minus, results_sigma_plus):
    """Create publication-quality plots."""
    
    output_dir = Path(__file__).parent.parent / 'figures'
    output_dir.mkdir(exist_ok=True)
    
    # Plot 1: Fixation probability vs p_plus
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.semilogx(results_sigma_minus['p_plus'], results_sigma_minus['fixation_prob'], 
                'o-', label=r'$\sigma_0 = -1$', linewidth=2, markersize=6)
    ax.semilogx(results_sigma_plus['p_plus'], results_sigma_plus['fixation_prob'],
                's-', label=r'$\sigma_0 = +1$', linewidth=2, markersize=6)
    
    ax.set_xlabel(r'$p_+$ (switching probability)', fontsize=12)
    ax.set_ylabel('Fixation probability', fontsize=12)
    ax.set_title('Fixation Probability vs Environment Switching Rate', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(str(output_dir / 'fixation_probability.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Average fixation time vs p_plus
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.loglog(results_sigma_minus['p_plus'], results_sigma_minus['fixation_time'],
              'o-', label=r'$\sigma_0 = -1$', linewidth=2, markersize=6)
    ax.loglog(results_sigma_plus['p_plus'], results_sigma_plus['fixation_time'],
              's-', label=r'$\sigma_0 = +1$', linewidth=2, markersize=6)
    
    ax.set_xlabel(r'$p_+$ (switching probability)', fontsize=12)
    ax.set_ylabel('Fixation time (generations)', fontsize=12)
    ax.set_title('Average Fixation Time vs Environment Switching Rate', fontsize=13)
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig(str(output_dir / 'fixation_time.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Plots saved to {output_dir}/")


if __name__ == '__main__':
    results_minus, results_plus = run_simulation()
    plot_results(results_minus, results_plus)
    print("Done!")
