"""Tests for quantum_predictor module (SBZET v2025.9)"""

import pytest

from app.modules.quantum_predictor import (
    QuantumParams,
    calibrate_bounds,
    describe,
    ready,
    success_prob,
)


class TestQuantumParams:
    """Test QuantumParams dataclass"""

    def test_default_params(self):
        params = QuantumParams()
        assert params.E0 == 3.0
        assert params.k == 1.25
        assert params.alpha == 0.9
        assert params.beta == 8.0
        assert params.gamma == 0.8

    def test_custom_params(self):
        params = QuantumParams(E0=5.0, k=2.0, alpha=0.5, beta=10.0, gamma=1.0)
        assert params.E0 == 5.0
        assert params.k == 2.0
        assert params.alpha == 0.5
        assert params.beta == 10.0
        assert params.gamma == 1.0


class TestSuccessProb:
    """Test SBZET success_prob function"""

    def test_basic_calculation(self):
        """Test basic SBZET calculation"""
        prob = success_prob(5.0, 0.1, 2.0)
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0

    def test_monotonicity_energy(self):
        """Test E↑ ⇒ p↑ (energy increases, probability increases)"""
        prob1 = success_prob(3.0, 0.1, 1.0)
        prob2 = success_prob(5.0, 0.1, 1.0)
        prob3 = success_prob(7.0, 0.1, 1.0)

        assert prob1 <= prob2 <= prob3, f"Energy monotonicity failed: {prob1} <= {prob2} <= {prob3}"

    def test_monotonicity_distance(self):
        """Test D↑ ⇒ p↓ (distance increases, probability decreases)"""
        prob1 = success_prob(5.0, 0.1, 0.5)
        prob2 = success_prob(5.0, 0.1, 2.0)
        prob3 = success_prob(5.0, 0.1, 5.0)

        assert prob1 >= prob2 >= prob3, f"Distance monotonicity failed: {prob1} >= {prob2} >= {prob3}"

    def test_monotonicity_gravity(self):
        """Test Δg↑ ⇒ p↑ (gravity increases, probability increases)"""
        prob1 = success_prob(5.0, -0.1, 2.0)
        prob2 = success_prob(5.0, 0.0, 2.0)
        prob3 = success_prob(5.0, 0.1, 2.0)

        assert prob1 <= prob2 <= prob3, f"Gravity monotonicity failed: {prob1} <= {prob2} <= {prob3}"

    def test_boundary_values(self):
        """Test boundary and edge cases"""
        prob_zero_d = success_prob(5.0, 0.1, 0.0)
        assert 0.0 <= prob_zero_d <= 1.0

        prob_high_e = success_prob(100.0, 0.1, 1.0)
        assert 0.0 <= prob_high_e <= 1.0

        prob_high_d = success_prob(5.0, 0.1, 100.0)
        assert 0.0 <= prob_high_d <= 1.0

    def test_custom_params(self):
        """Test with custom parameters"""
        custom_params = QuantumParams(E0=2.0, k=2.0, alpha=0.5, beta=5.0, gamma=0.5)
        prob = success_prob(4.0, 0.2, 1.5, custom_params)
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0

    def test_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        with pytest.raises(ValueError, match="Mesafe faktörü negatif olamaz"):
            success_prob(5.0, 0.1, -1.0)

        with pytest.raises((ValueError, TypeError)):
            success_prob("invalid", 0.1, 1.0)  # type: ignore

    def test_extreme_values(self):
        """Test extreme input values for numerical stability"""
        prob_large = success_prob(1000.0, 0.0, 0.1)
        assert 0.0 <= prob_large <= 1.0

        prob_small = success_prob(-1000.0, 0.0, 0.1)
        assert 0.0 <= prob_small <= 1.0


class TestModuleFunctions:
    """Test module utility functions"""

    def test_calibrate_bounds(self):
        """Test calibrate_bounds placeholder"""
        result = calibrate_bounds()
        assert isinstance(result, dict)
        assert result["status"] == "not_implemented"
        assert result["version"] == "v2025.9"

    def test_ready(self):
        """Test ready function"""
        assert ready() is True

    def test_describe(self):
        """Test describe function"""
        desc = describe()
        assert isinstance(desc, dict)
        assert desc["name"] == "quantum_predictor"
        assert desc["version"] == "SBZET v2025.9"
        assert desc["ready"] is True
        assert "formula" in desc
        assert "parameters" in desc
