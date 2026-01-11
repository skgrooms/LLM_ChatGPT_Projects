#!/usr/bin/env python3
"""
Sync Project Files Tool

Purpose:
    Copies source-of-truth files from docs/ and configs/ into project_files/.
    This ensures the bundled agent instructions stay in sync with the sources.

Usage:
    python tools/sync_project_files.py

When to run:
    After any tagged release that modifies:
    - docs/*.md
    - configs/fragmapper_rules.yml
    - README.md
"""

import shutil
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIGS_DIR = PROJECT_ROOT / "configs"
PROJECT_FILES_DIR = PROJECT_ROOT / "project_files"

# Files to sync from docs/
DOCS_FILES = [
    "ParfumoMapper.md",
    "FragranticaMapper.md",
    "CrosswalkMapper.md",
    "FragMapper_Router.md",
]

# Files to sync from configs/
CONFIG_FILES = [
    "fragmapper_rules.yml",
]

# Files to sync from root
ROOT_FILES = [
    "README.md",
]


# ============================================================================
# Sync Logic
# ============================================================================


def sync_file(source: Path, dest: Path) -> bool:
    """
    Copy source to dest if they differ or dest doesn't exist.
    
    Returns True if a copy was made, False if already in sync.
    """
    if not source.exists():
        print(f"  ⚠ Source missing: {source.relative_to(PROJECT_ROOT)}")
        return False
    
    if dest.exists():
        source_content = source.read_bytes()
        dest_content = dest.read_bytes()
        if source_content == dest_content:
            print(f"  ✓ Already in sync: {dest.name}")
            return False
    
    shutil.copy2(source, dest)
    print(f"  → Copied: {source.relative_to(PROJECT_ROOT)} → {dest.relative_to(PROJECT_ROOT)}")
    return True


def main():
    """Sync all source files to project_files/."""
    print("=" * 60)
    print("FragMapper: Sync Project Files")
    print("=" * 60)
    
    # Ensure project_files directory exists
    PROJECT_FILES_DIR.mkdir(exist_ok=True)
    
    copied_count = 0
    
    # Sync docs
    print("\nSyncing docs/*.md →")
    for filename in DOCS_FILES:
        source = DOCS_DIR / filename
        dest = PROJECT_FILES_DIR / filename
        if sync_file(source, dest):
            copied_count += 1
    
    # Sync configs
    print("\nSyncing configs/*.yml →")
    for filename in CONFIG_FILES:
        source = CONFIGS_DIR / filename
        dest = PROJECT_FILES_DIR / filename
        if sync_file(source, dest):
            copied_count += 1
    
    # Sync root files
    print("\nSyncing root files →")
    for filename in ROOT_FILES:
        source = PROJECT_ROOT / filename
        dest = PROJECT_FILES_DIR / filename
        if sync_file(source, dest):
            copied_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    if copied_count == 0:
        print("✓ All files already in sync!")
    else:
        print(f"✓ Synced {copied_count} file(s)")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
