"""
Text normalization utilities for FragMapper.

Version: 1.0.0
Last-Updated: 2026-01-10
"""

import re
from typing import Any, Optional


class TextNormalizer:
    """
    Text normalization and extraction utilities.

    Handles:
    - Common synonyms (edp/eau de parfum, parfum/extrait)
    - Token cleanup (remove "spray", "authentic", "100%", emojis, etc.)
    - Exclusion detection (decant, sample, empty bottle, box only)
    - Pack/size parsing (100 ml, 3.4 oz, "set", "2x")
    """

    # Concentration synonyms and mappings
    CONCENTRATION_PATTERNS = {
        r"\b(edp|eau\s+de\s+parfum)\b": "EDP",
        r"\b(edt|eau\s+de\s+toilette)\b": "EDT",
        r"\b(edc|eau\s+de\s+cologne|cologne)\b": "EDC",
        r"\b(parfum|extrait|extrait\s+de\s+parfum|pure\s+parfum)\b": "Parfum",
    }

    # Default exclusion terms
    DEFAULT_EXCLUSIONS = [
        "decant",
        "sample",
        "empty bottle",
        "box only",
        "tester",
        "travel size",
        "mini",
        "vial",
        "atomizer",
        "refill",
    ]

    # Noise terms to remove
    NOISE_TERMS = [
        r"\b(spray)\b",
        r"\b(authentic)\b",
        r"\b(100%)\b",
        r"\b(genuine)\b",
        r"\b(original)\b",
        r"\b(new\s+in\s+box|nib)\b",
        r"\b(sealed)\b",
        r"\b(brand\s+new)\b",
        r"\b(free\s+shipping)\b",
    ]

    # Size patterns
    SIZE_PATTERNS = [
        r"(\d+(?:\.\d+)?)\s*(ml|milliliter)",
        r"(\d+(?:\.\d+)?)\s*(oz|ounce)",
        r"(\d+(?:\.\d+)?)\s*(fl\.?\s*oz)",
    ]

    # Flanker/edition terms
    FLANKER_TERMS = [
        "intense",
        "absolu",
        "absolute",
        "elixir",
        "sport",
        "nuit",
        "noir",
        "extreme",
        "privee",
        "reserve",
        "limited edition",
        "collector",
        "oud",
        "exclusive",
    ]

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the normalizer with optional config.

        Args:
            config: Configuration dictionary that may contain custom rules
        """
        self.config = config or {}
        self.exclusions = self._load_exclusions()

    def _load_exclusions(self) -> list[str]:
        """Load exclusion terms from config or use defaults."""
        global_config = self.config.get("global", {})
        exclusions = global_config.get("exclusions", self.DEFAULT_EXCLUSIONS)
        return [e.lower() for e in exclusions]

    def normalize(self, text: str) -> str:
        """
        Normalize input text for matching.

        Args:
            text: Raw input text

        Returns:
            Normalized text
        """
        result = text.lower()

        # Remove noise terms
        for pattern in self.NOISE_TERMS:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)

        # Remove emojis and special characters
        result = re.sub(r"[^\w\s\-\./]", " ", result)

        # Collapse multiple spaces
        result = re.sub(r"\s+", " ", result).strip()

        return result

    def find_exclusions(self, text: str) -> list[str]:
        """
        Find exclusion terms in the text.

        Args:
            text: Input text to check

        Returns:
            List of exclusion terms found
        """
        text_lower = text.lower()
        found = []
        for exclusion in self.exclusions:
            if exclusion in text_lower:
                found.append(exclusion)
        return found

    def extract_components(self, text: str) -> dict[str, Any]:
        """
        Extract fragrance components from text.

        Args:
            text: Input text

        Returns:
            Dictionary with extracted components:
            - brand
            - name
            - concentration
            - size_ml
            - flanker
            - year
            - target
        """
        components: dict[str, Any] = {
            "brand": None,
            "name": None,
            "concentration": None,
            "size_ml": None,
            "flanker": None,
            "year": None,
            "target": None,
        }

        text_lower = text.lower()

        # Extract concentration
        for pattern, concentration in self.CONCENTRATION_PATTERNS.items():
            if re.search(pattern, text_lower):
                components["concentration"] = concentration
                break

        # Extract size
        size_ml = self._extract_size_ml(text)
        if size_ml:
            components["size_ml"] = size_ml

        # Extract year (4-digit number between 1900-2100)
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        if year_match:
            components["year"] = int(year_match.group(1))

        # Extract target
        if re.search(r"\b(pour\s+homme|for\s+men|men'?s?)\b", text_lower):
            components["target"] = "men"
        elif re.search(r"\b(pour\s+femme|for\s+women|women'?s?)\b", text_lower):
            components["target"] = "women"
        elif re.search(r"\b(unisex)\b", text_lower):
            components["target"] = "unisex"

        # Extract flanker terms
        for flanker in self.FLANKER_TERMS:
            if flanker.lower() in text_lower:
                components["flanker"] = flanker.title()
                break

        # Note: Brand and Name extraction would typically require
        # a database lookup or more sophisticated NLP.
        # For now, we leave these to be extracted by the LLM/agent.

        return components

    def _extract_size_ml(self, text: str) -> Optional[int]:
        """
        Extract size in milliliters from text.

        Args:
            text: Input text

        Returns:
            Size in ml, or None if not found
        """
        text_lower = text.lower()

        # Try ml patterns first
        ml_match = re.search(r"(\d+(?:\.\d+)?)\s*(ml|milliliter)", text_lower)
        if ml_match:
            return int(float(ml_match.group(1)))

        # Try oz patterns and convert to ml
        oz_match = re.search(r"(\d+(?:\.\d+)?)\s*(oz|ounce|fl\.?\s*oz)", text_lower)
        if oz_match:
            oz_value = float(oz_match.group(1))
            return int(oz_value * 29.5735)  # Convert oz to ml

        return None

    def build_search_query(
        self,
        brand: Optional[str] = None,
        name: Optional[str] = None,
        concentration: Optional[str] = None,
        flanker: Optional[str] = None,
        site: str = "parfumo.com",
    ) -> str:
        """
        Build a search query string.

        Args:
            brand: Brand name
            name: Fragrance name
            concentration: Concentration (EDT, EDP, etc.)
            flanker: Flanker/edition term
            site: Site to search on

        Returns:
            Search query string
        """
        parts = [f"site:{site}", "Perfumes"]

        if brand:
            parts.append(brand)
        if name:
            parts.append(f'"{name}"')
        if flanker:
            parts.append(flanker)
        if concentration:
            parts.append(concentration)

        return " ".join(parts)
