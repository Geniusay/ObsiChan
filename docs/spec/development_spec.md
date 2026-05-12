# ObsiChan 项目开发规范文档

## 1. 文档目的

本文档用于约束 ObsiChan 项目的后续维护方式，帮助开发者和 AI Agent 在修改安装脚本、Codex skills、教程文档、README 和项目规范时保持一致。

ObsiChan 不是一个传统应用仓库，而是一个“外置大脑安装包”：它通过脚本、Obsidian 配置、Claudian 插件、Codex provider 和 vault-level skills，把一个空目录初始化为可供人类与 AI Agent 共同维护的 Obsidian 第二大脑。

## 2. 项目定位

### 2.1 核心目标

- 提供一键式跨平台 Obsidian 外置大脑初始化方案。
- 将 skills 从教程中抽离，作为可单独更新的版本化资产。
- 将安装脚本从教程中抽离，避免文档和脚本逻辑重复。
- 让 Windows、macOS、Linux 上的 Agent 都能按相同架构复刻 vault。
- 降低 AI Agent 误删、误分类、混淆来源和个人判断的风险。

### 2.2 非目标

- 不实现 Obsidian 插件本体。
- 不替代 Claudian、Codex CLI、Obsidian 的官方安装流程。
- 不负责用户的私有 vault 内容同步。
- 不将用户笔记内容上传到仓库。
- 不默认创建复杂的 Raw、Wiki、Archive 分层，除非项目后续明确升级。

## 3. 仓库结构规范

```text
ObsiChan/
  README.md
  setup_tutorial.md
  setup/
    install.ps1
    install.sh
    skills/
      g-ark-vault-steward/
        SKILL.md
      g-ark-source-distiller/
        SKILL.md
  docs/
    spec/
      development_spec.md
```

### 3.1 根目录

| 文件 | 职责 |
| --- | --- |
| `README.md` | 面向首次访问者的项目介绍、思想说明和快速使用入口 |
| `setup_tutorial.md` | 完整安装教程，必须引用 `setup/` 中的脚本和 skills |

### 3.2 `setup/`

| 文件/目录 | 职责 |
| --- | --- |
| `setup/install.ps1` | Windows PowerShell 安装脚本 |
| `setup/install.sh` | macOS/Linux Bash 安装脚本 |
| `setup/skills/*/SKILL.md` | 可单独更新的 vault-level Codex skills |

### 3.3 `docs/spec/`

| 文件 | 职责 |
| --- | --- |
| `docs/spec/development_spec.md` | 项目开发和维护规范 |

## 4. 安装脚本开发规范

### 4.1 跨平台原则

Windows 使用 PowerShell：

```text
setup/install.ps1
```

macOS/Linux 使用 Bash：

```text
setup/install.sh
```

两个脚本必须尽量保持行为一致：

- 创建相同的 vault 目录结构。
- 写入相同语义的 Obsidian 配置。
- 写入相同语义的系统文件。
- 下载同版本 Claudian。
- 下载同一仓库分支下的 skills。
- 尝试配置 Claudian 的 Codex provider。

### 4.2 参数规范

PowerShell 脚本必须支持：

```powershell
-VaultPath
-Branch
-RepoRawBase
-ClaudianVersion
-CodexPath
```

Bash 脚本必须支持环境变量：

```bash
VAULT_PATH
BRANCH
REPO_RAW_BASE
CLAUDIAN_VERSION
CODEX_PATH
```

### 4.3 脚本安全规范

- 不删除用户已有笔记。
- 不清空已有 vault。
- 不写入用户 home 根目录下的无关文件。
- 不硬编码用户私有路径。
- 不把 Windows 路径写入 macOS/Linux 配置。
- 不默认迁移 `.claudian/sessions`。
- 不默认提交或上传用户 vault 内容。

### 4.4 下载地址规范

脚本下载仓库资产必须使用 GitHub raw URL：

```text
https://raw.githubusercontent.com/Geniusay/ObsiChan/<branch>/setup/...
```

不要在教程中复制完整 skill 内容作为主要安装方式。教程只声明下载位置和更新方式。

### 4.5 Claudian 配置规范

脚本可以尝试写入：

```text
<vault>/.claudian/claudian-settings.json
```

配置目标：

```json
{
  "settingsProvider": "codex",
  "enableAutoTitleGeneration": false
}
```

`enableAutoTitleGeneration` 默认关闭，原因是旧 Claude 会话可能触发 Claude title generation，导致出现 `Claude Code native binary not found`。

## 5. Skills 开发规范

### 5.1 Skill 存放位置

仓库内：

```text
setup/skills/<skill-name>/SKILL.md
```

安装后的 vault 内：

```text
<vault>/.codex/skills/<skill-name>/SKILL.md
```

### 5.2 当前内置 skills

| Skill | 职责 |
| --- | --- |
| `g-ark-vault-steward` | 维护、整理、复盘、扩展 vault |
| `g-ark-source-distiller` | 将外部资料提炼为来源笔记、概念笔记和 MOC 更新 |

### 5.3 Skill Frontmatter 规范

每个 skill 必须包含：

```yaml
---
name: skill-name
description: 清晰描述触发场景和能力边界
---
```

`description` 必须包含：

- 什么时候使用该 skill。
- 该 skill 会做什么。
- 常见用户表达方式。
- 适用对象为 ObsiChan/G-Ark Obsidian vault。

### 5.4 Skill 内容规范

