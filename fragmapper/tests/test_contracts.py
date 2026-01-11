"""
Contract Tests for FragMapper.

These tests verify invariants that must ALWAYS hold true, regardless of
whether the actual mapping implementation is complete. They test:

1. Output format contracts (to_simple_output formatting)
2. Router dispatch behavior
3. Schema validation
4. "No extra output" rules
5. Exclusion detection (implemented)

These tests should NEVER fail. If they do, something fundamental is broken.

Version: 1.0.0
"""

import pytest
from pathlib import Path

from fragmapper.router import FragMapperRouter
from fragmapper.models.schemas import (
    Mode,
    MatchStatus,
    MapperOutput,
    InputSummary,
    DebugInfo,
    AlternateMatch,
)
from fragmapper.agents.parfumo import ParfumoMapper
from fragmapper.agents.fragrantica import FragranticaMapper
from fragmapper.agents.crosswalk import CrosswalkMapper


class TestOutputContractFormat:
    """
    Tests that output formatting matches the contract exactly.
    
    Contract:
    - MATCH: URL only on single line
    - AMBIGUOUS: "AMBIGUOUS" then URLs, one per line
    - NO_MATCH/EXCLUDED: "NOT_FOUND"
    """

    def test_match_output_is_url_only(self):
        """MATCH status outputs only the URL, nothing else."""
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.MATCH,
            primary_url="https://www.parfumo.com/Perfumes/Dior/Sauvage",
            debug=DebugInfo(),
        )
        simple = output.to_simple_output()
        
        assert simple == "https://www.parfumo.com/Perfumes/Dior/Sauvage"
        assert "\n" not in simple  # Single line
        assert "MATCH" not in simple  # No status label
        assert "confidence" not in simple.lower()  # No extra info

    def test_no_match_output_is_not_found(self):
        """NO_MATCH status outputs exactly 'NOT_FOUND'."""
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.NO_MATCH,
            debug=DebugInfo(),
        )
        simple = output.to_simple_output()
        
        assert simple == "NOT_FOUND"

    def test_excluded_output_is_not_found(self):
        """EXCLUDED status outputs exactly 'NOT_FOUND'."""
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.EXCLUDED,
            debug=DebugInfo(),
        )
        simple = output.to_simple_output()
        
        assert simple == "NOT_FOUND"

    def test_ambiguous_output_format(self):
        """AMBIGUOUS status outputs 'AMBIGUOUS' then URLs."""
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.AMBIGUOUS,
            alternates=[
                AlternateMatch(url="https://url1.com", confidence=0.9),
                AlternateMatch(url="https://url2.com", confidence=0.8),
                AlternateMatch(url="https://url3.com", confidence=0.7),
            ],
            debug=DebugInfo(),
        )
        simple = output.to_simple_output()
        lines = simple.split("\n")
        
        assert lines[0] == "AMBIGUOUS"
        assert lines[1] == "https://url1.com"
        assert lines[2] == "https://url2.com"
        assert lines[3] == "https://url3.com"
        assert len(lines) == 4  # Header + 3 URLs

    def test_ambiguous_respects_max_5_alternates(self):
        """AMBIGUOUS outputs at most 5 alternate URLs."""
        output = MapperOutput(
            mode=Mode.DESC_TO_PARFUMO_URL,
            input_summary=InputSummary(),
            status=MatchStatus.AMBIGUOUS,
            alternates=[
                AlternateMatch(url=f"https://url{i}.com", confidence=0.9 - i * 0.1)
                for i in range(5)
            ],
            debug=DebugInfo(),
        )
        simple = output.to_simple_output()
        lines = simple.split("\n")
        
        assert len(lines) <= 6  # AMBIGUOUS + max 5 URLs


class TestRouterDispatchContract:
    """
    Tests that the router dispatches correctly to skills.
    """

    @pytest.fixture
    def router(self) -> FragMapperRouter:
        """Create a router instance."""
        config_path = Path(__file__).parent.parent / "configs" / "fragmapper_rules.yml"
        return FragMapperRouter(config_path=config_path)

    def test_desc_to_parfumo_dispatches_to_parfumo_mapper(self, router):
        """DESC_TO_PARFUMO_URL mode dispatches to ParfumoMapper."""
        result = router.route(Mode.DESC_TO_PARFUMO_URL, "test input")
        assert result.mode == Mode.DESC_TO_PARFUMO_URL

    def test_desc_to_fragrantica_dispatches_to_fragrantica_mapper(self, router):
        """DESC_TO_FRAGRANTICA_URL mode dispatches to FragranticaMapper."""
        result = router.route(Mode.DESC_TO_FRAGRANTICA_URL, "test input")
        assert result.mode == Mode.DESC_TO_FRAGRANTICA_URL

    def test_crosswalk_dispatches_to_crosswalk_mapper(self, router):
        """PARFUMO_TO_FRAGRANTICA_URL mode dispatches to CrosswalkMapper."""
        result = router.route(Mode.PARFUMO_TO_FRAGRANTICA_URL, "test input")
        assert result.mode == Mode.PARFUMO_TO_FRAGRANTICA_URL

    def test_all_modes_return_mapper_output(self, router):
        """All modes return a valid MapperOutput."""
        for mode in Mode:
            result = router.route(mode, "test input")
            assert isinstance(result, MapperOutput)
            assert result.mode == mode
            assert result.status in MatchStatus


