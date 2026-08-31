# Write Safety

Load this reference for every mode that may change vault files.

## Establish Authority

1. Resolve the canonical configuration through `scripts/gark.py`; do not treat the current workspace as the vault.
2. Read the configured `schema_path` and relevant `00_System` documents before choosing metadata, routing, or lifecycle transitions.
3. When rules disagree, apply this precedence:
   - explicit user instruction for the current task;
   - `00_System/GARK_SCHEMA.json` for machine-enforced structure;
   - current `00_System` workflow and policy documents;
   - this skill's procedural defaults.
4. Ask before proceeding when an explicit request would violate an invariant or destroy user material.

## Preflight

- Inspect the target and its local links before editing.
- Search for the same source URL, canonical title, aliases, or substantially equivalent note.
- Prefer updating or linking an existing note when identity is clear. Do not merge merely similar ideas.
- Compute the smallest file set required by the selected mode.
- Preserve body text, formatting, and properties outside the requested scope.
- For broad or destructive operations, present a dry-run change list and wait for confirmation.

## Apply And Verify

- Make scoped, atomic edits. Never combine opportunistic cleanup with the requested operation.
- Validate changed notes against the canonical schema.
- Re-run the relevant search or audit check to confirm paths and links.
- Report created, updated, moved, or deleted files separately. State any ambiguity or pending review.
