# FragMapper Tests

## Test Categories

This test suite is organized into two categories as per the architecture guidance:

### 1. Contract Tests (Always Pass)

**Files:** `test_contracts.py`

These tests verify invariants that must ALWAYS hold true, regardless of whether the actual mapping implementation is complete:

- Output format contracts (`to_simple_output()` formatting)
- Router dispatch behavior
- Schema validation
- Exclusion detection (implemented)
- Version information

**Run these after every code change.** If any fail, something fundamental is broken.

```bash
pytest tests/test_contracts.py -v
```

### 2. Unit Tests (Implementation Tests)

**Files:** `test_router.py`, `test_parfumo.py`

These test specific implementation details:

- Router initialization and configuration
- Normalizer text processing
- URL building utilities
- Component extraction

```bash
pytest tests/test_router.py tests/test_parfumo.py -v
```

### 3. UI Regression Tests (Manual)

**Files:** `cases.json`, `expected/DESC_TO_PARFUMO_URL.jsonl`

These are for **MANUAL** regression testing in the ChatGPT UI, NOT automated Python tests.

The Python placeholder implementation will NOT pass these tests because actual web search/LLM integration is not implemented.

**When to run these:**
- Monthly
- After any spec/rule file changes
- After ChatGPT model updates

**How to run:**
1. Open the ChatGPT Project
2. Paste test inputs from `cases.json`
3. Compare outputs against `expected/DESC_TO_PARFUMO_URL.jsonl`

## Running All Automated Tests

```bash
# From project root
pytest tests/ -v

# With coverage
pytest tests/ --cov=fragmapper --cov-report=term-missing
```

## Adding New Tests

- **Contract tests:** Add to `test_contracts.py` - things that must ALWAYS be true
- **Implementation tests:** Add to `test_router.py` or `test_parfumo.py`
- **UI regression cases:** Add to `cases.json` with expected output in `expected/`
