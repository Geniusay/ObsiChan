param(
  [string]$VaultPath = "$HOME\Documents\G-Ark",
  [string]$Branch = "main",
  [string]$RepoRawBase = "https://raw.githubusercontent.com/Geniusay/ObsiChan",
  [string]$ClaudianVersion = "2.0.11",
  [string]$CodexPath = ""
)

$ErrorActionPreference = "Stop"

function Write-Info {
  param([string]$Message)
  Write-Host "[ObsiChan] $Message"
}

function Write-TextFile {
  param(
    [string]$Path,
    [string]$Content
  )
  $dir = Split-Path -Parent $Path
  if ($dir) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
  }
  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Download-File {
  param(
    [string]$Url,
    [string]$OutFile
  )
  $dir = Split-Path -Parent $OutFile
  if ($dir) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
  }
  Invoke-WebRequest -Uri $Url -OutFile $OutFile -Headers @{ "User-Agent" = "ObsiChan-Installer" }
}

function Resolve-CodexPath {
  if ($CodexPath -and (Test-Path -LiteralPath $CodexPath)) {
    return $CodexPath
  }

  $cmd = Get-Command codex -ErrorAction SilentlyContinue
  if ($cmd) {
    return $cmd.Source
  }

  $candidates = @(
    "$HOME\AppData\Local\OpenAI\Codex\bin\codex.exe",
    "$HOME\AppData\Roaming\npm\codex.cmd"
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }
  return ""
}

$VaultPath = [System.IO.Path]::GetFullPath($VaultPath)
$RawBase = "$RepoRawBase/$Branch"

Write-Info "Creating vault at $VaultPath"

$dirs = @(
  "00_System",
  "10_Inbox",
  "20_Sources\Books","20_Sources\Articles","20_Sources\Papers","20_Sources\Videos","20_Sources\Courses","20_Sources\Documents",
  "30_Notes\Concepts","30_Notes\Questions","30_Notes\Models","30_Notes\Claims","30_Notes\People","30_Notes\Terms",
  "40_Maps",
  "50_Projects\Active","50_Projects\Waiting","50_Projects\Completed",
  "60_Areas",
  "70_Outputs\Essays","70_Outputs\Plans","70_Outputs\Reports","70_Outputs\Prompts",
  "80_Assets\Images","80_Assets\PDFs","80_Assets\Audio","80_Assets\Exports",
  "_templates",
  ".obsidian",
  ".obsidian\plugins\claudian",
  ".codex\skills"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Path (Join-Path $VaultPath $dir) -Force | Out-Null
}

Write-Info "Writing Obsidian config"
Write-TextFile -Path (Join-Path $VaultPath ".obsidian\app.json") -Content @'
{
  "promptDelete": false,
  "newFileLocation": "folder",
  "newFileFolderPath": "10_Inbox",
  "attachmentFolderPath": "80_Assets"
}
'@

Write-TextFile -Path (Join-Path $VaultPath ".obsidian\templates.json") -Content @'
{
  "folder": "_templates",
  "dateFormat": "YYYY-MM-DD",
  "timeFormat": "HH:mm"
}
'@

Write-TextFile -Path (Join-Path $VaultPath ".obsidian\core-plugins.json") -Content @'
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
'@

Write-TextFile -Path (Join-Path $VaultPath ".obsidian\community-plugins.json") -Content @'
[
  "claudian"
]
'@

Write-Info "Writing system notes"
Write-TextFile -Path (Join-Path $VaultPath "00_System\Index.md") -Content @'
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
'@

Write-TextFile -Path (Join-Path $VaultPath "00_System\AI_CONTEXT.md") -Content @'
# AI Context

## 知识库目标

这个 vault 用于构建一个适合个人思考、长期学习、项目推进和 AI 协作的第二大脑。

## AI 协作原则

- 优先读取 `00_System/Index.md`、`00_System/SCHEMA.md`、`00_System/WORKFLOW.md`。
- 如果任务涉及整理、维护、复盘或扩展本 vault，优先使用 `g-ark-vault-steward`。
- 如果任务涉及把外部资料整理进本 vault，优先使用 `g-ark-source-distiller`。
- AI 生成内容必须标记 `status: ai-draft`。
- 不要删除用户已有笔记，除非用户明确要求。

## 用户偏好

- 使用中文作为主要笔记语言。
- 保留 Obsidian wikilinks，例如 `[[MOC - AI]]`。
- 内容应该面向未来检索、复用和 AI 协作。
'@

Write-TextFile -Path (Join-Path $VaultPath "00_System\SCHEMA.md") -Content @'
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

## 状态约定

- `inbox`：尚未整理
- `raw`：来源内容尚未提炼
- `ai-draft`：AI 生成或整理，等待用户确认
- `seed`：初步形成
- `evergreen`：已稳定
- `active`：正在推进
- `waiting`：等待外部条件
- `completed`：已完成
'@

Write-TextFile -Path (Join-Path $VaultPath "00_System\WORKFLOW.md") -Content @'
# Workflow

## 每日捕获

临时想法、网页片段、待读资料先放入 `10_Inbox`。

## 每周整理

处理 `10_Inbox`：

1. 外部资料整理到 `20_Sources`。
2. 自己的想法整理到 `30_Notes`。
3. 可执行事项关联到 `50_Projects`。
4. 长期责任关联到 `60_Areas`。
5. 可发布内容移动到 `70_Outputs`。

