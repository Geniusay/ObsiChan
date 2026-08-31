# Session Mode

Use session mode when the user wants the useful substance of an AI conversation, IDE chat, debugging discussion, design review, implementation explanation, or pasted transcript summarized or preserved. Produce a focused content summary, not a chronological chat recap or a collection of small knowledge cards.

Use `distill` instead when a supplied transcript is being treated as an external source and the user wants source traceability plus reusable extracted notes.

## Scope And Default Interaction

Honor an explicit source scope or save mode. Otherwise use:

- source scope: the assistant's most recent substantive answer;
- save mode: review before writing.

Use the full visible session only when the user asks for it. If the requested conversation is unavailable, ask for the narrowest missing transcript. A request for a summary without preservation is summary-only and does not require vault access.

In review mode:

1. Generate and show the focused summary without frontmatter or vault edits.
2. Wait for an explicit decision to save, revise then save, keep summary-only, or cancel.
3. Apply requested edits before saving. Silence or a new unrelated request is not approval.

Write directly only when the user explicitly requests direct saving and the result is high-confidence, low-risk, and permitted by current capture policy.

## Summary Method

1. Identify the question, decision, problem, or design concern that drove the exchange.
2. Preserve final conclusions, material reasoning, tradeoffs, user corrections, and relevant open actions.
3. Remove tool logs, progress updates, repeated context, polite filler, and failed attempts that do not affect the conclusion.
4. Use one content-specific H1 followed by content-specific H2 sections. Avoid headings or wrapper phrases that describe the chat container, such as "session summary" or "the discussion above."
5. Keep source claims, user decisions, and new inference distinguishable. Do not turn uncertain discussion into established knowledge.

The summary should be understandable later without rereading the conversation, while remaining concise enough to review reliably.

## Saving

After explicit approval, load [write-safety.md](write-safety.md), the canonical schema, and current capture policy. Search for an equivalent note before creating anything.

Use the capture CLI for an AI-authored or AI-reformulated candidate:

`python <skill-root>/scripts/gark.py capture --title <title> --content <approved-summary> --source-session <opaque-session-id> --json`

Inspect the dry-run result before adding `--apply`. Use a stable opaque session identifier that contains no transcript text, username, local path, credential, or other environment detail. Preserve AI authorship, conversation provenance, and review state exactly as the schema requires.

Do not save secrets, credentials, unnecessary private data, machine-specific paths, configuration contents, or operational logs. Report the saved note by title and vault-relative path only.

## Output

Before approval, return the summary and the available decision in natural language. After saving, report the source scope, mode, note title, vault-relative path, and any remaining human review. Do not expose frontmatter internals or environment configuration unless the user explicitly asks for them.
