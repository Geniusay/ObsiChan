#!/usr/bin/env bash
set -euo pipefail

VAULT_PATH="${VAULT_PATH:-$HOME/Documents/G-Ark}"
BRANCH="${BRANCH:-main}"
REPO_RAW_BASE="${REPO_RAW_BASE:-https://raw.githubusercontent.com/Geniusay/ObsiChan}"
CLAUDIAN_VERSION="${CLAUDIAN_VERSION:-2.0.11}"
CODEX_PATH="${CODEX_PATH:-}"
INSTALL_DATE="$(date +%F)"

RAW_BASE="$REPO_RAW_BASE/$BRANCH"

info() {
  printf '[ObsiChan] %s\n' "$1"
}

write_file() {
  local path="$1"
  local dir
  dir="$(dirname "$path")"
  mkdir -p "$dir"
  sed "s/__OBSI_INSTALL_DATE__/$INSTALL_DATE/g" > "$path"
}

download_file() {
  local url="$1"
  local out="$2"
  mkdir -p "$(dirname "$out")"
  curl -fsSL "$url" -o "$out"
}

resolve_codex_path() {
  if [ -n "$CODEX_PATH" ] && [ -x "$CODEX_PATH" ]; then
    printf '%s\n' "$CODEX_PATH"
    return 0
  fi
  if command -v codex >/dev/null 2>&1; then
    command -v codex
    return 0
  fi
  for candidate in "/opt/homebrew/bin/codex" "/usr/local/bin/codex" "$HOME/.npm-global/bin/codex" "$HOME/.local/bin/codex"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

case "$VAULT_PATH" in
  "~") VAULT_PATH="$HOME" ;;
  "~/"*) VAULT_PATH="$HOME/${VAULT_PATH#~/}" ;;
esac
mkdir -p "$VAULT_PATH"
VAULT_PATH="$(cd "$VAULT_PATH" && pwd -P)"
info "Creating vault at $VAULT_PATH"

mkdir -p \
  "$VAULT_PATH/00_System" \
  "$VAULT_PATH/10_Inbox" \
  "$VAULT_PATH/20_Sources/Books" "$VAULT_PATH/20_Sources/Articles" "$VAULT_PATH/20_Sources/Papers" "$VAULT_PATH/20_Sources/Videos" "$VAULT_PATH/20_Sources/Courses" "$VAULT_PATH/20_Sources/Documents" "$VAULT_PATH/20_Sources/Collections" \
  "$VAULT_PATH/30_Notes/Concepts" "$VAULT_PATH/30_Notes/Questions" "$VAULT_PATH/30_Notes/Models" "$VAULT_PATH/30_Notes/Claims" "$VAULT_PATH/30_Notes/People" "$VAULT_PATH/30_Notes/Terms" \
  "$VAULT_PATH/40_Maps" \
  "$VAULT_PATH/50_Projects/Active" "$VAULT_PATH/50_Projects/Waiting" "$VAULT_PATH/50_Projects/Completed" \
  "$VAULT_PATH/60_Areas" \
  "$VAULT_PATH/70_Outputs/Essays" "$VAULT_PATH/70_Outputs/Plans" "$VAULT_PATH/70_Outputs/Reports" "$VAULT_PATH/70_Outputs/Prompts" \
  "$VAULT_PATH/80_Assets/Images" "$VAULT_PATH/80_Assets/PDFs" "$VAULT_PATH/80_Assets/Audio" "$VAULT_PATH/80_Assets/Exports" \
  "$VAULT_PATH/_templates" \
  "$VAULT_PATH/.obsidian/plugins/claudian" \
  "$VAULT_PATH/.codex/skills" \
  "$VAULT_PATH/.gark/skill"

info "Writing Obsidian config"
write_file "$VAULT_PATH/.obsidian/app.json" <<'EOF'
{
  "promptDelete": false,
  "newFileLocation": "folder",
  "newFileFolderPath": "10_Inbox",
  "attachmentFolderPath": "80_Assets"
}
EOF

write_file "$VAULT_PATH/.obsidian/templates.json" <<'EOF'
{
  "folder": "_templates",
  "dateFormat": "YYYY-MM-DD",
  "timeFormat": "HH:mm"
}
EOF

write_file "$VAULT_PATH/.obsidian/core-plugins.json" <<'EOF'
[
  "file-explorer",
  "global-search",
  "switcher",
  "graph",
  "backlink",
  "outgoing-link",
  "tag-pane",
  "page-preview",
  "daily-notes",
  "templates",
  "note-composer",
  "command-palette",
  "slash-command",
  "properties",
  "canvas",
  "bases"
]
EOF

write_file "$VAULT_PATH/.obsidian/community-plugins.json" <<'EOF'
[
  "claudian"
]
EOF

info "Writing system notes"
write_file "$VAULT_PATH/00_System/Index.md" <<'EOF'
---
type: system
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "G-Ark 知识库系统入口"
---

# G-Ark Knowledge Base

## 快速入口

