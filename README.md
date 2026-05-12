<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&height=190&color=0:7C3AED,42:06B6D4,100:F97316&text=ObsiChan&fontColor=ffffff&fontSize=64&fontAlignY=36&desc=Your%20Obsidian%20External%20Brain%20Mascot&descAlignY=58&animation=fadeIn" alt="ObsiChan banner" width="100%" />

  [![Obsidian](https://img.shields.io/badge/Obsidian-Vault-8B5CF6?style=for-the-badge&logo=obsidian&logoColor=white)](https://obsidian.md/)
  [![Codex](https://img.shields.io/badge/Codex-Skills-111827?style=for-the-badge)](https://www.npmjs.com/package/@openai/codex)
  [![Claudian](https://img.shields.io/badge/Claudian-Plugin-D97757?style=for-the-badge)](https://github.com/YishenTu/claudian)
  [![Platform](https://img.shields.io/badge/Windows%20%7C%20macOS%20%7C%20Linux-Ready-06B6D4?style=for-the-badge)](#-快速开始)

  <br />

  <p>
    一只住进 Obsidian 的知识看板娘：帮你把灵感、资料、概念、项目和 AI 协作整理成可持续生长的外置大脑。
  </p>

</div>

---

## ObsiChan 是什么

**ObsiChan** 是一个可复刻的 Obsidian 外置大脑安装包。它会把一个空目录初始化成适合人类长期思考、也适合 AI Agent 持续维护的个人知识库。

它不只是“文件夹模板”。ObsiChan 会一起准备：

- Obsidian vault 目录结构
- AI 可读的系统规则
- Claudian 插件安装
- Codex provider 配置
- vault-level Codex skills
- 跨 Windows / macOS / Linux 的安装与更新脚本

你可以把它理解成 **G-Ark 外置大脑架构的可安装版本**：G-Ark 是一座知识方舟，ObsiChan 是帮你把方舟搭起来、整理好、持续更新的小助手。

## 第一条咒语

```text
1. 把新想法丢进 10_Inbox/Quick Capture.md
2. 把外部资料沉淀到 20_Sources/
3. 把自己的理解拆成 30_Notes/ 里的概念、问题、模型
4. 用 40_Maps/ 把知识点接成星图
5. 在 50_Projects/ 和 70_Outputs/ 里把想法变成现实
```

预期效果：你不再靠脑内缓存硬扛世界，ObsiChan 会替你保存线索、关系与下一步行动。

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

## 已安装用户更新

ObsiChan 的 skills 会继续升级。已经安装过外置大脑的用户不需要重装 vault，只需要运行更新脚本。

### Windows

```powershell
$script = "$env:TEMP\obsichan-update.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.ps1" -OutFile $script
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark"
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.sh -o /tmp/obsichan-update.sh
VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-update.sh
```

默认只更新：

- `.codex/skills/g-ark-vault-steward/SKILL.md`
- `.codex/skills/g-ark-source-distiller/SKILL.md`
- 缺失时补建 `20_Sources/Collections`

它不会覆盖你的笔记、MOC、项目和输出。

## ObsiChan 会创建什么

```text
G-Ark/
  00_System/         AI 上下文、规则、流程、分类表
  10_Inbox/          快速捕获
  20_Sources/        来源笔记
    Collections/     资料汇总、网站清单、学习资源合集
  30_Notes/          概念、问题、模型、判断
  40_Maps/           MOC 内容地图
  50_Projects/       当前项目
  60_Areas/          长期责任区
  70_Outputs/        文章、方案、报告、Prompt
  80_Assets/         图片、PDF、音频、导出文件
  _templates/        Obsidian 模板
  .codex/skills/     vault-level Codex skills
  .obsidian/         Obsidian 配置与插件
```

核心流转：

```text
捕获 -> 来源 -> 理解 -> 连接 -> 行动 -> 产出
```

对应目录：

```text
10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs
```

## 架构思想

### 1. 文件夹管生命周期，MOC 管主题

`20_Sources` 不按“AI / 前端 / 强化学习”这种主题分文件夹，而是按来源形态分：

```text
Books / Articles / Papers / Videos / Courses / Documents / Collections
```

主题关系交给：

```text
topics
related
40_Maps/MOC - *.md
```

这样可以避免文件夹越来越碎。比如“多臂老虎机算法学习资料汇总”属于 `resource-list`，应该进入：

```text
20_Sources/Collections/
```

而不是新建：

```text
20_Sources/强化学习/
```

### 2. AI 需要协议，不只是权限

Agent 进入 vault 前会先读：

```text
00_System/AI_CONTEXT.md
00_System/SCHEMA.md
00_System/WORKFLOW.md
```

它会知道：

- 来源笔记和个人理解要分开
- AI 生成内容要标记 `status: ai-draft`
- 不确定内容要等待用户审核
- 主题导航用 MOC，而不是乱建文件夹

### 3. Skills 独立更新

ObsiChan 不把长篇 skill 塞进教程，而是放在：

```text
setup/skills/
```

安装和更新脚本会从 GitHub 下载最新版 skills 到：

```text
<vault>/.codex/skills/
```

这样教程、脚本、skills 可以各自演进。

## 内置 Codex Skills

### `$g-ark-vault-steward`

负责维护整个 vault：

- 清理 Inbox
- 更新 MOC
- 路由笔记
- 检查 AI 草稿
- 维护项目、领域、输出层
- 将 `resource-list` 归档到 `20_Sources/Collections`

源文件：

[setup/skills/g-ark-vault-steward/SKILL.md](./setup/skills/g-ark-vault-steward/SKILL.md)

### `$g-ark-source-distiller`

负责把外部资料整理进知识库：

- 生成来源笔记
- 提炼概念、问题、模型
- 标记 `status: ai-draft`
- 更新相关 MOC
- 按来源形态放入 `20_Sources` 的稳定子目录

源文件：

[setup/skills/g-ark-source-distiller/SKILL.md](./setup/skills/g-ark-source-distiller/SKILL.md)

## 看板娘组件路线图

GitHub README 不能直接运行交互脚本，所以 ObsiChan 暂时只在 README 中保留看板娘视觉风格。后续如果做文档站或 Obsidian 插件 UI，可以考虑这些 Live2D 方案：

| 组件 | 适合场景 | 备注 |
| --- | --- | --- |
| [oh-my-live2d](https://www.npmjs.com/package/oh-my-live2d) | 文档站、Vite/React/Vue 项目、快速挂载看板娘 | 支持 CDN/ES Module，引入简单，适合 ObsiChan Docs 站点 |
| [stevenjoezhang/live2d-widget](https://github.com/stevenjoezhang/live2d-widget) | 经典网页角落看板娘 | 生态成熟，适合静态站点 |
| [guansss/pixi-live2d-display](https://github.com/guansss/pixi-live2d-display) | 自定义交互、Canvas/WebGL、复杂 UI | 更底层，更适合后续做 Obsidian 插件界面 |

注意：Live2D 模型本身通常有独立版权。引入看板娘时要确认模型授权，避免把不明来源模型打进仓库。

## 安装脚本

```text
setup/install.ps1  Windows PowerShell
setup/install.sh   macOS / Linux Bash
setup/update.ps1   Windows 更新脚本
setup/update.sh    macOS / Linux 更新脚本
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
    update.ps1
    update.sh
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
