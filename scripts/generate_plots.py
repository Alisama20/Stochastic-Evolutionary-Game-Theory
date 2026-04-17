"""
Generate all publication-quality plots for the paper.

This script sweeps key parameters and reproduces all result figures.
"""

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from fixation_probability import run_simulation, plot_results


def main():
    """Run full parameter sweep and generate all plots."""
    
    print("=" * 70)
    print("STOCHASTIC EVOLUTIONARY GAME THEORY — Parameter Sweep")
    print("=" * 70)
    print()
    
    # Run main simulation
    results_sigma_minus, results_sigma_plus = run_simulation()
    
    # Generate plots
    plot_results(results_sigma_minus, results_sigma_plus)
    
    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Fixation probability range (σ₀=-1): {min(results_sigma_minus['fixation_prob']):.3f} — {max(results_sigma_minus['fixation_prob']):.3f}")
    print(f"Fixation probability range (σ₀=+1): {min(results_sigma_plus['fixation_prob']):.3f} — {max(results_sigma_plus['fixation_prob']):.3f}")
    print()
    print(f"Fixation time range (σ₀=-1): {min([t for t in results_sigma_minus['fixation_time'] if t > 0]):.1f} — {max(results_sigma_minus['fixation_time']):.1f} generations")
    print(f"Fixation time range (σ₀=+1): {min([t for t in results_sigma_plus['fixation_time'] if t > 0]):.1f} — {max(results_sigma_plus['fixation_time']):.1f} generations")
    print()


if __name__ == '__main__':
    main()