- [[AI_CONTEXT]]：AI 协作上下文
- [[SCHEMA]]：目录、元数据、命名规则
- [[WORKFLOW]]：日常使用流程
- [[REVIEW]]：定期整理清单
- [[TAXONOMY]]：主题、标签和类型表
- [[MOC - 个人知识库]]
- [[MOC - AI]]

## Codex Skill

- `g-ark`：统一负责检索、引用、归档、提炼、会话沉淀、关联、审阅和维护。

## 知识生命周期

10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs
EOF

write_file "$VAULT_PATH/00_System/AI_CONTEXT.md" <<'EOF'
---
type: system
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "AI 访问和维护知识库时的协作边界"
---

# AI Context

## 知识库目标

这个 vault 用于构建一个适合个人思考、长期学习、项目推进和 AI 协作的第二大脑。

## AI 协作原则

- 优先读取 `00_System/Index.md`、`00_System/SCHEMA.md`、`00_System/WORKFLOW.md`。
- 涉及本 vault 的检索、归档、提炼、会话沉淀、维护或审阅时，统一使用 `g-ark`。
- AI 生成内容必须按 `GARK_SCHEMA.json` 标记来源和审核状态。
- 不要删除用户已有笔记，除非用户明确要求。
- 不在笔记或反馈中暴露配置内容、凭据、用户名、机器绝对路径或运行数据。
EOF

write_file "$VAULT_PATH/00_System/SCHEMA.md" <<'EOF'
---
type: system
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "GARK_SCHEMA.json 的人类可读说明"
---

# Schema

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `00_System` | 知识库操作系统 |
| `10_Inbox` | 临时捕获 |
| `20_Sources` | 来源笔记 |
| `30_Notes` | 个人知识资产 |
| `40_Maps` | 内容地图 |
| `50_Projects` | 当前行动 |
| `60_Areas` | 长期责任区 |
| `70_Outputs` | 产出物 |
| `80_Assets` | 附件资源 |
| `_templates` | 模板 |

## 来源笔记子目录规则

`20_Sources` 优先按来源形态归档，而不是按主题归档。主题关系使用 `topics`、`related` 和 `40_Maps` 表达。

| source_type | 推荐位置 |
| --- | --- |
| `book` | `20_Sources/Books` |
| `article` | `20_Sources/Articles` |
| `paper` | `20_Sources/Papers` |
| `video` | `20_Sources/Videos` |
| `course` | `20_Sources/Courses` |
| `document` | `20_Sources/Documents` |
| `resource-list` / `collection` / `website-list` | `20_Sources/Collections` |

不要为每个主题随意创建新文件夹；主题导航交给 MOC 和链接。
EOF

write_file "$VAULT_PATH/00_System/WORKFLOW.md" <<'EOF'
---
type: system
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "知识捕获、提炼、连接和审核流程"
---

# Workflow

10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs

AI 生成内容必须按 `GARK_SCHEMA.json` 标记 `ai_generated` 与 `review_status` 并进入审核流程。
EOF

write_file "$VAULT_PATH/00_System/REVIEW.md" <<'EOF'
---
type: review
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "需要人工判断的知识库审核入口"
---

# Review

- [ ] 清理 `10_Inbox`
- [ ] 检查 `review_status: pending` 的 AI 生成笔记
- [ ] 更新相关 MOC
EOF

write_file "$VAULT_PATH/00_System/TAXONOMY.md" <<'EOF'
---
type: system
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "知识库稳定主题及别名说明"
---

# Taxonomy

- AI
- 个人知识管理
- 第二大脑
- Obsidian
- 写作
- 学习
- 项目管理
EOF

write_file "$VAULT_PATH/00_System/PROMPTS.md" <<'EOF'
---
type: system
status: active
review_status: not-required
created: __OBSI_INSTALL_DATE__
topics: []
summary: "调用统一 G-Ark skill 的常用请求"
---

# Prompts

请读取 `00_System/AI_CONTEXT.md` 和 `00_System/SCHEMA.md`，把我提供的资料整理进这个 Obsidian vault。
EOF

info "Writing starter notes"
printf '%s\n' '---' 'type: inbox' 'status: inbox' 'review_status: not-required' "created: $INSTALL_DATE" 'topics: []' 'summary: "临时捕获入口"' '---' '' '# Quick Capture' '' '## 临时想法' '' '- ' > "$VAULT_PATH/10_Inbox/Quick Capture.md"
for moc in 个人知识库 AI 学习 写作 项目; do
  printf '%s\n' '---' 'type: moc' 'status: active' 'review_status: not-required' "created: $INSTALL_DATE" 'topics: []' "summary: \"$moc 主题导航\"" '---' '' "# MOC - $moc" '' '## 核心问题' '' '- ' > "$VAULT_PATH/40_Maps/MOC - $moc.md"
done

for area in 学习 职业 健康 财务 创作; do
  printf '%s\n' '---' 'type: area' 'status: active' 'review_status: not-required' "created: $INSTALL_DATE" 'topics: []' "summary: \"$area 长期责任区\"" 'standard: ""' 'review_cycle: monthly' '---' '' "# $area" '' '## 维护标准' '' '- ' > "$VAULT_PATH/60_Areas/$area.md"
