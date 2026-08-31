# Review Mode

Use review mode to turn pending AI material into an explicit human decision, not merely another checklist item.

## Workflow

1. Load [write-safety.md](write-safety.md), the canonical schema, and current review policy.
2. Identify pending items with the audit tool and confirm their actual state from the files.
3. Present a manageable batch. For each item, show:
   - note and location;
   - what AI created or changed;
   - provenance and supporting source;
   - uncertainty, conflict, or missing information;
   - the concrete decision available.
4. Accept explicit outcomes such as approve, revise, defer, merge, or reject only when supported by the current schema/workflow.
5. Change lifecycle or review properties only after the user's decision. Never infer approval from silence, retrieval, or casual mention.
6. Apply the smallest edit needed for the chosen outcome, validate it, and report unresolved items.

## Boundaries

- Do not promote content solely because it is old, linked, or frequently retrieved.
- Do not rewrite the user's view to make an AI draft easier to approve.
- Separate factual verification from preference approval; one does not imply the other.
- Never delete a rejected note unless the user explicitly authorizes deletion.
