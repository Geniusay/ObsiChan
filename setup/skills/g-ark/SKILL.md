---
name: g-ark
description: Operate and consult the user's G-Ark Obsidian knowledge base through one routed interface. Use for archiving or distilling sources; summarizing and preserving useful AI-session conclusions; searching or citing prior notes; capturing durable conclusions; connecting notes and MOCs; reviewing AI drafts; auditing or maintaining the vault. Also invoke proactively for substantive planning, analysis, writing, or decision questions when prior knowledge may materially improve the answer. Do not invoke merely for simple facts, generic coding help, or unrelated transient tasks.
---

# G-Ark

Use G-Ark as personal knowledge context, not merely as storage. Read proactively but conservatively; write deliberately and visibly.

## Initialize

1. Locate this skill's directory and use `scripts/gark.py` from it. Let the CLI load the canonical `.gark/config.toml`; never infer the vault from the current working directory.
2. For any write, migration, or validation, resolve `vault_root` and `schema_path` from that configuration, then read the canonical schema and the relevant documents under `00_System/`.
3. Treat `00_System/GARK_SCHEMA.json` as the machine-readable source of truth. System documents explain it. This skill defines procedure only and must not invent metadata values, folders, or migrations.
4. If configuration or schema cannot be resolved, stop before writing and report the missing dependency. Retrieval may fall back only when the configured vault root is known.

## Route

Choose the smallest mode that satisfies the request. Combine modes only when the user asks for multiple outcomes.

| Mode | Use for | Load |
| --- | --- | --- |
| `archive` | Preserve supplied material and add only required properties | [archive.md](references/archive.md) |
| `distill` | Turn a source into traceable, reusable knowledge | [distill.md](references/distill.md) |
| `session` | Produce a focused summary from an AI conversation or transcript, then optionally save it after review | [session.md](references/session.md) |
| `retrieve` | Search prior knowledge and use relevant notes in an answer | [retrieve.md](references/retrieve.md) |
| `capture` | Save a durable conclusion or explicit memory request | [capture.md](references/capture.md) |
| `connect` | Add high-signal links or maintain a MOC | [connect.md](references/connect.md) |
| `review` | Let the user inspect and confirm AI-authored knowledge | [review.md](references/review.md) |
| `audit` | Diagnose schema, link, duplicate, taxonomy, or coverage issues | [audit.md](references/audit.md) |

For any mode that changes files, also load [write-safety.md](references/write-safety.md).

## Global Behavior

- Search before creating or materially updating a note.
- Preserve user-authored text and unrelated changes. Never delete, overwrite, move, merge, or promote notes without authorization appropriate to that operation.
- Keep environment details private. Do not expose configuration contents, credentials, usernames, machine-specific absolute paths, or runtime data in generated notes, telemetry, or user-facing reports. Prefer vault-relative paths when reporting changes.
- Distinguish source claims, the user's established views, and new AI inference. Do not present one as another.
- Use knowledge-base material only when it materially improves the answer. Weak or irrelevant results are permission to answer without it.
- A vault search is not current web research. Use current external sources when freshness is required, and label the distinction.
- Do not silently turn ordinary conversation, temporary emotion, secrets, or unverified speculation into memory.
- After a write, report exactly what changed and what still needs human judgment. After retrieval, cite the notes actually used.
