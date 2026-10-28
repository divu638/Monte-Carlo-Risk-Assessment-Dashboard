"""
Test Suite: NumPy Vectorized Monte Carlo VaR Engine
Verifies:
- Statistical sanity (meanLoss <= valueAtRisk95 <= worstCase)
- Deterministic reproducibility with random seed
- Bounded iteration counts and histogram bin integration
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))
from app import run_monte_carlo


def test_monte_carlo_ordering():
    """Verify that statistical loss outputs satisfy natural ordering: mean <= VaR(95) <= Worst."""
    sim = run_monte_carlo(likelihood_val=4, impact_val=4, financial_base=1_000_000, iterations=3000, seed=42)
    assert sim["meanLoss"] <= sim["valueAtRisk95"]
    assert sim["valueAtRisk95"] <= sim["worstCase"]
    assert sim["iterations"] == 3000
    assert "methodology" in sim


def test_monte_carlo_seed_reproducibility():
    """Verify that running with an identical seed produces exactly identical results."""
    sim1 = run_monte_carlo(likelihood_val=3, impact_val=3, financial_base=500_000, iterations=1000, seed=123)
    sim2 = run_monte_carlo(likelihood_val=3, impact_val=3, financial_base=500_000, iterations=1000, seed=123)
    assert sim1["meanLoss"] == sim2["meanLoss"]
    assert sim1["valueAtRisk95"] == sim2["valueAtRisk95"]
    assert sim1["worstCase"] == sim2["worstCase"]


def test_monte_carlo_histogram_bins():
    """Verify that the sum of histogram bucket frequencies covers all simulation trials."""
    sim = run_monte_carlo(likelihood_val=5, impact_val=5, financial_base=2_000_000, iterations=2000, seed=99)
    total_histogram_freq = sum(b["frequency"] for b in sim["histogram"])
    assert total_histogram_freq == 2000
    assert len(sim["histogram"]) == 10
