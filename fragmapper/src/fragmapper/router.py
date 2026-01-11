"""
FragMapper Router - Thin dispatcher for skill modules.

Version: 1.0.0
Last-Updated: 2026-01-10

Purpose:
    Routes user requests to exactly one skill module based on MODE.
    
Non-negotiables:
    - Execute only the selected skill module
    - Do not mix instructions from different skills
    - Enforce the output contract of the selected skill
    - Do not add any output beyond what the selected skill's output contract allows
"""

from pathlib import Path
from typing import Optional

import yaml

from fragmapper.agents.parfumo import ParfumoMapper
from fragmapper.agents.fragrantica import FragranticaMapper
from fragmapper.agents.crosswalk import CrosswalkMapper
from fragmapper.agents.base import BaseAgent
from fragmapper.models.schemas import (
    Mode,
    MapperOutput,
    MatchStatus,
    RouterInput,
    RulesConfig,
)


class FragMapperRouter:
    """
    Main router/orchestrator for FragMapper.

    The orchestrator:
    - Passes inputs
    - Chooses which agent runs
    - Never reasons deeply itself

    Think: dispatcher, not thinker.
    """

    VERSION = "1.0.0"
    LAST_UPDATED = "2026-01-10"

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the router with optional config path.

        Args:
            config_path: Path to fragmapper_rules.yml. If None, uses default location.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self._skills = self._initialize_skills()

    def _get_default_config_path(self) -> Path:
        """Get the default config file path."""
        # Navigate from src/fragmapper to configs/
        package_root = Path(__file__).parent.parent.parent.parent
        return package_root / "configs" / "fragmapper_rules.yml"

    def _load_config(self) -> dict:
        """Load rules configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _initialize_skills(self) -> dict[Mode, BaseAgent]:
        """Initialize skill modules for each mode."""
        return {
            Mode.DESC_TO_PARFUMO_URL: ParfumoMapper(config=self.config),
            Mode.DESC_TO_FRAGRANTICA_URL: FragranticaMapper(config=self.config),
            Mode.PARFUMO_TO_FRAGRANTICA_URL: CrosswalkMapper(config=self.config),
        }

    def route(self, mode: Mode, input_text: str) -> MapperOutput:
        """
        Route input to the appropriate skill based on MODE.

        Args:
            mode: The mode to execute
            input_text: The input text to process

        Returns:
            MapperOutput with the result
        """
        skill = self._skills.get(mode)

        if skill is None:
            # If MODE is missing or unsupported, return NOT_FOUND
            return MapperOutput(
                mode=mode,
                status=MatchStatus.NO_MATCH,
                notes=["Unsupported MODE"],
            )

        return skill.execute(input_text)

    def process(self, router_input: RouterInput) -> MapperOutput:
        """
        Process a RouterInput object.

        Args:
            router_input: Validated router input

        Returns:
            MapperOutput with the result
        """
        return self.route(router_input.mode, router_input.input_text)

    def get_simple_output(self, mode: Mode, input_text: str) -> str:
        """
        Get simplified string output as per output contract.

        Args:
            mode: The mode to execute
            input_text: The input text to process

        Returns:
            Simple string: URL, "AMBIGUOUS" + URLs, or "NOT_FOUND"
        """
        result = self.route(mode, input_text)
        return result.to_simple_output()

    @property
    def supported_modes(self) -> list[Mode]:
        """Return list of supported modes."""
        return list(self._skills.keys())

    def get_version_info(self) -> dict[str, str]:
        """Return version information for all components."""
        return {
            "router": self.VERSION,
            "router_last_updated": self.LAST_UPDATED,
            "config_version": self.config.get("version", "unknown"),
            **{
                f"skill_{mode.value}": skill.VERSION
                for mode, skill in self._skills.items()
            },
        }
