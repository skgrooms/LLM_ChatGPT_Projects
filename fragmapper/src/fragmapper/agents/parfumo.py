"""
ParfumoMapper Skill - Maps fragrance descriptions to Parfumo URLs.

Skill: ParfumoMapper
Mode: DESC_TO_PARFUMO_URL
Version: 1.0.0
Output-Contract: 1.0.0
Last-Updated: 2026-01-10
"""

from typing import Any, Optional

from fragmapper.agents.base import BaseAgent
from fragmapper.models.schemas import (
    AlternateMatch,
    DebugInfo,
    InputSummary,
    MapperOutput,
    MatchStatus,
    Mode,
)
from fragmapper.utils.normalizer import TextNormalizer


class ParfumoMapper(BaseAgent):
    """
    ParfumoMapper - Maps messy fragrance descriptions to Parfumo.com URLs.

    Purpose:
        Given a user-provided fragrance description, output the Parfumo
        fragrance URL that corresponds to it.

    Non-negotiables:
        - Output must be extremely simple and usable without further parsing
        - Do not include explanations unless output contract requires it
        - Prefer correctness over guessing
        - Use web browsing when mapping (search Parfumo and confirm the target page)
        - Prefer returning AMBIGUOUS over asking questions
        - Keep the user's workflow fast: map and output
    """

    VERSION = "1.0.0"
    MODE = Mode.DESC_TO_PARFUMO_URL

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize ParfumoMapper with config."""
        super().__init__(config)
        self.normalizer = TextNormalizer(config)

    def execute(self, input_text: str) -> MapperOutput:
        """
        Execute the Parfumo mapping workflow.

        Workflow:
        1. Normalize & Extract Clues
        2. Search Strategy (Web)
        3. Candidate Scoring (Choose best page)
        4. Confidence Threshold

        Args:
            input_text: Free-text fragrance description

        Returns:
            MapperOutput with Parfumo URL or AMBIGUOUS/NOT_FOUND
        """
        # Step 1: Normalize & Extract Clues
        input_summary, debug_info = self._extract_clues(input_text)

        # Check for exclusions
        if debug_info.excluded_terms_found:
            return MapperOutput(
                mode=self.MODE,
                input_summary=input_summary,
                status=MatchStatus.EXCLUDED,
                debug=debug_info,
                notes=["Input contains exclusion terms"],
            )

        # Step 2-4: Search, Score, and Determine Confidence
        # NOTE: This is a placeholder implementation.
        # In production, this would integrate with:
        # - Web search API (to search site:parfumo.com)
        # - Or LLM with web browsing capability
        # - Or a pre-built Parfumo database

        result = self._search_and_match(input_summary, debug_info)
        return result

    def _extract_clues(
        self, input_text: str
    ) -> tuple[InputSummary, DebugInfo]:
        """
        Extract clues from the input text.

        From the description, extract:
        - Brand / house
        - Fragrance name (core name)
        - Flanker / edition terms
        - Concentration (EDT/EDP/Parfum/Extrait/Cologne)
        - Release year (if present)
        - Target (men/women/unisex)
        - Key notes
        - Bottle cues
        """
        normalized = self.normalizer.normalize(input_text)
        excluded = self.normalizer.find_exclusions(input_text)

        # Extract components using normalizer
        components = self.normalizer.extract_components(input_text)

        input_summary = InputSummary(
            brand=components.get("brand"),
            name=components.get("name"),
            concentration=components.get("concentration"),
            size_ml=components.get("size_ml"),
            flanker=components.get("flanker"),
            year=components.get("year"),
            target=components.get("target"),
        )

        debug_info = DebugInfo(
            normalized_title=normalized,
            excluded_terms_found=excluded,
        )

        return input_summary, debug_info

    def _search_and_match(
        self, input_summary: InputSummary, debug_info: DebugInfo
    ) -> MapperOutput:
        """
        Search Parfumo and find matching fragrance page.

        This is a placeholder that should be replaced with actual
        web search integration or database lookup.
        """
        # Build search query
        query_parts = []
        if input_summary.brand:
            query_parts.append(input_summary.brand)
        if input_summary.name:
            query_parts.append(input_summary.name)
        if input_summary.flanker:
            query_parts.append(input_summary.flanker)
        if input_summary.concentration:
            query_parts.append(input_summary.concentration)

        if not query_parts:
            return MapperOutput(
                mode=self.MODE,
                input_summary=input_summary,
                status=MatchStatus.NO_MATCH,
                debug=debug_info,
                notes=["Insufficient information to search"],
            )

        search_query = f"site:parfumo.com Perfumes {' '.join(query_parts)}"
        debug_info.search_queries_used.append(search_query)

        # PLACEHOLDER: Actual implementation would:
        # 1. Execute web search
        # 2. Parse results
        # 3. Score candidates
        # 4. Return best match or AMBIGUOUS

        # For now, return NOT_FOUND as this requires external integration
        return MapperOutput(
            mode=self.MODE,
            input_summary=input_summary,
            status=MatchStatus.NO_MATCH,
            debug=debug_info,
            notes=[
                "Placeholder implementation - requires web search integration",
                f"Would search: {search_query}",
            ],
        )

    def _build_parfumo_url(self, brand: str, name: str) -> str:
        """
        Build a Parfumo URL from brand and fragrance name.

        Args:
            brand: Brand name
            name: Fragrance name

        Returns:
            Parfumo URL
        """
        # Parfumo URL pattern: https://www.parfumo.com/Perfumes/{Brand}/{Name}
        # Spaces are replaced with underscores
        brand_slug = brand.replace(" ", "_")
        name_slug = name.replace(" ", "_")
        return f"https://www.parfumo.com/Perfumes/{brand_slug}/{name_slug}"
