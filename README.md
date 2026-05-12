<div align="center">

# ObsiChan

### 给 Obsidian 装上一只会整理知识的外置大脑看板娘

`Obsidian + Codex + Claudian + Vault-Level Skills`

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-7c3aed)](#-快速开始)
[![Obsidian](https://img.shields.io/badge/Obsidian-vault-8b5cf6)](https://obsidian.md/)
[![Codex](https://img.shields.io/badge/Codex-skills-111827)](https://www.npmjs.com/package/@openai/codex)
[![Claudian](https://img.shields.io/badge/Claudian-plugin-d97757)](https://github.com/YishenTu/claudian)

</div>

ObsiChan 是一个可复刻的 Obsidian 外置大脑安装包。它会把一个空目录初始化成适合人类长期思考、也适合 AI Agent 持续维护的个人知识库。

它不像普通模板那样只给你一堆文件夹。ObsiChan 会同时准备：

- Obsidian vault 目录结构
- AI 可读的系统规则
- Claudian 插件安装
- Codex provider 配置
- vault-level Codex skills
- 跨 Windows / macOS / Linux 的安装脚本

把它想象成一只住在你 Obsidian 里的知识看板娘：你丢资料，她帮你分拣；你想复盘，她帮你找线索；你要写东西，她把散落笔记牵成一张地图。

## 快速开始

完整安装说明见：

[setup_tutorial.md](./setup_tutorial.md)

### Windows PowerShell

```powershell
$script = "$env:TEMP\obsichan-install.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.ps1" -OutFile $script
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark"
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.sh -o /tmp/obsichan-install.sh
VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-install.sh
```

安装完成后，用 Obsidian 的 `Open folder as vault` 打开：

```text
~/Documents/G-Ark
```

或你在脚本中指定的路径。

## ObsiChan 会创建什么？

```text
G-Ark/
  00_System/      AI 上下文、规则、流程、分类表
  10_Inbox/       快速捕获
  20_Sources/     来源笔记
  30_Notes/       概念、问题、模型、判断
  40_Maps/        MOC 内容地图
  50_Projects/    当前项目
  60_Areas/       长期责任区
  70_Outputs/     文章、方案、报告、Prompt
  80_Assets/      图片、PDF、音频、导出文件
  _templates/     Obsidian 模板
  .codex/skills/  vault-level Codex skills
  .obsidian/      Obsidian 配置与插件
```

核心流转方式：

```text
捕获 -> 来源 -> 理解 -> 连接 -> 行动 -> 产出
```

对应到目录：

```text
10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs
```

## 架构思想

ObsiChan 的设计来自三个判断：

### 1. 知识库不是收藏夹

资料进入 `20_Sources`，但真正有价值的是被你理解后的 `30_Notes`。

### 2. AI 需要规则，不只是权限

Agent 进入 vault 前会先读：

```text
00_System/AI_CONTEXT.md
00_System/SCHEMA.md
00_System/WORKFLOW.md
```

这样它知道什么能改、什么要审核、笔记应该放哪里。

### 3. Skills 应该独立更新

ObsiChan 不把长篇 skill 塞进教程，而是放在：

```text
setup/skills/
```

安装脚本会从 GitHub 下载最新版 skills 到目标 vault：

```text
<vault>/.codex/skills/
```

这样教程、脚本、skills 可以独立演进。

## 内置 Codex Skills

### `$g-ark-vault-steward`

负责维护整个 vault：

- 清理 Inbox
- 更新 MOC
- 路由笔记
- 检查 AI 草稿
- 维护项目、领域、输出层

源文件：

[setup/skills/g-ark-vault-steward/SKILL.md](./setup/skills/g-ark-vault-steward/SKILL.md)

### `$g-ark-source-distiller`

负责把外部资料整理进知识库：

- 生成来源笔记
- 提炼概念、问题、模型
- 标记 `status: ai-draft`
- 更新相关 MOC

源文件：

[setup/skills/g-ark-source-distiller/SKILL.md](./setup/skills/g-ark-source-distiller/SKILL.md)

## 安装脚本

```text
setup/install.ps1  Windows PowerShell
setup/install.sh   macOS / Linux Bash
```

脚本会自动：

- 创建 vault 目录结构
- 写入 Obsidian 配置
- 写入系统文件和 starter MOC
- 下载 Claudian 插件
- 下载 Codex skills
- 尝试配置 Claudian 使用 Codex provider

## 验收

安装后在 vault 根目录执行：

```bash
codex debug prompt-input "测试 ObsiChan skills" | grep "g-ark"
```

Windows PowerShell：

```powershell
codex debug prompt-input "测试 ObsiChan skills" | Select-String "g-ark"
```

预期能看到：

```text
g-ark-vault-steward
g-ark-source-distiller
```

在 Obsidian 中启用 Claudian 后，进入 `Codex Skills` 页面，应该能看到：

```text
$g-ark-vault-steward
$g-ark-source-distiller
```

## 常见问题

### Claudian 报 `Claude Code native binary not found`

你可能使用的是 Codex provider，但 Claudian 仍在恢复旧 Claude tab 或旧 Claude 会话。

处理方式见：

[setup_tutorial.md#91-claudian-报-claude-code-native-binary-not-found](./setup_tutorial.md#91-claudian-报-claude-code-native-binary-not-found)

### Codex Skills 页面为空

先确认文件存在：

```bash
find .codex/skills -name SKILL.md
```

再确认 Codex 能看到：

```bash
codex debug prompt-input "测试 ObsiChan skills" | grep "g-ark"
```

更完整排错见：

[setup_tutorial.md#92-codex-skills-页面仍显示空](./setup_tutorial.md#92-codex-skills-页面仍显示空)

## 项目结构

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

## 维护规范

后续开发者或 AI Agent 请先阅读：

[docs/spec/development_spec.md](./docs/spec/development_spec.md)

核心约定：

- 改脚本，要同步检查 `setup_tutorial.md`。
- 改 skills，要同步检查教程和开发规范。
- 改 vault 默认结构，要同步检查脚本、教程、README 和规范。
- 不要提交用户个人 vault 内容。

## License

MIT

<div align="center">

愿你的 Obsidian 不再变成资料仓库，而是成为会陪你一起长大的外置大脑。

`ObsiChan is watching your Inbox.`

</div>
