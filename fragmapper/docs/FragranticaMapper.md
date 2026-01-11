# FragranticaMapper (Placeholder)

**Version:** 1.1.0  
**Last-Updated:** 2026-01-10

## MODE
MODE: DESC_TO_FRAGRANTICA_URL

## Purpose
Placeholder skill module for mapping a user-provided fragrance description to a single canonical Fragrantica.com fragrance page.

## Status
Not implemented yet. No mapping workflow is defined here.

## Output Contract
Must mirror the ParfumoMapper output contract style:
- Single confident match: output ONLY the URL on a single line
- Ambiguous: first line AMBIGUOUS, then up to 5 candidate URLs, one per line
- No match: output exactly NOT_FOUND

Do not output anything else.
