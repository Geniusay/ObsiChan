<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&height=190&color=0:7C3AED,42:06B6D4,100:F97316&text=ObsiChan&fontColor=ffffff&fontSize=64&fontAlignY=36&desc=Obsidian%20External%20Brain%20Installer&descAlignY=58&animation=fadeIn" alt="ObsiChan banner" width="100%" />

  [![Obsidian](https://img.shields.io/badge/Obsidian-Vault-8B5CF6?style=for-the-badge&logo=obsidian&logoColor=white)](https://obsidian.md/)
  [![Codex](https://img.shields.io/badge/Codex-Skills-111827?style=for-the-badge)](https://www.npmjs.com/package/@openai/codex)
  [![Claudian](https://img.shields.io/badge/Claudian-Plugin-D97757?style=for-the-badge)](https://github.com/YishenTu/claudian)
  [![Platform](https://img.shields.io/badge/Windows%20%7C%20macOS%20%7C%20Linux-Ready-06B6D4?style=for-the-badge)](#快速开始)

  <br />

  <p>
    一只住进 Obsidian 的知识看板娘：把灵感、资料、概念、项目和 AI 协作整理成可持续生长的外置大脑。
  </p>

</div>

---

## 为什么做 ObsiChan

多数个人知识库最终会滑向两个极端：要么变成塞满剪藏的资料仓库，要么变成只靠热情维护几天的复杂系统。AI 时代又加了一层新问题：Agent 可以帮你写、改、总结、链接，但如果知识库没有清晰规则，它也会把来源、判断、草稿和输出混在一起。

**ObsiChan** 想解决的是这件事：让一个空的 Obsidian vault 从第一天起就具备清晰结构、AI 协作边界和可更新的操作能力。

它不是另一个“漂亮文件夹模板”，而是一套外置大脑启动器：

- 帮你搭好 Obsidian 第二大脑的目录骨架。
- 给 AI Agent 一份可执行的 vault 规则。
- 用 Claudian 把 Codex 接进 Obsidian。
- 用 vault-level Codex skills 固化整理、提炼、复盘的方法。
- 让已经安装的用户可以持续更新 skills，而不是重装整个知识库。

一句话：**ObsiChan 负责把知识库从“文件夹”变成“可被人和 AI 一起维护的认知系统”。**

## 设计思想

ObsiChan 的底层思想来自几套成熟笔记方法论的组合，而不是迷信单一分类法。

### 1. PARA：让知识进入行动

PARA 把信息按行动关系拆成 Projects、Areas、Resources、Archives。ObsiChan 取其中最实用的部分：

- `50_Projects`：有明确结果、正在推进的事情。
- `60_Areas`：长期责任区，比如学习、职业、健康、财务、创作。
- `70_Outputs`：文章、方案、报告、Prompt 等可复用产出。

这样知识库不会只收藏资料，而会持续流向项目和输出。

### 2. Zettelkasten：把资料变成自己的理解

Zettelkasten 的核心不是卡片数量，而是把信息拆成可链接、可复用的原子想法。

ObsiChan 对应为：

- `20_Sources`：外部资料和来源笔记，回答“资料说了什么”。
- `30_Notes`：概念、问题、模型、判断，回答“我理解了什么”。
- `source`、`related`、`topics`：保留来源和连接关系。

来源和理解分开，可以减少 AI 总结、个人判断、原文引用混在一起的风险。

### 3. MOC / LYT：用地图组织主题

文件夹适合表达“生命周期”，但不适合表达主题。一个笔记可能同时属于 AI、产品、学习和写作。

所以 ObsiChan 使用：

```text
40_Maps/MOC - *.md
```

MOC 负责主题导航，文件夹负责工作流阶段。

这也是为什么 `20_Sources` 不建议按主题创建大量文件夹。比如“多臂老虎机算法学习资料汇总”应该放在：

```text
20_Sources/Collections/
```

它的主题关系交给：

```text
topics: [AI, 机器学习, 强化学习, 多臂老虎机]
related: ["[[MOC - AI]]", "[[MOC - 学习]]"]
```

### 4. AI-Native Vault：给 Agent 明确协议

ObsiChan 默认把 AI 当作协作者，而不是神谕机器。

Agent 进入 vault 前会先读：

```text
00_System/AI_CONTEXT.md
00_System/SCHEMA.md
00_System/WORKFLOW.md
```

这几份文件规定：

- 什么内容放在哪里。
- AI 生成内容必须标记 `status: ai-draft`。
- 来源笔记和个人理解要分开。
- 主题导航用 MOC，不要随意新建主题文件夹。
- 不删除用户已有笔记，除非用户明确要求。

### 5. Skills 可更新：把方法论变成可维护能力

ObsiChan 把两个核心能力做成 vault-level Codex skills：

- `$g-ark-vault-steward`：维护、整理、复盘和扩展 vault。
- `$g-ark-source-distiller`：把外部资料提炼成来源笔记、概念笔记和 MOC 更新。

它们放在：

```text
setup/skills/
```

安装后进入：

```text
<vault>/.codex/skills/
```

这样 skills 可以从 GitHub 单独更新，不需要重装用户的知识库。

## 快速开始

完整安装教程见：

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

已安装用户更新 skills：

```bash
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.sh -o /tmp/obsichan-update.sh
VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-update.sh
```

Windows 更新：

```powershell
$script = "$env:TEMP\obsichan-update.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.ps1" -OutFile $script
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark"
```

## 贡献代码

欢迎改进 ObsiChan，但请保持这个项目的边界清晰：它是外置大脑安装器，不是用户 vault 内容仓库。

开发前建议先读：

[docs/spec/development_spec.md](./docs/spec/development_spec.md)

基本原则：

- 改安装脚本时，同步检查 `setup_tutorial.md`。
- 改 skills 时，同步检查 `setup/skills`、安装教程和开发规范。
- 改默认 vault 结构时，同步检查 README、安装脚本、教程和规范。
- 不要提交用户个人笔记、Claudian 会话、Obsidian workspace 状态。

本地开发流程：

```bash
git clone https://github.com/Geniusay/ObsiChan.git
cd ObsiChan
git checkout -b docs/improve-readme
```

提交示例：

```bash
git add .
git commit -m "docs(readme): clarify external brain design"
git push origin docs/improve-readme
```

然后发起 Pull Request。

## License

MIT

<div align="center">

`ObsiChan is watching your Inbox.`

</div>
