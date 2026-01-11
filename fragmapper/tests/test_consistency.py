"""
Consistency Tests - Verifies version alignment and bundle sync.

Purpose:
    Catches drift between source-of-truth files and bundled copies.
    Ensures all version numbers match across the project.

Run:
    pytest tests/test_consistency.py -v
"""

import re
from pathlib import Path

import pytest
import yaml


# ============================================================================
# Path Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIGS_DIR = PROJECT_ROOT / "configs"
PROJECT_FILES_DIR = PROJECT_ROOT / "project_files"
SRC_DIR = PROJECT_ROOT / "src" / "fragmapper"


# ============================================================================
# Version Extraction Helpers
# ============================================================================


def get_pyproject_version() -> str:
    """Extract version from pyproject.toml."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def get_rules_yml_version() -> str:
    """Extract version from configs/fragmapper_rules.yml."""
    rules_path = CONFIGS_DIR / "fragmapper_rules.yml"
    with open(rules_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("version", "").strip('"')


def get_markdown_version(md_path: Path) -> str | None:
    """Extract Version from a markdown file's header."""
    content = md_path.read_text(encoding="utf-8")
    # Match: **Version:** 1.0.0 or Version: 1.0.0
    match = re.search(r"\*?\*?Version:?\*?\*?\s*(\d+\.\d+\.\d+)", content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def get_python_module_version(py_path: Path) -> str | None:
    """Extract VERSION constant or docstring Version from a Python file."""
    content = py_path.read_text(encoding="utf-8")
    
    # Try VERSION class attribute: VERSION = "1.0.0"
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    
    # Try docstring Version: header
    match = re.search(r"Version:\s*(\d+\.\d+\.\d+)", content)
    if match:
        return match.group(1)
    
    return None


# ============================================================================
# Test: Version Consistency
# ============================================================================


class TestVersionConsistency:
    """All version numbers must match across the project."""

    def test_pyproject_version_exists(self):
        """pyproject.toml must have a version."""
        version = get_pyproject_version()
        assert version, "pyproject.toml version is empty"
        assert re.match(r"^\d+\.\d+\.\d+$", version), f"Invalid version format: {version}"

    def test_rules_yml_matches_pyproject(self):
        """configs/fragmapper_rules.yml version must match pyproject.toml."""
        pyproject_version = get_pyproject_version()
        rules_version = get_rules_yml_version()
        assert rules_version == pyproject_version, (
            f"fragmapper_rules.yml version ({rules_version}) "
            f"!= pyproject.toml ({pyproject_version})"
        )

    def test_router_version_matches_pyproject(self):
        """router.py VERSION must match pyproject.toml."""
        pyproject_version = get_pyproject_version()
        router_path = SRC_DIR / "router.py"
        router_version = get_python_module_version(router_path)
        assert router_version == pyproject_version, (
            f"router.py VERSION ({router_version}) "
            f"!= pyproject.toml ({pyproject_version})"
        )

    @pytest.mark.parametrize("agent_name", ["parfumo", "fragrantica", "crosswalk"])
    def test_agent_versions_match_pyproject(self, agent_name: str):
        """Each agent's docstring Version must match pyproject.toml."""
        pyproject_version = get_pyproject_version()
        agent_path = SRC_DIR / "agents" / f"{agent_name}.py"
        agent_version = get_python_module_version(agent_path)
        assert agent_version == pyproject_version, (
            f"{agent_name}.py version ({agent_version}) "
            f"!= pyproject.toml ({pyproject_version})"
        )

    @pytest.mark.parametrize(
        "doc_name",
        [
            "ParfumoMapper.md",
            "FragranticaMapper.md",
            "CrosswalkMapper.md",
            "FragMapper_Router.md",
        ],
    )
    def test_docs_versions_match_pyproject(self, doc_name: str):
        """docs/*.md Version headers must match pyproject.toml."""
        pyproject_version = get_pyproject_version()
        doc_path = DOCS_DIR / doc_name
        if not doc_path.exists():
            pytest.skip(f"{doc_name} does not exist")
        doc_version = get_markdown_version(doc_path)
        assert doc_version == pyproject_version, (
            f"docs/{doc_name} version ({doc_version}) "
            f"!= pyproject.toml ({pyproject_version})"
        )


# ============================================================================
# Test: Bundle Sync (project_files/ must match sources)
# ============================================================================


class TestBundleSync:
    """project_files/ must be byte-identical to source files."""

    @pytest.mark.parametrize(
        "doc_name",
        [
            "ParfumoMapper.md",
            "FragranticaMapper.md",
            "CrosswalkMapper.md",
            "FragMapper_Router.md",
        ],
    )
    def test_project_files_md_matches_docs(self, doc_name: str):
        """project_files/*.md must be byte-identical to docs/*.md."""
        source_path = DOCS_DIR / doc_name
        bundle_path = PROJECT_FILES_DIR / doc_name

        if not source_path.exists():
            pytest.skip(f"docs/{doc_name} does not exist")
        if not bundle_path.exists():
            pytest.fail(f"project_files/{doc_name} is missing (expected copy from docs/)")

        source_content = source_path.read_bytes()
        bundle_content = bundle_path.read_bytes()

        assert source_content == bundle_content, (
            f"project_files/{doc_name} differs from docs/{doc_name}. "
            f"Run: python tools/sync_project_files.py"
        )

    def test_project_files_rules_yml_matches_configs(self):
        """project_files/fragmapper_rules.yml must match configs/fragmapper_rules.yml."""
        source_path = CONFIGS_DIR / "fragmapper_rules.yml"
        bundle_path = PROJECT_FILES_DIR / "fragmapper_rules.yml"

        if not bundle_path.exists():
            pytest.fail(
                "project_files/fragmapper_rules.yml is missing "
                "(expected copy from configs/)"
            )

        source_content = source_path.read_bytes()
        bundle_content = bundle_path.read_bytes()

        assert source_content == bundle_content, (
            "project_files/fragmapper_rules.yml differs from configs/fragmapper_rules.yml. "
            "Run: python tools/sync_project_files.py"
        )


# ============================================================================
# Test: README sync (optional - README.md in project_files)
# ============================================================================


class TestReadmeSync:
    """README.md in project_files should match root README.md if present."""

    def test_project_files_readme_matches_root(self):
        """project_files/README.md must match root README.md."""
        source_path = PROJECT_ROOT / "README.md"
        bundle_path = PROJECT_FILES_DIR / "README.md"

        if not source_path.exists():
            pytest.skip("Root README.md does not exist")
        if not bundle_path.exists():
            pytest.skip("project_files/README.md does not exist")

        source_content = source_path.read_bytes()
        bundle_content = bundle_path.read_bytes()

        assert source_content == bundle_content, (
            "project_files/README.md differs from root README.md. "
            "Run: python tools/sync_project_files.py"
        )
