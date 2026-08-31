# Capture Mode

Use capture mode for explicit save or remember requests, or to propose saving a durable conclusion discovered in conversation. This is a lightweight bridge, not a full autonomous memory system.

## Eligibility

Good candidates are stable user decisions, durable preferences, verified conclusions, reusable models, or meaningful project state. Do not capture routine chat, temporary emotion, secrets, credentials, private data unnecessary to the knowledge goal, copied material without provenance, or unverified speculation.

## Workflow

1. Load [write-safety.md](write-safety.md), then read capture policy from the canonical configuration and schema.
2. Reduce the candidate to one durable idea. Keep the user's wording when it carries intent.
3. Search for an existing note that already contains the idea.
4. If an existing note is clearly the same knowledge object, propose or make the smallest authorized update. Otherwise use the capture CLI for an AI-authored or AI-reformulated candidate:

   `python <skill-root>/scripts/gark.py capture --title <title> --content <content> --source-session <session-id> --json`

   This is a dry run by default. Inspect the proposed target and metadata before any write.
5. Apply only when the user explicitly requested saving or the configured capture policy authorizes this exact case. `--apply` requires a stable `--source-session` value and refuses a second AI candidate from the same session.
6. Keep AI authorship, conversation provenance, and review state visible as defined by the schema.
7. Tell the user what was saved and where. If only a suggestion was warranted, ask once without creating a file.

## Guardrails

- Obey the configured per-session capture limit.
- Treat the capture CLI as an AI-candidate writer. When the user asks to preserve supplied wording verbatim, use the schema-valid Inbox/archive path instead, do not rewrite it, and do not set `ai_generated: true` merely because AI performed the file operation.
- Prefer a reviewable capture target over silently editing mature knowledge.
- Do not create a new formal note, MOC, or taxonomy term unless the request requires it.
- Never treat captured conversation as verified evidence. Link supporting sources separately.
