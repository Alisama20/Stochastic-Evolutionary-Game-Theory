"""
Utility functions for evolutionary game theory simulations.
"""

import numpy as np
from pathlib import Path


def load_results(output_dir='figures'):
    """Load simulation results from .npz file."""
    npz_path = Path(output_dir) / 'fixation_results.npz'
    if npz_path.exists():
        data = np.load(str(npz_path))
        return dict(data)
    else:
        raise FileNotFoundError(f"Results file not found: {npz_path}")


def save_txt_output(p_plus_values, fixation_probs, filename='prob.txt'):
    """Save results in plain text format for legacy compatibility."""
    with open(filename, 'w') as f:
        for p, fp in zip(p_plus_values, fixation_probs):
            f.write(f"{p:e}    {fp:.6f}\n")


def compute_statistics(time_to_fixation_array):
    """Compute mean and std of fixation times."""
    valid_times = time_to_fixation_array[time_to_fixation_array > 0]
    if len(valid_times) > 0:
        return {
            'mean': np.mean(valid_times),
            'std': np.std(valid_times),
            'min': np.min(valid_times),
            'max': np.max(valid_times),
            'median': np.median(valid_times),
            'n_fixed': len(valid_times)
        }
    else:
        return None


if __name__ == '__main__':
    # Quick test
    try:
        results = load_results()
        print("Loaded results successfully")
        print(f"Available keys: {list(results.keys())}")
    except FileNotFoundError as e:
        print(f"No results file yet. Run fixation_probability.py first.\n{e}")
