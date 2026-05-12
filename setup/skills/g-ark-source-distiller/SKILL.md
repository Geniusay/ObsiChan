---
name: g-ark-source-distiller
description: Use this skill whenever the user provides an article, web page, book excerpt, paper, PDF, transcript, meeting notes, copied text, or any external material and asks to add it to an ObsiChan/G-Ark Obsidian vault. It creates a source note, distills reusable concepts/questions/models, updates relevant MOCs, and marks AI-generated notes for review. Use it for prompts like "整理这篇文章进 Obsidian", "把这个 PDF 放进知识库", "从这段内容提炼笔记", "生成 Zettelkasten 笔记", or "更新我的第二大脑".
---

# G-Ark Source Distiller

Use this skill to transform external material into structured ObsiChan/G-Ark Obsidian notes.

The goal is not to summarize everything. The goal is to preserve source traceability, extract reusable knowledge, and make the result easy for the user and future AI sessions to build on.

## First Files To Read

Before writing notes, read:

1. `00_System/AI_CONTEXT.md`
2. `00_System/SCHEMA.md`
3. `00_System/WORKFLOW.md`
4. `00_System/TAXONOMY.md`

If the user gives a topic, also read the most relevant `40_Maps/MOC - *.md`.

## Ingestion Workflow

For each source:

1. Identify the source type: article, book, paper, video, transcript, meeting, document, or unknown.
2. Create or update one source note in `20_Sources/`.
3. Write a concise source summary: what the source says, not what the user believes.
4. Extract 1-5 reusable notes into `30_Notes/` only when the ideas are worth future reuse.
5. Link every extracted note back to the source note.
6. Mark AI-generated extracted notes as `status: ai-draft`.
7. Update relevant MOCs in `40_Maps/`.
8. Add review items to `00_System/REVIEW.md` if human judgment is needed.

## Source Folder Policy

Route source notes by source form:

- `book` -> `20_Sources/Books`
- `article` -> `20_Sources/Articles`
- `paper` -> `20_Sources/Papers`
- `video` or `transcript` -> `20_Sources/Videos`
- `course` -> `20_Sources/Courses`
- `document` -> `20_Sources/Documents`
- `resource-list`, `collection`, `website-list`, learning resource roundup -> `20_Sources/Collections`

Do not create topic folders by default. A note about multi-armed bandits should not create `20_Sources/Reinforcement Learning`; it should go to the source-form folder and connect to `[[MOC - AI]]`, `[[MOC - 学习]]`, or a more specific MOC through links.

## Source Note Template

Use this shape for source notes:

```markdown
---
type: source
status: seed
created: YYYY-MM-DD
updated:
author:
source_url:
source_type:
topics: []
related: []
summary: ""
---

# Title

## 一句话摘要

## 核心观点

## 重要摘录

## 我的批注

## 可提炼笔记

## 相关链接
```

Use `status: raw` if the source has only been captured but not processed. Use `status: seed` after you have summarized it.

## Extracted Note Types

Create extracted notes only when they have standalone value.

- Concept -> `30_Notes/Concepts`
- Question -> `30_Notes/Questions`
- Model -> `30_Notes/Models`
- Claim -> `30_Notes/Claims`
- Person -> `30_Notes/People`
- Term -> `30_Notes/Terms`

Use this frontmatter pattern:

```yaml
---
type: concept
status: ai-draft
created: YYYY-MM-DD
updated:
topics: []
source: ["Source Note Title"]
related: []
confidence: medium
summary: ""
---
```

Adapt `type` and fields to the actual note type.

## Distillation Rules

- Keep source notes factual and attributable.
- Put personal interpretation in extracted notes, not in the source summary.
- Prefer one idea per extracted note.
- Do not create many tiny notes from a weak source.
- Do not create a note if a good note already exists. Update or link the existing note instead.
- Use `confidence: low` for speculative interpretations.
- Keep direct quotes short and cite the source note.

## MOC Updates

After extracting notes:

1. Find the closest existing MOC.
2. Add the source note under "来源笔记" when relevant.
3. Add extracted concept/question/model links under the right section.
4. If no MOC exists and the theme is important, ask before creating a new MOC unless the user requested automatic organization.

## Review Markers

Add a short checklist item to `00_System/REVIEW.md` when:

- A note is `status: ai-draft`
- A source lacks author, URL, or date
- A claim is uncertain
- There are multiple possible MOCs
- The material may need privacy or sensitivity review

## Final Response

Tell the user:

- Which source note was created or updated
- Which extracted notes were created
- Which MOCs were updated
- What needs user review
