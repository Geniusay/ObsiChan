# Retrieve Mode

Use retrieve mode to let relevant prior knowledge inform the current answer.

## When To Search

Search proactively when the task involves a substantive plan, decision, analysis, synthesis, or writing topic and the user's prior sources, models, preferences, or decisions could materially change the result. Always search when the user asks to use, search, or compare against the knowledge base.

Skip automatic search for simple facts, generic coding questions, small transactional tasks, or unrelated temporary matters. If current information is required, knowledge retrieval does not replace external research.

## Retrieval Workflow

1. Convert the request into a short search query using the user's key concepts and likely note titles. Do not add speculative jargon.
2. Run:

   `python <skill-root>/scripts/gark.py search <query> --limit <configured-limit> --json`

   Add `--expand-links` only when one-hop graph context could clarify a strong initial hit.
3. Inspect the returned title, path, type, summary, snippet, and score. Open only the most promising notes and enough linked context to interpret them safely.
4. Use only notes that materially support, constrain, contradict, or personalize the answer. A keyword hit alone is not evidence of relevance.
5. Separate:
   - what an external source says;
   - what the user's knowledge base already concludes;
   - what is newly inferred in this answer.
6. Cite every note actually used with its `[[Wikilink]]`; when useful outside Obsidian, also provide the resolved local file link.
7. Optionally record a lightweight local observation with `gark.py observe` when it will help evaluate retrieval quality. Use `--no-query` by default and store only the trigger, hit/use counts, and outcome. Include `--query` only when the text is non-sensitive and genuinely useful for tuning. Do not put telemetry into knowledge notes.

## Failure Behavior

- If results are absent or weak, answer from the appropriate general or current sources without forcing a knowledge-base angle.
- If the user explicitly requested vault grounding, say briefly that no relevant note was found.
- Never cite a search snippet without opening enough of the note to understand its context.
- Do not write or capture anything merely because retrieval occurred.
- Treat retrieve mode as read-only for vault content. Local telemetry is optional operational data, may be disabled, and must never contain secrets or sensitive conversation content.
