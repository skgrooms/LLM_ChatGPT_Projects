# Changelog

All notable changes to FragMapper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-01-10

### Changed
- Default to most recent formulation/version when no year is specified and Parfumo has multiple year/version pages for the same fragrance name + concentration
- Updated ParfumoMapper.md: Step 1 (extraction), Step 3 (scoring preferences and hard rules), and Edge Cases sections
- Updated fragmapper_rules.yml: Added hard rule for year/version handling

## [1.0.0] - 2026-01-10

### Added
- Initial project structure following Agent OS architecture
- FragMapper Router for MODE-based skill selection
- ParfumoMapper skill for DESC_TO_PARFUMO_URL mode
- FragranticaMapper placeholder skill
- CrosswalkMapper placeholder skill
- Rules-as-data configuration (fragmapper_rules.yml)
- Pydantic output schemas for structured responses
- Golden test set infrastructure
- Text normalization utilities

### Architecture
- Separated authority (config files) from conversation (runtime)
- Implemented Router + Skill Modules + Rules-as-Data pattern
- Single responsibility per agent/skill

### Documentation
- Router specification (FragMapper_Router.md)
- ParfumoMapper specification (ParfumoMapper.md)
- FragranticaMapper placeholder specification
- CrosswalkMapper placeholder specification

---

## Release Checklist

Before each release:
- [ ] Version bumped in all modified files
- [ ] CHANGELOG.md updated
- [ ] Golden 5 tests passed
- [ ] Files synced to ChatGPT Project (if using UI)
- [ ] Git tag created
