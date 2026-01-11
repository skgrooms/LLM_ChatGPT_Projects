"""
Pydantic schemas for FragMapper output contracts.

Version: 1.0.0
Last-Updated: 2026-01-10
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Mode(str, Enum):
    """Supported FragMapper modes."""

    DESC_TO_PARFUMO_URL = "DESC_TO_PARFUMO_URL"
    DESC_TO_FRAGRANTICA_URL = "DESC_TO_FRAGRANTICA_URL"
    PARFUMO_TO_FRAGRANTICA_URL = "PARFUMO_TO_FRAGRANTICA_URL"


class MatchStatus(str, Enum):
    """Match result status."""

    MATCH = "MATCH"
    AMBIGUOUS = "AMBIGUOUS"
    NO_MATCH = "NO_MATCH"
    EXCLUDED = "EXCLUDED"


class AlternateMatch(BaseModel):
    """An alternate candidate match."""

    url: str = Field(..., description="Candidate URL")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0 and 1"
    )
    note: Optional[str] = Field(None, description="Brief explanation for this candidate")


class InputSummary(BaseModel):
    """Extracted/normalized input information."""

    brand: Optional[str] = Field(None, description="Brand/house name")
    name: Optional[str] = Field(None, description="Fragrance name (core name)")
    concentration: Optional[str] = Field(
        None, description="Concentration (EDT/EDP/Parfum/Extrait/Cologne)"
    )
    size_ml: Optional[int] = Field(None, description="Size in milliliters")
    flanker: Optional[str] = Field(
        None, description="Flanker/edition terms (Intense, Absolu, etc.)"
    )
    year: Optional[int] = Field(None, description="Release year if present")
    target: Optional[str] = Field(None, description="Target audience (men/women/unisex)")


class DebugInfo(BaseModel):
    """Debug information for troubleshooting."""

    excluded_terms_found: list[str] = Field(
        default_factory=list, description="Exclusion terms detected in input"
    )
    normalized_title: Optional[str] = Field(
        None, description="Normalized version of the input"
    )
    search_queries_used: list[str] = Field(
        default_factory=list, description="Search queries attempted"
    )


class MapperOutput(BaseModel):
    """
    Standard output envelope for all FragMapper modes.

    This ensures deterministic, structured outputs that can be:
    - Regression tested by comparing JSON
    - Parsed without ambiguity
    - Versioned and validated
    """

    mode: Mode = Field(..., description="The mode that was executed")
    input_summary: InputSummary = Field(
        default_factory=InputSummary,
        description="Extracted/normalized input information",
    )
    status: MatchStatus = Field(..., description="Match result status")
    primary_url: Optional[str] = Field(
        None, description="Primary matched URL (if status is MATCH)"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence for primary match"
    )
    alternates: list[AlternateMatch] = Field(
        default_factory=list,
        description="Alternate candidates (if status is AMBIGUOUS)",
        max_length=5,
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Short, structured reasons only",
    )
    debug: DebugInfo = Field(
        default_factory=DebugInfo,
        description="Debug information for troubleshooting",
    )

    def to_simple_output(self) -> str:
        """
        Convert to simple string output as per the output contract.

        Returns:
            - Single URL for MATCH
            - "AMBIGUOUS" + URLs for AMBIGUOUS
            - "NOT_FOUND" for NO_MATCH or EXCLUDED
        """
        if self.status == MatchStatus.MATCH and self.primary_url:
            return self.primary_url
        elif self.status == MatchStatus.AMBIGUOUS and self.alternates:
            urls = [alt.url for alt in self.alternates]
            return "AMBIGUOUS\n" + "\n".join(urls)
        else:
            return "NOT_FOUND"


class RouterInput(BaseModel):
    """Input to the FragMapper router."""

    mode: Mode = Field(..., description="The mode to execute")
    input_text: str = Field(..., description="The input text to process")


class RulesConfig(BaseModel):
    """Configuration loaded from fragmapper_rules.yml."""

    model_config = {"extra": "allow"}  # Allow additional fields from YAML

    version: str = Field(..., description="Rules version")
