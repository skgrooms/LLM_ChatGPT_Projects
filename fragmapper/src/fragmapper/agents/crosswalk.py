"""
CrosswalkMapper Skill - Maps Parfumo URLs to Fragrantica URLs.

Skill: CrosswalkMapper
Mode: PARFUMO_TO_FRAGRANTICA_URL
Version: 1.1.0
Output-Contract: 1.1.0
Last-Updated: 2026-01-10

Status: Placeholder - Not implemented yet
"""

from typing import Any, Optional

from fragmapper.agents.base import BaseAgent
from fragmapper.models.schemas import (
    DebugInfo,
    InputSummary,
    MapperOutput,
    MatchStatus,
    Mode,
)


class CrosswalkMapper(BaseAgent):
    """
    CrosswalkMapper (Placeholder) - Maps Parfumo URLs to Fragrantica URLs.

    Purpose:
        Placeholder skill module for mapping a Parfumo fragrance page
        (or Parfumo-identified fragrance) to the equivalent canonical
        Fragrantica.com fragrance page.

    Status:
        Not implemented yet. No mapping workflow is defined here.

    Output Contract:
        Must mirror the ParfumoMapper output contract style:
        - Single confident match: output ONLY the URL on a single line
        - Ambiguous: first line AMBIGUOUS, then up to 5 candidate URLs
        - No match: output exactly NOT_FOUND
    """

    VERSION = "1.1.0"
    MODE = Mode.PARFUMO_TO_FRAGRANTICA_URL

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize CrosswalkMapper with config."""
        super().__init__(config)

    def execute(self, input_text: str) -> MapperOutput:
        """
        Execute the Crosswalk mapping workflow.

        Currently a placeholder that returns NOT_FOUND.

        Args:
            input_text: Parfumo URL or Parfumo brand/name

        Returns:
            MapperOutput with NOT_FOUND status
        """
        return MapperOutput(
            mode=self.MODE,
            input_summary=InputSummary(),
            status=MatchStatus.NO_MATCH,
            debug=DebugInfo(),
            notes=["CrosswalkMapper is not implemented yet"],
        )