每个 skill 应包含：

- First Files To Read
- Core Workflow
- Editing Principles
- Output To User

Skill 不应包含：

- 私有 API key。
- 用户个人路径。
- 一次性对话历史。
- 与 ObsiChan 无关的全局偏好。

## 6. 文档维护规范

### 6.1 `setup_tutorial.md`

安装教程必须保持：

- 面向终端用户。
- 先给快速安装，再解释目录和排错。
- 脚本使用 GitHub raw URL。
- skills 使用 `setup/skills` 下载说明。
- 包含 macOS Agent 可直接执行的提示词。
- 包含 Claudian + Codex provider 的常见排错。

每次改动 `setup/install.ps1` 或 `setup/install.sh` 后，必须检查 `setup_tutorial.md` 中对应命令是否仍正确。

### 6.2 `README.md`

README 必须保持：

- 第一屏说明项目是什么。
- 快速使用链接到 `setup_tutorial.md`。
- 简明介绍外置大脑架构思想。
- 列出跨平台支持。
- 列出仓库结构。
- 不塞入过长安装脚本。

README 可以保持轻松、可爱、有二次元风格，但不能牺牲可执行性。

### 6.3 `docs/spec/development_spec.md`

开发规范应在以下情况更新：

- 新增或删除目录。
- 新增或删除 skill。
- 改变安装方式。
- 改变 Claudian provider 策略。
- 改变 vault 默认结构。

## 7. Vault 架构规范

默认 vault 结构：

```text
00_System/
10_Inbox/
20_Sources/
30_Notes/
40_Maps/
50_Projects/
60_Areas/
70_Outputs/
80_Assets/
_templates/
.obsidian/
.codex/skills/
```

### 7.1 暂不默认创建的目录

| 目录 | 何时加入 |
| --- | --- |
| `20_Raw` | 原始资料明显变多，需要不可变证据层时 |
| `40_Wiki` | AI 编译领域知识明显增多时 |
| `90_Archive` | 完成项目和过期资料明显增多时 |

### 7.2 AI 写入原则

- 来源笔记进入 `20_Sources`。
- 用户自己的长期理解进入 `30_Notes`。
- 主题导航进入 `40_Maps`。
- 行动进入 `50_Projects`。
- 输出进入 `70_Outputs`。
- AI 生成内容必须标记 `status: ai-draft`。

## 8. 测试与验收规范

### 8.1 静态检查

每次提交前执行：

```bash
git status --short
```

检查脚本和文档是否包含错误路径：

```bash
grep -R "D:\\\\Code\\\\WorkSpace" .
grep -R "C:\\\\Users\\\\WIN11" .
```

这些路径只能出现在示例或 Windows 说明中，不能出现在 macOS/Linux 执行逻辑中。

### 8.2 Skill 可见性验收

在安装后的 vault 根目录执行：

```bash
codex debug prompt-input "测试 ObsiChan skills" | grep "g-ark"
```

Windows PowerShell：

```powershell
codex debug prompt-input "测试 ObsiChan skills" | Select-String "g-ark"
```

必须能看到：

```text
g-ark-vault-steward
g-ark-source-distiller
```

### 8.3 Obsidian 验收

打开 Obsidian 后检查：

- vault 文件树存在标准目录。
- Claudian 插件可启用。
- Claudian 使用 Codex provider。
- Codex Skills 页面能看到两个 `$g-ark-*` skill。
- 新建聊天不出现 Claude Code native binary 报错。

## 9. 发布规范

### 9.1 提交信息

推荐提交格式：

```text
feat(setup): add cross-platform ObsiChan installer
docs(readme): add kawaii quick start guide
docs(spec): add development maintenance spec
fix(claudian): avoid stale Claude provider state
```

### 9.2 版本变更检查

更新 Claudian 版本时，必须同步修改：

- `setup/install.ps1`
- `setup/install.sh`
- `setup_tutorial.md`
- `README.md` 中相关说明，如有

更新 skills 时，必须同步检查：

- `setup/skills/*/SKILL.md`
- `setup_tutorial.md`
- `docs/spec/development_spec.md`

## 10. AI Agent 维护指令

后续 AI Agent 维护该项目时，请先读取：

```text
README.md
setup_tutorial.md
docs/spec/development_spec.md
setup/install.ps1
setup/install.sh
setup/skills/g-ark-vault-steward/SKILL.md
setup/skills/g-ark-source-distiller/SKILL.md
```

维护顺序：

1. 先判断改动属于脚本、skill、教程、README 还是规范。
2. 若改脚本，必须同步检查教程。
3. 若改 skill，必须同步检查教程和规范。
4. 若改默认 vault 结构，必须同步检查脚本、教程、README 和规范。
5. 不要把用户个人 vault 内容提交到该仓库。

## 11. 自检报告

1. YAML Frontmatter 合规性：
   - 本文档已移除模板级 Frontmatter。
   - 文档不包含模板占位符。

2. 内容完整性：
   - 已覆盖项目定位、目录结构、脚本规范、skills 规范、文档规范、测试验收、发布规范和 AI 维护指令。

3. 文档格式：
   - 文档使用开发规范类结构，适合开发者和 AI Agent 后续维护。

4. 文件命名：
   - 文件归档至 `docs/spec/development_spec.md`。

5. 内容质量：
   - 已结合 ObsiChan 的实际仓库结构、Claudian/Codex provider、跨平台脚本和 vault-level Codex skills。
