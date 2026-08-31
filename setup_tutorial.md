# ObsiChan 外置大脑构建安装教程

## 1. 你会得到什么？

ObsiChan 是一套面向 Obsidian + Codex Agent 的外置大脑初始化方案。它会帮你搭建一个可被人类使用、也可被 AI Agent 长期维护的个人知识库。

完成安装后，你会得到：

- 一个结构化 Obsidian vault。
- 一套 `00_System` 系统规则，让 Agent 知道如何读写知识库。
- 一套 Inbox、Sources、Notes、Maps、Projects、Areas、Outputs、Assets 目录。
- Claudian Obsidian 插件。
- Codex provider 配置。
- 一个统一的 vault-level Codex skill：`$g-ark`。

整体工作流：

```text
10_Inbox -> 20_Sources -> 30_Notes -> 40_Maps -> 50_Projects / 70_Outputs
```

## 2. 前置条件

### 2.1 必需软件

- Obsidian Desktop
- Git
- Node.js
- Codex CLI

### 2.2 Codex CLI 安装

Windows / macOS / Linux 都可以使用 npm 安装：

```bash
npm install -g @openai/codex
codex --version
codex login
```

如果你使用 Codex Desktop 或其他安装器，也可以使用系统已有的 `codex` 可执行文件。唯一要求是终端里能运行：

```bash
codex --version
```

## 3. 快速安装

### 3.1 Windows PowerShell

默认安装到：

```text
$HOME\Documents\G-Ark
```

运行：

```powershell
$script = "$env:TEMP\obsichan-install.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.ps1" -OutFile $script
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark"
```

自定义 vault 路径：

```powershell
$script = "$env:TEMP\obsichan-install.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.ps1" -OutFile $script
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark"
```

如果 Claudian 没能自动识别 Codex，可以显式传入路径：

```powershell
powershell -ExecutionPolicy Bypass -File $script `
  -VaultPath "$HOME\Documents\G-Ark" `
  -CodexPath "$HOME\AppData\Local\OpenAI\Codex\bin\codex.exe"
```

### 3.2 macOS / Linux

默认安装到：

```text
~/Documents/G-Ark
```

运行：

```bash
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.sh -o /tmp/obsichan-install.sh
bash /tmp/obsichan-install.sh
```

自定义 vault 路径：

```bash
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.sh -o /tmp/obsichan-install.sh
VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-install.sh
```

如果 Claudian 没能自动识别 Codex，可以显式传入路径：

```bash
CODEX_PATH="$(which codex)" VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-install.sh
```

## 4. 安装脚本在哪里？

脚本已从教程正文中抽离，统一归档在仓库的 `setup/` 目录：

```text
setup/install.ps1
setup/install.sh
setup/update.ps1
setup/update.sh
```

对应 GitHub 下载地址：

- Windows: `https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.ps1`
- macOS / Linux: `https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.sh`
- Windows 更新: `https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.ps1`
- macOS / Linux 更新: `https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.sh`

脚本会自动完成：

- 创建 vault 目录结构。
- 写入 Obsidian 基础配置。
- 写入 `00_System` 系统文件。
- 写入初始 MOC、Areas、Templates。
- 下载并安装 Claudian。
- 从 GitHub 下载完整的 `$g-ark` skill、默认相对配置和机器可读 schema。
- 尝试写入 Claudian Codex provider 配置。

### 4.1 已安装用户如何更新

ObsiChan 的 `$g-ark` skill 会持续更新。已安装用户不需要重装整个 vault，可以只运行更新脚本。

Windows PowerShell：

```powershell
$script = "$env:TEMP\obsichan-update.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.ps1" -OutFile $script
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark"
```

