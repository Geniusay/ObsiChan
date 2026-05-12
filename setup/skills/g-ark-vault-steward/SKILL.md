---
name: g-ark-vault-steward
description: Use this skill whenever the user asks Codex to organize, maintain, refactor, review, or extend an ObsiChan/G-Ark Obsidian vault. This includes routing notes to folders, updating MOCs, cleaning Inbox, creating project/area/output notes, applying the vault schema, checking AI-generated drafts, and keeping the vault usable for both the user and AI. Use it even if the user only says "整理我的知识库", "更新 MOC", "清理 Inbox", "帮我管理 Obsidian", or mentions ObsiChan/G-Ark.
---

# G-Ark Vault Steward

You are maintaining an ObsiChan/G-Ark Obsidian vault. Treat the vault as a living personal knowledge system, not a pile of Markdown files.

## First Files To Read

Before making structural changes, read these files when they exist:

1. `00_System/AI_CONTEXT.md`
2. `00_System/SCHEMA.md`
3. `00_System/WORKFLOW.md`
4. `00_System/TAXONOMY.md`
5. Relevant `40_Maps/MOC - *.md` files

Use those files as the source of truth for folder purpose, note types, status values, and AI collaboration rules.

## Core Model

ObsiChan currently uses the lightweight structure:

```text
00_System   system rules, AI context, workflow, taxonomy
10_Inbox    quick capture and unprocessed material
20_Sources  source notes about external material
30_Notes    the user's concepts, questions, models, claims, people, terms
40_Maps     MOCs and navigational maps
50_Projects active/waiting/completed project notes
60_Areas    long-term responsibility areas
70_Outputs  essays, plans, reports, prompts, reusable outputs
80_Assets   attachments and media files
_templates  note templates
```

Do not introduce `20_Raw`, `40_Wiki`, or `90_Archive` unless the user explicitly asks or the existing system files are updated to include them.

## Routing Rules

Use this routing decision tree:

- Temporary thought, pasted fragment, or unclear item -> `10_Inbox`
- Summary of an external article, book, paper, video, document, meeting, transcript -> `20_Sources`
- Curated resource list, website list, learning resource roundup, or `source_type: resource-list` -> `20_Sources/Collections`
- One reusable idea in the user's own words -> `30_Notes/Concepts`
- Open research question -> `30_Notes/Questions`
- Framework, method, or thinking model -> `30_Notes/Models`
- Explicit judgment or thesis -> `30_Notes/Claims`
- Topic navigation page -> `40_Maps`
- Work with a concrete outcome -> `50_Projects/Active`, `Waiting`, or `Completed`
- Long-running responsibility without a deadline -> `60_Areas`
- Publishable or reusable artifact -> `70_Outputs`
- PDF, image, audio, export, screenshot -> `80_Assets`

When uncertain, put the content in `10_Inbox` and add a short reason.

## Source Folder Policy

`20_Sources` is organized by source form, not by topic. Use `topics`, `related`, and MOCs for thematic navigation.

Use these stable folders:

- `Books` for books
- `Articles` for articles and blog posts
- `Papers` for academic papers
- `Videos` for videos and transcripts
- `Courses` for courses
- `Documents` for general documents
- `Collections` for resource lists, website lists, curated link collections, and learning material roundups

Do not create a new folder for every topic such as `Reinforcement Learning` or `Frontend Design` unless the user explicitly asks. Topic folders fragment the vault quickly; MOCs are better for topic navigation.

## Editing Principles

- Preserve user-created content. Do not delete or overwrite notes unless the user explicitly asks.
- Keep source notes and personal notes separate.
- Use Obsidian wikilinks, for example `[[MOC - AI]]`.
- Use Chinese as the default language unless the note itself is clearly in another language.
- Keep notes concise and useful. Remove empty scaffolding only when it is clearly noise.
- When creating AI-generated notes, set `status: ai-draft`.
- When the user confirms or edits a draft, change status to `seed` or `evergreen`.
- Add `source`, `topics`, `related`, and `summary` fields when useful.

## MOC Maintenance

MOCs are not folders. They are topic maps.

When updating a MOC:

1. Add only links that are clearly relevant.
2. Group links by question, concept, source, project, or output.
3. Prefer fewer high-signal links over long lists.
4. Remove broken links if the target note no longer exists.
5. Do not duplicate entire note contents inside the MOC.

## Review Workflow

When asked to review or clean the vault:

1. Inspect `10_Inbox`.
2. Find `status: ai-draft` notes.
3. Check for broken wikilinks.
4. Check active projects for missing `next_action`.
5. Update `00_System/REVIEW.md` with concrete checklist items.
6. Summarize what changed and what still needs human judgment.

## Output To User

After changes, report:

- Files created
- Files updated
- Files moved or deleted
- Any notes requiring user review
- Any follow-up setup needed in Obsidian or Claudian
