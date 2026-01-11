"""
FragMapper - Agent system for mapping fragrance descriptions to canonical URLs.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "FragServices"

from fragmapper.router import FragMapperRouter
from fragmapper.models.schemas import (
    MapperOutput,
    MatchStatus,
    Mode,
)

__all__ = [
    "FragMapperRouter",
    "MapperOutput",
    "MatchStatus",
    "Mode",
]