macOS / Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/update.sh -o /tmp/obsichan-update.sh
VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-update.sh
```

默认更新 `.gark/skill/` 下的统一 skill，并补建缺失的 `.gark/config.toml`、`00_System/GARK_SCHEMA.json` 和 `20_Sources/Collections`。已有配置和 schema 不会被覆盖。

升级脚本会把旧的 `g-ark-vault-steward`、`g-ark-source-distiller`、`g-ark-session-distiller` 移到 `.gark/legacy-skills/`。这些备份不会再被 Codex 发现，但仍可手动恢复。脚本不会覆盖你的笔记、MOC、项目或输出文件。

如果你也想更新 Claudian 插件：

Windows：

```powershell
powershell -ExecutionPolicy Bypass -File $script -VaultPath "$HOME\Documents\G-Ark" -UpdateClaudian
```

macOS / Linux：

```bash
UPDATE_CLAUDIAN=1 VAULT_PATH="$HOME/Documents/G-Ark" bash /tmp/obsichan-update.sh
```

## 5. Skill 在哪里？

统一 skill 的版本化源码放在：

```text
setup/skills/g-ark/
```

安装脚本会下载完整目录、默认配置和 schema，并建立唯一发现入口：

```text
<vault>/.gark/config.toml
<vault>/.gark/skill/
<vault>/00_System/GARK_SCHEMA.json
<vault>/.codex/skills/g-ark -> ../../.gark/skill
```

只更新 skill 时，推荐运行上一节的更新脚本。不要只下载 `SKILL.md`，因为统一版还依赖 `references/` 和 `scripts/gark.py`。

默认配置只使用相对路径：

```toml
vault_root = ".."
schema_path = "00_System/GARK_SCHEMA.json"
```

更新器不会读取、打印、上传或覆盖现有 `config.toml`。Skill 的笔记和操作报告也应只使用 vault 相对路径，不包含凭据、用户名或机器绝对路径。

## 6. 用 Obsidian 打开 vault

1. 打开 Obsidian。
2. 选择 `Open folder as vault`。
3. 打开你的 vault 路径：
   - Windows: `$HOME\Documents\G-Ark`
   - macOS: `~/Documents/G-Ark`
   - Linux: `~/Documents/G-Ark`
4. 进入 `Settings -> Community plugins`。
5. 关闭 Restricted Mode。
6. 启用 Claudian。

## 7. 配置 Claudian 使用 Codex provider

安装脚本会尽量自动写入 Codex provider 配置。若仍需手动调整：

1. 打开 `Settings -> Community plugins -> Claudian`。
2. 启用 Codex provider。
3. 将 Settings Provider 切换为 `Codex`。
4. 设置 Codex CLI 路径。

常见路径：

```text
Windows: C:\Users\<用户名>\AppData\Local\OpenAI\Codex\bin\codex.exe
macOS: /opt/homebrew/bin/codex 或 /usr/local/bin/codex
Linux: /usr/local/bin/codex 或 ~/.npm-global/bin/codex
```

macOS / Linux 可用：

```bash
which codex
```

Windows 可用：

```powershell
Get-Command codex
```

## 8. 验收

在目标 vault 根目录执行：

```bash
codex debug prompt-input "测试 ObsiChan skills" | grep "g-ark"
```

Windows PowerShell：

```powershell
codex debug prompt-input "测试 ObsiChan skills" | Select-String "g-ark"
```

预期只看到：

```text
g-ark
```

在 Obsidian 的 Claudian 设置页中，进入 `Codex Skills`，点击刷新，应该能看到：

```text
$g-ark
```

## 9. 常见问题

### 9.0 为什么 `resource-list` 没有进入子文件夹？

早期版本的 `20_Sources` 只创建了 Books、Articles、Papers、Videos、Courses、Documents。像“资料汇总”“网站清单”“学习资源合集”这种 `source_type: resource-list` 没有稳定落点，所以会留在 `20_Sources` 根目录。

新版规则增加：

```text
20_Sources/Collections
```

用于存放：

- 学习资料汇总
- 网站清单
- 资源合集
- curated links
- `source_type: resource-list`

不建议为每个主题创建大文件夹，例如 `20_Sources/强化学习`、`20_Sources/前端设计`。主题关系应该交给 `topics`、`related` 和 `40_Maps`，否则文件夹会很快膨胀。

### 9.1 Claudian 报 `Claude Code native binary not found`

原因通常不是 Codex 没装，而是 Claudian 仍在恢复旧 Claude 状态，例如：

- 旧 tab 的 `draftModel` 是 `haiku`、`sonnet`、`opus`。
- `.claudian/sessions/` 中有旧会话 `"providerId": "claude"`。
- 自动标题生成触发了旧 Claude 会话。

解决：

1. 完全退出 Obsidian。
2. 检查 `<vault>/.obsidian/plugins/claudian/data.json`。
3. 删除或备份 `<vault>/.claudian/sessions/` 中旧 Claude 会话。
4. 确认 `<vault>/.claudian/claudian-settings.json` 中：

```json
{
  "settingsProvider": "codex",
  "enableAutoTitleGeneration": false
}
```

5. 重启 Obsidian。

### 9.2 Codex Skills 页面仍显示空

检查：

```bash
find "$VAULT/.codex/skills" -name SKILL.md
codex debug prompt-input "测试 ObsiChan skills" | grep "g-ark"
```

如果 Codex CLI 能看到，但 Claudian 看不到：

- 检查 Claudian 的 Codex CLI path 是否指向 `which codex` 或 `Get-Command codex`。
- 确认 Settings Provider 是 Codex。
- 完全退出并重启 Obsidian。

### 9.3 macOS 看不到 `.obsidian` 或 `.codex`

这些是隐藏目录。

Finder 中按：

```text
Command + Shift + .
```

终端中查看：

```bash
ls -la
```

## 10. 给 macOS Agent 的执行提示

你可以把下面这段直接交给 macOS 上的 Agent：

```text
请在 macOS 上安装 ObsiChan 外置大脑。

目标路径：~/Documents/G-Ark

执行要求：
1. 确认 Obsidian、Git、Node.js、Codex CLI 已安装。
2. 确认 `codex --version` 可运行。
3. 下载并执行：
   curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.sh -o /tmp/obsichan-install.sh
   VAULT_PATH="$HOME/Documents/G-Ark" CODEX_PATH="$(which codex)" bash /tmp/obsichan-install.sh
4. 用 Obsidian 的 Open folder as vault 打开 `~/Documents/G-Ark`。
5. 启用 Claudian 社区插件。
6. 确认 Claudian 使用 Codex provider。
7. 验收 `.codex/skills/g-ark` 指向 `.gark/skill`，并且 Claudian 的 Codex Skills 页面只显示 `$g-ark`。
8. 如果出现 Claude Code native binary 报错，按本文档 9.1 清理旧 Claude 状态。
```
