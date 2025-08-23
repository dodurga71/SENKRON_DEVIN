"""Tests for unified_predictor module (Fusion Core)"""

from datetime import date

from app.modules.unified_predictor import (
    _calculate_astro_score,
    _sigmoid,
    describe,
    ready,
    unified_score,
)


class TestUnifiedScore:
    """Test unified_score function"""

    def test_basic_calculation(self):
        """Test basic unified score calculation"""
        result = unified_score(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            E=5.0,
            delta_g=0.1,
            D=2.0
        )

        assert isinstance(result, dict)
        assert "astro" in result
        assert "quant" in result
        assert "final" in result
        assert "weights" in result
        assert "metadata" in result

        assert 0.0 <= result["astro"] <= 1.0
        assert 0.0 <= result["quant"] <= 1.0
        assert 0.0 <= result["final"] <= 1.0

    def test_custom_weights(self):
        """Test unified score with custom weights"""
        result = unified_score(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            E=5.0,
            delta_g=0.1,
            D=2.0,
            weights=(0.3, 0.7)
        )

        assert result["weights"] == (0.3, 0.7)
        assert 0.0 <= result["final"] <= 1.0

    def test_ablation_study(self):
        """Test that final score is influenced by both components"""
        result_astro = unified_score(
            date(2024, 1, 1), date(2024, 1, 31),
            E=5.0, delta_g=0.1, D=2.0,
            weights=(0.9, 0.1)
        )

        result_quant = unified_score(
            date(2024, 1, 1), date(2024, 1, 31),
            E=5.0, delta_g=0.1, D=2.0,
            weights=(0.1, 0.9)
        )

        assert result_astro["final"] != result_quant["final"]

    def test_invalid_weights(self):
        """Test error handling for invalid weights"""
        result = unified_score(
            date(2024, 1, 1), date(2024, 1, 31),
            E=5.0, delta_g=0.1, D=2.0,
            weights=(1.5, 0.5)  # Invalid: > 1.0
        )

        assert "error" in result
        assert result["final"] == 0.0

    def test_invalid_dates(self):
        """Test error handling for invalid date range"""
        result = unified_score(
            start_date=date(2024, 1, 31),
            end_date=date(2024, 1, 1),  # End before start
            E=5.0,
            delta_g=0.1,
            D=2.0
        )

        assert "error" in result
        assert result["final"] == 0.0

    def test_metadata_content(self):
        """Test metadata content in response"""
        result = unified_score(
            date(2024, 1, 1), date(2024, 1, 31),
            E=5.0, delta_g=0.1, D=2.0
        )

        metadata = result["metadata"]
        assert "start_date" in metadata
        assert "end_date" in metadata
        assert "quantum_params" in metadata
        assert metadata["quantum_params"]["E"] == 5.0
        assert metadata["quantum_params"]["delta_g"] == 0.1
        assert metadata["quantum_params"]["D"] == 2.0


class TestAstroScore:
    """Test _calculate_astro_score function"""

    def test_astro_score_calculation(self):
        """Test astro score calculation"""
        score = _calculate_astro_score(date(2024, 1, 1), date(2024, 12, 31))
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_astro_score_empty_period(self):
        """Test astro score with no events"""
        score = _calculate_astro_score(date(2025, 1, 1), date(2025, 1, 2))
        assert score == 0.0

    def test_astro_score_single_day(self):
        """Test astro score for single day"""
        score = _calculate_astro_score(date(2024, 1, 15), date(2024, 1, 15))
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestSigmoid:
    """Test _sigmoid function"""

    def test_sigmoid_basic(self):
        """Test basic sigmoid function"""
        assert _sigmoid(0.0) == 0.5
        assert 0.0 < _sigmoid(-1.0) < 0.5
        assert 0.5 < _sigmoid(1.0) < 1.0

    def test_sigmoid_extreme_values(self):
        """Test sigmoid with extreme values"""
        assert _sigmoid(1000.0) == 1.0
        assert _sigmoid(-1000.0) == 0.0

    def test_sigmoid_monotonicity(self):
        """Test sigmoid monotonicity"""
        values = [-5, -1, 0, 1, 5]
        sigmoid_values = [_sigmoid(x) for x in values]

        for i in range(len(sigmoid_values) - 1):
            assert sigmoid_values[i] <= sigmoid_values[i + 1]


class TestModuleFunctions:
    """Test module utility functions"""

    def test_ready(self):
        """Test ready function"""
        assert ready() is True

    def test_describe(self):
        """Test describe function"""
        desc = describe()
        assert isinstance(desc, dict)
        assert desc["name"] == "unified_predictor"
        assert "version" in desc
        assert desc["ready"] is True
        assert "formula" in desc
        assert "default_weights" in desc
        assert "components" in desc
