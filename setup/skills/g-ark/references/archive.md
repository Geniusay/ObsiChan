# Archive Mode

Use archive mode when the user wants supplied material filed as-is, with properties, and without newly generated document content.

## Workflow

1. Load [write-safety.md](write-safety.md), the canonical schema, and the system workflow for archive policy.
2. Inspect every supplied file completely. Determine whether it is already inside the configured vault.
3. Search for an existing note with the same source identity or equivalent content.
4. Resolve note type, required properties, and destination only from the canonical schema and current system policy.
5. Preserve the document body exactly. Add or normalize only the properties required for a valid archive, unless the user explicitly authorizes other edits.
6. Create or update one archived note per supplied document. Do not create extracted notes, summaries, MOCs, review pages, or other prose artifacts.
7. Validate the result and report each destination.

## Boundaries

- Missing information stays explicitly unknown according to the schema; never fabricate author, publication date, URL, or provenance.
- Existing frontmatter values are user data. Change them only when required for validity or explicitly requested.
- Do not interpret "archive" as "distill." Switch or add `distill` only when the user asks for synthesis or reusable notes.
