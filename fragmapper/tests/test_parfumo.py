"""
Tests for ParfumoMapper skill.

Version: 1.0.0
"""

import pytest
from pathlib import Path

from fragmapper.agents.parfumo import ParfumoMapper
from fragmapper.models.schemas import MatchStatus, Mode
from fragmapper.utils.normalizer import TextNormalizer


class TestParfumoMapper:
    """Test suite for ParfumoMapper skill."""

    @pytest.fixture
    def mapper(self) -> ParfumoMapper:
        """Create a ParfumoMapper instance."""
        return ParfumoMapper()

    def test_mapper_initialization(self, mapper: ParfumoMapper):
        """Test that mapper initializes correctly."""
        assert mapper.VERSION == "1.0.0"
        assert mapper.MODE == Mode.DESC_TO_PARFUMO_URL

    def test_execute_returns_mapper_output(self, mapper: ParfumoMapper):
        """Test that execute returns correct type."""
        result = mapper.execute("Dior Sauvage EDP 100ml")
        assert result.mode == Mode.DESC_TO_PARFUMO_URL

    def test_exclusion_detection(self, mapper: ParfumoMapper):
        """Test that exclusion terms are detected."""
        result = mapper.execute("Dior Sauvage EDP 5ml decant")
        assert result.status == MatchStatus.EXCLUDED
        assert "decant" in result.debug.excluded_terms_found

    def test_multiple_exclusions_detected(self, mapper: ParfumoMapper):
        """Test that multiple exclusion terms are detected."""
        result = mapper.execute("Chanel Bleu sample tester vial")
        assert result.status == MatchStatus.EXCLUDED
        assert len(result.debug.excluded_terms_found) >= 2


class TestTextNormalizer:
    """Test suite for TextNormalizer utility."""

    @pytest.fixture
    def normalizer(self) -> TextNormalizer:
        """Create a TextNormalizer instance."""
        return TextNormalizer()

    def test_normalize_removes_noise(self, normalizer: TextNormalizer):
        """Test that noise terms are removed."""
        result = normalizer.normalize("Dior Sauvage EDP 100ml spray authentic new in box")
        assert "spray" not in result.lower()
        assert "authentic" not in result.lower()
        assert "new in box" not in result.lower()

    def test_find_exclusions(self, normalizer: TextNormalizer):
        """Test exclusion term detection."""
        exclusions = normalizer.find_exclusions("Chanel Bleu 5ml decant sample")
        assert "decant" in exclusions
        assert "sample" in exclusions

    def test_extract_concentration_edp(self, normalizer: TextNormalizer):
        """Test EDP concentration extraction."""
        components = normalizer.extract_components("Dior Sauvage Eau de Parfum")
        assert components["concentration"] == "EDP"

    def test_extract_concentration_edt(self, normalizer: TextNormalizer):
        """Test EDT concentration extraction."""
        components = normalizer.extract_components("Chanel Bleu EDT for men")
        assert components["concentration"] == "EDT"

    def test_extract_size_ml(self, normalizer: TextNormalizer):
        """Test size extraction in ml."""
        components = normalizer.extract_components("Dior Sauvage EDP 100ml")
        assert components["size_ml"] == 100

    def test_extract_size_oz(self, normalizer: TextNormalizer):
        """Test size extraction in oz (converted to ml)."""
        components = normalizer.extract_components("Dior Sauvage EDP 3.4 oz")
        assert components["size_ml"] == 100  # 3.4 oz ≈ 100 ml

    def test_extract_year(self, normalizer: TextNormalizer):
        """Test year extraction."""
        components = normalizer.extract_components("Chanel No 5 Parfum 2020 edition")
        assert components["year"] == 2020

    def test_extract_target_men(self, normalizer: TextNormalizer):
        """Test target extraction for men."""
        components = normalizer.extract_components("Dior Sauvage pour homme")
        assert components["target"] == "men"

    def test_extract_target_women(self, normalizer: TextNormalizer):
        """Test target extraction for women."""
        components = normalizer.extract_components("Chanel No 5 pour femme")
        assert components["target"] == "women"

    def test_extract_flanker(self, normalizer: TextNormalizer):
        """Test flanker term extraction."""
        components = normalizer.extract_components("Dior Sauvage Intense")
        assert components["flanker"] == "Intense"

    def test_build_search_query(self, normalizer: TextNormalizer):
        """Test search query building."""
        query = normalizer.build_search_query(
            brand="Dior",
            name="Sauvage",
            concentration="EDP",
            site="parfumo.com"
        )
        assert "site:parfumo.com" in query
        assert "Dior" in query
        assert '"Sauvage"' in query
        assert "EDP" in query


class TestParfumoUrlGeneration:
    """Test URL generation utilities."""

    @pytest.fixture
    def mapper(self) -> ParfumoMapper:
        """Create a ParfumoMapper instance."""
        return ParfumoMapper()

    def test_build_parfumo_url(self, mapper: ParfumoMapper):
        """Test Parfumo URL building."""
        url = mapper._build_parfumo_url("Dior", "Sauvage Eau de Parfum")
        assert url == "https://www.parfumo.com/Perfumes/Dior/Sauvage_Eau_de_Parfum"

    def test_build_parfumo_url_with_spaces(self, mapper: ParfumoMapper):
        """Test URL building handles spaces correctly."""
        url = mapper._build_parfumo_url("Tom Ford", "Oud Wood")
        assert url == "https://www.parfumo.com/Perfumes/Tom_Ford/Oud_Wood"