class TestSchemaValidation:
    """
    Tests that schemas enforce validation rules.
    """

    def test_confidence_must_be_0_to_1(self):
        """Confidence scores must be between 0 and 1."""
        # Valid confidence
        alt = AlternateMatch(url="https://test.com", confidence=0.5)
        assert alt.confidence == 0.5

        # Edge cases
        alt_zero = AlternateMatch(url="https://test.com", confidence=0.0)
        assert alt_zero.confidence == 0.0
        
        alt_one = AlternateMatch(url="https://test.com", confidence=1.0)
        assert alt_one.confidence == 1.0

    def test_mapper_output_requires_mode(self):
        """MapperOutput requires mode field."""
        with pytest.raises(Exception):  # Pydantic validation error
            MapperOutput(
                input_summary=InputSummary(),
                status=MatchStatus.NO_MATCH,
                debug=DebugInfo(),
            )

    def test_mapper_output_requires_status(self):
        """MapperOutput requires status field."""
        with pytest.raises(Exception):  # Pydantic validation error
            MapperOutput(
                mode=Mode.DESC_TO_PARFUMO_URL,
                input_summary=InputSummary(),
                debug=DebugInfo(),
            )


class TestExclusionDetection:
    """
    Tests that exclusion detection works correctly.
    This IS implemented and should always work.
    """

    @pytest.fixture
    def mapper(self) -> ParfumoMapper:
        """Create a ParfumoMapper instance."""
        return ParfumoMapper()

    def test_decant_is_excluded(self, mapper):
        """'decant' triggers exclusion."""
        result = mapper.execute("Dior Sauvage 5ml decant")
        assert result.status == MatchStatus.EXCLUDED
        assert "decant" in result.debug.excluded_terms_found

    def test_sample_is_excluded(self, mapper):
        """'sample' triggers exclusion."""
        result = mapper.execute("Chanel Bleu sample vial")
        assert result.status == MatchStatus.EXCLUDED
        assert "sample" in result.debug.excluded_terms_found

    def test_tester_is_excluded(self, mapper):
        """'tester' triggers exclusion."""
        result = mapper.execute("Tom Ford Oud Wood tester bottle")
        assert result.status == MatchStatus.EXCLUDED
        assert "tester" in result.debug.excluded_terms_found

    def test_empty_bottle_is_excluded(self, mapper):
        """'empty bottle' triggers exclusion."""
        result = mapper.execute("Creed Aventus empty bottle only")
        assert result.status == MatchStatus.EXCLUDED
        assert "empty bottle" in result.debug.excluded_terms_found

    def test_box_only_is_excluded(self, mapper):
        """'box only' triggers exclusion."""
        result = mapper.execute("YSL La Nuit box only no bottle")
        assert result.status == MatchStatus.EXCLUDED
        assert "box only" in result.debug.excluded_terms_found

    def test_non_excluded_input_not_excluded(self, mapper):
        """Normal input without exclusion terms is not EXCLUDED."""
        result = mapper.execute("Dior Sauvage EDP 100ml")
        assert result.status != MatchStatus.EXCLUDED
        assert len(result.debug.excluded_terms_found) == 0


class TestVersioning:
    """
    Tests that version information is available and consistent.
    """

    def test_router_has_version(self):
        """Router has VERSION constant."""
        assert hasattr(FragMapperRouter, "VERSION")
        assert FragMapperRouter.VERSION == "1.0.0"

    def test_parfumo_mapper_has_version(self):
        """ParfumoMapper has VERSION constant."""
        assert hasattr(ParfumoMapper, "VERSION")
        assert ParfumoMapper.VERSION == "1.0.0"

    def test_fragrantica_mapper_has_version(self):
        """FragranticaMapper has VERSION constant."""
        assert hasattr(FragranticaMapper, "VERSION")
        assert FragranticaMapper.VERSION == "1.0.0"

    def test_crosswalk_mapper_has_version(self):
        """CrosswalkMapper has VERSION constant."""
        assert hasattr(CrosswalkMapper, "VERSION")
        assert CrosswalkMapper.VERSION == "1.0.0"

    def test_router_version_info_complete(self):
        """Router provides complete version info."""
        config_path = Path(__file__).parent.parent / "configs" / "fragmapper_rules.yml"
        router = FragMapperRouter(config_path=config_path)
        
        version_info = router.get_version_info()
        
        assert "router" in version_info
        assert "config_version" in version_info
        assert "skill_DESC_TO_PARFUMO_URL" in version_info
