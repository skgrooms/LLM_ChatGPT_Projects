"""
Base Agent class for FragMapper skills.

Version: 1.0.0
Last-Updated: 2026-01-10
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from fragmapper.models.schemas import MapperOutput, Mode


class BaseAgent(ABC):
    """
    Abstract base class for all FragMapper skill agents.

    Each agent must have:
    - One responsibility
    - One output format
    - One validation surface
    """

    VERSION = "1.0.0"
    MODE: Mode  # Each subclass must define its mode

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the agent with optional configuration.

        Args:
            config: Configuration dictionary from fragmapper_rules.yml
        """
        self.config = config or {}
        self._mode_config = self._get_mode_config()

    def _get_mode_config(self) -> dict[str, Any]:
        """Get configuration specific to this agent's mode."""
        modes = self.config.get("modes", {})
        return modes.get(self.MODE.value, {}) if hasattr(self, "MODE") else {}

    @abstractmethod
    def execute(self, input_text: str) -> MapperOutput:
        """
        Execute the agent's main task.

        Args:
            input_text: The input text to process

        Returns:
            MapperOutput with the result
        """
        pass

    def get_hard_rules(self) -> list[str]:
        """Get hard rules for this mode from config."""
        return self._mode_config.get("hard_rules", [])

    def get_output_contract(self) -> dict[str, str]:
        """Get output contract for this mode from config."""
        return self._mode_config.get("output_contract", {})