## AI 协作流程

AI 整理资料时，应创建来源笔记、提炼 1-5 篇长期笔记、标记 `status: ai-draft`，并更新相关 MOC。
'@

Write-TextFile -Path (Join-Path $VaultPath "00_System\REVIEW.md") -Content @'
# Review

## Inbox 清理

- [ ] 清理 `10_Inbox`
- [ ] 把外部资料整理到 `20_Sources`
- [ ] 把个人想法整理到 `30_Notes`

## AI 草稿审核

- [ ] 检查 `status: ai-draft` 的笔记是否准确
- [ ] 为 AI 生成笔记补充来源链接
- [ ] 把确认后的笔记改为 `status: seed` 或 `status: evergreen`
'@

Write-TextFile -Path (Join-Path $VaultPath "00_System\TAXONOMY.md") -Content @'
# Taxonomy

## 初始主题

- AI
- 个人知识管理
- 第二大脑
- Obsidian
- 写作
- 学习
- 项目管理
- 产品
- 职业
- 健康
- 财务
- 创作
'@

Write-TextFile -Path (Join-Path $VaultPath "00_System\PROMPTS.md") -Content @'
# Prompts

## 整理一篇资料

请读取 `00_System/AI_CONTEXT.md` 和 `00_System/SCHEMA.md`，把我提供的资料整理进这个 Obsidian vault。
'@

Write-Info "Writing starter MOCs, templates, and areas"
Write-TextFile -Path (Join-Path $VaultPath "10_Inbox\Quick Capture.md") -Content "# Quick Capture`n`n## 临时想法`n`n- "
Write-TextFile -Path (Join-Path $VaultPath "40_Maps\MOC - 个人知识库.md") -Content "# MOC - 个人知识库`n`n## 核心问题`n`n- 如何把资料转化为可复用的思想？`n- 如何让知识库同时适合人和 AI 使用？"
Write-TextFile -Path (Join-Path $VaultPath "40_Maps\MOC - AI.md") -Content "# MOC - AI`n`n## 核心问题`n`n- AI 如何改变个人知识管理？"
Write-TextFile -Path (Join-Path $VaultPath "40_Maps\MOC - 学习.md") -Content "# MOC - 学习`n`n## 核心问题`n`n- 什么样的学习会长期复利？"
Write-TextFile -Path (Join-Path $VaultPath "40_Maps\MOC - 写作.md") -Content "# MOC - 写作`n`n## 核心问题`n`n- 如何把笔记转化为文章？"
Write-TextFile -Path (Join-Path $VaultPath "40_Maps\MOC - 项目.md") -Content "# MOC - 项目`n`n## Active`n`n- "

foreach ($area in @("学习","职业","健康","财务","创作")) {
  Write-TextFile -Path (Join-Path $VaultPath "60_Areas\$area.md") -Content "# $area`n`n## 维护标准`n`n- "
}

Write-TextFile -Path (Join-Path $VaultPath "_templates\source-template.md") -Content @'
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
'@

Write-TextFile -Path (Join-Path $VaultPath "_templates\concept-template.md") -Content @'
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

## 例子

## 边界和误区

## 相关链接
'@

Write-Info "Downloading Claudian $ClaudianVersion"
$pluginDir = Join-Path $VaultPath ".obsidian\plugins\claudian"
$claudianBase = "https://github.com/YishenTu/claudian/releases/download/$ClaudianVersion"
Download-File -Url "$claudianBase/main.js" -OutFile (Join-Path $pluginDir "main.js")
Download-File -Url "$claudianBase/manifest.json" -OutFile (Join-Path $pluginDir "manifest.json")
Download-File -Url "$claudianBase/styles.css" -OutFile (Join-Path $pluginDir "styles.css")

Write-Info "Downloading vault-level Codex skills"
foreach ($skill in @("g-ark-vault-steward", "g-ark-source-distiller")) {
  $skillDir = Join-Path $VaultPath ".codex\skills\$skill"
  New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
  Download-File -Url "$RawBase/setup/skills/$skill/SKILL.md" -OutFile (Join-Path $skillDir "SKILL.md")
}

$resolvedCodexPath = Resolve-CodexPath
if ($resolvedCodexPath) {
  $hostname = hostname
  $escaped = $resolvedCodexPath.Replace("\", "\\")
  Write-Info "Writing Claudian Codex provider config for $resolvedCodexPath"
  Write-TextFile -Path (Join-Path $VaultPath ".claudian\claudian-settings.json") -Content @"
{
  "model": "gpt-5.5",
  "enableAutoTitleGeneration": false,
  "providerConfigs": {
    "codex": {
      "enabled": true,
      "safeMode": "workspace-write",
      "cliPath": "",
      "cliPathsByHost": {
        "$hostname": "$escaped"
      },
      "customModels": "gpt-5.5",
      "reasoningSummary": "detailed",
      "environmentVariables": "",
      "environmentHash": "",
      "installationMethodsByHost": {
        "$hostname": "native-windows"
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
"@
} else {
  Write-Warning "Codex CLI was not found. Install it and set the path in Claudian settings."
}

Write-Info "Done. Open Obsidian -> Open folder as vault -> $VaultPath"
