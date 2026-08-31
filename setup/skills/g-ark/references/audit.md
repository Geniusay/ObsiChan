# Audit Mode

Use audit mode to measure knowledge-base health before deciding whether to change it.

## Default: Read Only

Run:

`python <skill-root>/scripts/gark.py audit --json`

Use the canonical configuration and schema. Inspect files directly only to confirm or explain reported findings.

## Report

The CLI checks:

- required and type-specific fields, declared field types, lifecycle/status enums, and routes;
- unresolved links, orphaned long-lived notes, and MOC coverage;
- AI review state and provenance invariants;
- topic aliases or unknown topics;
- duplicate non-empty `source_url` values.

Prioritize findings that impair retrieval, trust, or future maintenance. For each material issue, include affected paths, impact, and the smallest corrective action. Distinguish deterministic violations from judgment calls. Inspect stale projects, output relationships, or semantic duplicates separately only when the user asks; the first-version CLI does not infer those judgments.

## Fixing Findings

Load [write-safety.md](write-safety.md) and switch from diagnosis to mutation only when the user asks to fix findings. Use a dry-run for migration or broad repair, keep the scope explicit, and re-run the audit after applying changes.

Do not create review documents, MOCs, taxonomy terms, or cleanup notes merely to describe the audit. Report results in the conversation unless the user explicitly asks for a vault artifact.
