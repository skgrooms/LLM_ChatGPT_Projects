"""Agent modules for FragMapper."""

from fragmapper.agents.base import BaseAgent
from fragmapper.agents.parfumo import ParfumoMapper
from fragmapper.agents.fragrantica import FragranticaMapper
from fragmapper.agents.crosswalk import CrosswalkMapper

__all__ = [
    "BaseAgent",
    "ParfumoMapper",
    "FragranticaMapper",
    "CrosswalkMapper",
]
