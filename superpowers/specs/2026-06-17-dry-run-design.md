# Dry Run Mode Design

**Date:** 2026-06-17  
**Status:** Approved

## Summary

Add `--dry-run` CLI flag that runs the full Horizon pipeline (real scraping, dedup, filtering, output) while skipping all LLM API calls. Saves output to the standard `data/summaries/` path. Does not send email, webhook, or copy to `docs/_posts/`.

## Motivation

Allow testing the pipeline end-to-end without incurring LLM costs. Useful for verifying source configuration, checking what content is being scraped, and debugging the pipeline locally.

## Architecture

### New file: `src/ai/dry_run.py`

`DryRunAIClient` implements `AIClient`. The `complete()` method inspects the `system` prompt to determine call type and returns mock JSON immediately without any network call.

| Call type | Detection (system contains) | Mock response |
|---|---|---|
| Content analysis | default | `{"score": 8.0, "reason": "[dry-run]", "summary": "<title from user prompt>", "tags": ["dry-run"]}` |
| Topic dedup | `"deduplication"` | `{"duplicates": []}` |
| Concept extraction | `"concepts"` | `{"queries": []}` |
| Content enrichment | `"technical writer"` | Template fields in en+zh using title/summary from user prompt |
| Translation fallback | `"translator"` | `{"title_zh": "<title>", "summary_zh": "<summary>"}` |

Score fixed at **8.0** — above the default threshold of 7.0 so all scraped items pass through to the final output.

### Changes to `src/orchestrator.py`

- `__init__` gains `dry_run: bool = False`
- All four `create_ai_client(self.config.ai)` calls replaced with `self._make_ai_client()`
- `_make_ai_client()` returns `DryRunAIClient()` when `self.dry_run` else `create_ai_client(self.config.ai)`
- When `dry_run=True`: skip email send, skip webhook send, skip `docs/_posts/` copy

### Changes to `src/main.py`

- Add `--dry-run` argument to argparse
- Pass `dry_run=args.dry_run` to `HorizonOrchestrator`
- Print yellow notice: `[DRY RUN] LLM calls skipped — output saved locally`

### Changes to `src/ai/__init__.py`

Export `DryRunAIClient`.

## Data Flow (dry run)

```
Scrape sources (real, network)
  → merge cross-source duplicates (unchanged)
  → analyze with DryRunAIClient (instant, score=8.0 for all)
  → filter by threshold (all pass)
  → semantic dedup with DryRunAIClient (returns no duplicates)
  → balanced digest (unchanged)
  → enrich with DryRunAIClient (template background, no web search)
  → generate Markdown (unchanged)
  → save to data/summaries/horizon-{date}-{lang}.md
  → [SKIP] email
  → [SKIP] webhook
  → [SKIP] docs/_posts/ copy
```

## Out of Scope

- Offline/mock scraping (scrapers always hit real sources in dry run)
- Separate output path (dry run writes to the same path as normal runs)
- Config-file dry run flag (CLI only)
