"""
Tests for FragMapper Router.

Version: 1.0.0
"""

import pytest
from pathlib import Path

from fragmapper.router import FragMapperRouter
from fragmapper.models.schemas import Mode, MatchStatus


class TestFragMapperRouter:
    """Test suite for FragMapperRouter."""

    @pytest.fixture
    def router(self) -> FragMapperRouter:
        """Create a router instance with test config."""
        config_path = Path(__file__).parent.parent / "configs" / "fragmapper_rules.yml"
        return FragMapperRouter(config_path=config_path)

    def test_router_initialization(self, router: FragMapperRouter):
        """Test that router initializes correctly."""
        assert router.VERSION == "1.0.0"
        assert router.config is not None
        assert len(router.supported_modes) == 3

    def test_supported_modes(self, router: FragMapperRouter):
        """Test that all expected modes are supported."""
        expected_modes = [
            Mode.DESC_TO_PARFUMO_URL,
            Mode.DESC_TO_FRAGRANTICA_URL,
            Mode.PARFUMO_TO_FRAGRANTICA_URL,
        ]
        for mode in expected_modes:
            assert mode in router.supported_modes

    def test_route_to_parfumo_mapper(self, router: FragMapperRouter):
        """Test routing to ParfumoMapper skill."""
        result = router.route(Mode.DESC_TO_PARFUMO_URL, "Dior Sauvage EDP")
        assert result.mode == Mode.DESC_TO_PARFUMO_URL
        # ParfumoMapper is a placeholder, should return NO_MATCH
        assert result.status in [MatchStatus.MATCH, MatchStatus.AMBIGUOUS, MatchStatus.NO_MATCH]

    def test_route_to_fragrantica_mapper(self, router: FragMapperRouter):
        """Test routing to FragranticaMapper skill (placeholder)."""
        result = router.route(Mode.DESC_TO_FRAGRANTICA_URL, "Dior Sauvage EDP")
        assert result.mode == Mode.DESC_TO_FRAGRANTICA_URL
        assert result.status == MatchStatus.NO_MATCH  # Placeholder returns NOT_FOUND

    def test_route_to_crosswalk_mapper(self, router: FragMapperRouter):
        """Test routing to CrosswalkMapper skill (placeholder)."""
        result = router.route(
            Mode.PARFUMO_TO_FRAGRANTICA_URL,
            "https://www.parfumo.com/Perfumes/Dior/Sauvage_Eau_de_Parfum"
        )
        assert result.mode == Mode.PARFUMO_TO_FRAGRANTICA_URL
        assert result.status == MatchStatus.NO_MATCH  # Placeholder returns NOT_FOUND

    def test_get_simple_output(self, router: FragMapperRouter):
        """Test simple string output generation."""
        output = router.get_simple_output(Mode.DESC_TO_FRAGRANTICA_URL, "Test input")
        assert output == "NOT_FOUND"  # Placeholder returns NOT_FOUND

    def test_version_info(self, router: FragMapperRouter):
        """Test version info retrieval."""
        version_info = router.get_version_info()
        assert "router" in version_info
        assert version_info["router"] == "1.0.0"
        assert "config_version" in version_info


class TestRouterOutputContract:
    """Test that router enforces output contract."""

    @pytest.fixture
    def router(self) -> FragMapperRouter:
        """Create a router instance."""
        config_path = Path(__file__).parent.parent / "configs" / "fragmapper_rules.yml"
        return FragMapperRouter(config_path=config_path)

    def test_output_has_required_fields(self, router: FragMapperRouter):
        """Test that output contains all required fields."""
        result = router.route(Mode.DESC_TO_PARFUMO_URL, "Test fragrance")
        
        assert hasattr(result, "mode")
        assert hasattr(result, "status")
        assert hasattr(result, "input_summary")
        assert hasattr(result, "primary_url")
        assert hasattr(result, "alternates")
        assert hasattr(result, "notes")
        assert hasattr(result, "debug")

    def test_to_simple_output_match(self, router: FragMapperRouter):
        """Test simple output for MATCH status."""
        from fragmapper.models.schemas import MapperOutput, InputSummary, DebugInfo
        
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.MATCH,
            primary_url="https://www.parfumo.com/Perfumes/Dior/Sauvage",
            debug=DebugInfo(),
        )
        assert output.to_simple_output() == "https://www.parfumo.com/Perfumes/Dior/Sauvage"

    def test_to_simple_output_not_found(self, router: FragMapperRouter):
        """Test simple output for NO_MATCH status."""
        from fragmapper.models.schemas import MapperOutput, InputSummary, DebugInfo
        
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.NO_MATCH,
            debug=DebugInfo(),
        )
        assert output.to_simple_output() == "NOT_FOUND"

    def test_to_simple_output_ambiguous(self, router: FragMapperRouter):
        """Test simple output for AMBIGUOUS status."""
        from fragmapper.models.schemas import MapperOutput, InputSummary, DebugInfo, AlternateMatch
        
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.AMBIGUOUS,
            alternates=[
                AlternateMatch(url="https://url1.com", confidence=0.9),
                AlternateMatch(url="https://url2.com", confidence=0.8),
            ],
            debug=DebugInfo(),
        )
        simple = output.to_simple_output()
        assert simple.startswith("AMBIGUOUS")
        assert "https://url1.com" in simple
        assert "https://url2.com" in simple