done

write_file "$VAULT_PATH/_templates/source-template.md" <<'EOF'
---
type: source
status: raw
review_status: not-required
created: {{date}}
updated:
author:
source_url:
source_type:
topics: []
related: []
summary: ""
---

# {{title}}

## 一句话摘要

## 核心观点

## 重要摘录

## 我的批注

## 可提炼笔记

## 相关链接
EOF

write_file "$VAULT_PATH/_templates/concept-template.md" <<'EOF'
---
type: concept
status: seed
review_status: not-required
created: {{date}}
updated:
topics: []
source: []
related: []
confidence: medium
summary: ""
---

# {{title}}

## 定义

## 我的理解

## 相关链接
EOF

info "Downloading Claudian $CLAUDIAN_VERSION"
CLAUDIAN_BASE="https://github.com/YishenTu/claudian/releases/download/$CLAUDIAN_VERSION"
download_file "$CLAUDIAN_BASE/main.js" "$VAULT_PATH/.obsidian/plugins/claudian/main.js"
download_file "$CLAUDIAN_BASE/manifest.json" "$VAULT_PATH/.obsidian/plugins/claudian/manifest.json"
download_file "$CLAUDIAN_BASE/styles.css" "$VAULT_PATH/.obsidian/plugins/claudian/styles.css"

info "Downloading the unified G-Ark Codex skill"
GARK_ROOT="$VAULT_PATH/.gark"
SKILL_ROOT="$GARK_ROOT/skill"
SKILL_FILES=(
  "SKILL.md"
  "agents/openai.yaml"
  "references/archive.md"
  "references/audit.md"
  "references/capture.md"
  "references/connect.md"
  "references/distill.md"
  "references/retrieve.md"
  "references/review.md"
  "references/session.md"
  "references/write-safety.md"
  "scripts/gark.py"
  "scripts/install-global.ps1"
)
for relative_path in "${SKILL_FILES[@]}"; do
  download_file "$RAW_BASE/setup/skills/g-ark/$relative_path" "$SKILL_ROOT/$relative_path"
done

if [ ! -f "$GARK_ROOT/config.toml" ]; then
  download_file "$RAW_BASE/setup/gark/config.toml" "$GARK_ROOT/config.toml"
fi
download_file "$RAW_BASE/setup/gark/GARK_SCHEMA.json" "$VAULT_PATH/00_System/GARK_SCHEMA.json"

SKILL_LINK="$VAULT_PATH/.codex/skills/g-ark"
if [ ! -e "$SKILL_LINK" ] && [ ! -L "$SKILL_LINK" ]; then
  ln -s ../../.gark/skill "$SKILL_LINK"
elif [ ! -L "$SKILL_LINK" ]; then
  printf 'Cannot enable g-ark because a non-link path already exists: %s\n' "$SKILL_LINK" >&2
  exit 1
else
  ln -sfn ../../.gark/skill "$SKILL_LINK"
fi

LEGACY_ROOT="$GARK_ROOT/legacy-skills"
for legacy_name in g-ark-vault-steward g-ark-source-distiller g-ark-session-distiller; do
  legacy_path="$VAULT_PATH/.codex/skills/$legacy_name"
  if [ -e "$legacy_path" ] || [ -L "$legacy_path" ]; then
    mkdir -p "$LEGACY_ROOT"
    backup_path="$LEGACY_ROOT/$legacy_name"
    if [ -e "$backup_path" ] || [ -L "$backup_path" ]; then
      printf 'Legacy backup already exists; leaving %s unchanged.\n' "$legacy_name" >&2
    else
      mv "$legacy_path" "$backup_path"
      info "Disabled legacy skill $legacy_name and preserved it under .gark/legacy-skills"
    fi
  fi
done

if CODEX_RESOLVED="$(resolve_codex_path)"; then
  HOSTNAME_VALUE="$(hostname)"
  info "Writing Claudian Codex provider config for $CODEX_RESOLVED"
  mkdir -p "$VAULT_PATH/.claudian"
  cat > "$VAULT_PATH/.claudian/claudian-settings.json" <<EOF
{
  "model": "gpt-5.5",
  "enableAutoTitleGeneration": false,
  "providerConfigs": {
    "codex": {
      "enabled": true,
      "safeMode": "workspace-write",
      "cliPath": "",
      "cliPathsByHost": {
        "$HOSTNAME_VALUE": "$CODEX_RESOLVED"
      },
      "customModels": "gpt-5.5",
      "reasoningSummary": "detailed",
      "environmentVariables": "",
      "environmentHash": "",
      "wslDistroOverridesByHost": {}
    }
  },
  "settingsProvider": "codex",
  "savedProviderModel": {
    "codex": "gpt-5.5"
  },
  "savedProviderEffort": {
    "codex": "high"
  },
  "savedProviderPermissionMode": {
    "codex": "yolo"
  }
}
EOF
else
  info "Codex CLI was not found. Install it and set the path in Claudian settings."
fi

info "Done. Open Obsidian -> Open folder as vault -> $VAULT_PATH"
