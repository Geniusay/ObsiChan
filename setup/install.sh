#!/usr/bin/env bash
set -euo pipefail

VAULT_PATH="${VAULT_PATH:-$HOME/Documents/G-Ark}"
BRANCH="${BRANCH:-main}"
REPO_RAW_BASE="${REPO_RAW_BASE:-https://raw.githubusercontent.com/Geniusay/ObsiChan}"
CLAUDIAN_VERSION="${CLAUDIAN_VERSION:-2.0.11}"
CODEX_PATH="${CODEX_PATH:-}"

RAW_BASE="$REPO_RAW_BASE/$BRANCH"

info() {
  printf '[ObsiChan] %s\n' "$1"
}

write_file() {
  local path="$1"
  local dir
  dir="$(dirname "$path")"
  mkdir -p "$dir"
  cat > "$path"
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
  "$VAULT_PATH/20_Sources/Books" "$VAULT_PATH/20_Sources/Articles" "$VAULT_PATH/20_Sources/Papers" "$VAULT_PATH/20_Sources/Videos" "$VAULT_PATH/20_Sources/Courses" "$VAULT_PATH/20_Sources/Documents" \
  "$VAULT_PATH/30_Notes/Concepts" "$VAULT_PATH/30_Notes/Questions" "$VAULT_PATH/30_Notes/Models" "$VAULT_PATH/30_Notes/Claims" "$VAULT_PATH/30_Notes/People" "$VAULT_PATH/30_Notes/Terms" \
  "$VAULT_PATH/40_Maps" \
  "$VAULT_PATH/50_Projects/Active" "$VAULT_PATH/50_Projects/Waiting" "$VAULT_PATH/50_Projects/Completed" \
  "$VAULT_PATH/60_Areas" \
  "$VAULT_PATH/70_Outputs/Essays" "$VAULT_PATH/70_Outputs/Plans" "$VAULT_PATH/70_Outputs/Reports" "$VAULT_PATH/70_Outputs/Prompts" \
  "$VAULT_PATH/80_Assets/Images" "$VAULT_PATH/80_Assets/PDFs" "$VAULT_PATH/80_Assets/Audio" "$VAULT_PATH/80_Assets/Exports" \
  "$VAULT_PATH/_templates" \
  "$VAULT_PATH/.obsidian/plugins/claudian" \
  "$VAULT_PATH/.codex/skills"

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
# G-Ark Knowledge Base

## 快速入口

- [[AI_CONTEXT]]：AI 协作上下文
- [[SCHEMA]]：目录、元数据、命名规则
- [[WORKFLOW]]：日常使用流程
- [[REVIEW]]：定期整理清单
- [[TAXONOMY]]：主题、标签和类型表
- [[MOC - 个人知识库]]
- [[MOC - AI]]

## Vault-Level Codex Skills

- `g-ark-vault-steward`：整理、维护、复盘和扩展这个 Obsidian vault。
- `g-ark-source-distiller`：把文章、PDF、网页、摘录、会议记录等外部资料整理进知识库。

## 知识生命周期

10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs
EOF

write_file "$VAULT_PATH/00_System/AI_CONTEXT.md" <<'EOF'
# AI Context

## 知识库目标

这个 vault 用于构建一个适合个人思考、长期学习、项目推进和 AI 协作的第二大脑。

## AI 协作原则

- 优先读取 `00_System/Index.md`、`00_System/SCHEMA.md`、`00_System/WORKFLOW.md`。
- 如果任务涉及整理、维护、复盘或扩展本 vault，优先使用 `g-ark-vault-steward`。
- 如果任务涉及把外部资料整理进本 vault，优先使用 `g-ark-source-distiller`。
- AI 生成内容必须标记 `status: ai-draft`。
- 不要删除用户已有笔记，除非用户明确要求。
EOF

write_file "$VAULT_PATH/00_System/SCHEMA.md" <<'EOF'
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
EOF

write_file "$VAULT_PATH/00_System/WORKFLOW.md" <<'EOF'
# Workflow

10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs

AI 生成内容必须标记 `status: ai-draft` 并进入审核流程。
EOF

write_file "$VAULT_PATH/00_System/REVIEW.md" <<'EOF'
# Review

- [ ] 清理 `10_Inbox`
- [ ] 检查 `status: ai-draft` 的笔记
- [ ] 更新相关 MOC
EOF

write_file "$VAULT_PATH/00_System/TAXONOMY.md" <<'EOF'
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
# Prompts

请读取 `00_System/AI_CONTEXT.md` 和 `00_System/SCHEMA.md`，把我提供的资料整理进这个 Obsidian vault。
EOF

info "Writing starter notes"
printf '# Quick Capture\n\n## 临时想法\n\n- \n' > "$VAULT_PATH/10_Inbox/Quick Capture.md"
printf '# MOC - 个人知识库\n\n## 核心问题\n\n- 如何把资料转化为可复用的思想？\n' > "$VAULT_PATH/40_Maps/MOC - 个人知识库.md"
printf '# MOC - AI\n\n## 核心问题\n\n- AI 如何改变个人知识管理？\n' > "$VAULT_PATH/40_Maps/MOC - AI.md"
printf '# MOC - 学习\n\n## 核心问题\n\n- 什么样的学习会长期复利？\n' > "$VAULT_PATH/40_Maps/MOC - 学习.md"
printf '# MOC - 写作\n\n## 核心问题\n\n- 如何把笔记转化为文章？\n' > "$VAULT_PATH/40_Maps/MOC - 写作.md"
printf '# MOC - 项目\n\n## Active\n\n- \n' > "$VAULT_PATH/40_Maps/MOC - 项目.md"

for area in 学习 职业 健康 财务 创作; do
  printf '# %s\n\n## 维护标准\n\n- \n' "$area" > "$VAULT_PATH/60_Areas/$area.md"
done

write_file "$VAULT_PATH/_templates/source-template.md" <<'EOF'
---
type: source
status: raw
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

info "Downloading vault-level Codex skills"
for skill in g-ark-vault-steward g-ark-source-distiller; do
  mkdir -p "$VAULT_PATH/.codex/skills/$skill"
  download_file "$RAW_BASE/setup/skills/$skill/SKILL.md" "$VAULT_PATH/.codex/skills/$skill/SKILL.md"
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
      "installationMethodsByHost": {
        "$HOSTNAME_VALUE": "native-windows"
      },
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
