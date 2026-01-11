# FragMapper Change Protocol

**Version:** 1.0.0  
**Last-Updated:** 2026-01-10

## Purpose

This document defines how behavior changes are managed in the FragMapper project.
It prevents configuration drift and ensures consistency across all project artifacts.

---

## Rule 1: No Behavior Changes via Chat Acknowledgements

Chat discussions, verbal agreements, or acknowledgements in conversation **do not** 
constitute behavior changes.

- ❌ "Let's change the output format to include X" in chat → **Not a change**
- ❌ "Okay, I'll remember to do Y from now on" → **Not a change**
- ✅ Code/doc edits + version bump + changelog → **Real change**

---

## Rule 2: Behavior Changes Require the Full Change Cycle

Any change to FragMapper behavior **must** include:

1. **Edit the source of truth:**
   - `docs/*.md` — for skill/router documentation
   - `configs/fragmapper_rules.yml` — for operational rules

2. **Version bump:**
   - Update `version` in `pyproject.toml`
   - Update `version` in `configs/fragmapper_rules.yml`
   - Update `Version:` headers in `docs/*.md`
   - Update `VERSION` constants in `src/fragmapper/router.py` and agents

3. **Changelog:**
   - Add entry to `CHANGELOG.md`

4. **Golden 5 tests:**
   - Ensure all 5 golden test cases pass

5. **Tag:**
   - Create a git tag for the release (e.g., `v1.0.1`)

---

## Rule 3: Sync project_files/ Only from Tagged Releases

The `project_files/` directory is a **bundled snapshot** for agent consumption.

- **Never** edit `project_files/` directly
- **Always** sync from `docs/` and `configs/` after a tagged release
- Use `tools/sync_project_files.py` to sync

```bash
python tools/sync_project_files.py
```

This ensures:
- `project_files/*.md` matches `docs/*.md` byte-for-byte
- `project_files/fragmapper_rules.yml` matches `configs/fragmapper_rules.yml`

---

## Quick Reference

| Action | Required Steps |
|--------|----------------|
| Fix typo in docs | Edit → version bump → changelog → Golden 5 → tag |
| Change output contract | Edit → version bump → changelog → Golden 5 → tag |
| Add exclusion term | Edit rules.yml → version bump → changelog → Golden 5 → tag |
| Discuss potential change | No action until formalized |

---

## Verification

Run the consistency test to verify all versions match and bundles are synced:

```bash
pytest tests/test_consistency.py -v
```
