# ObsiChan 外置大脑构建安装教程

## 1. 你会得到什么？

ObsiChan 是一套面向 Obsidian + Codex Agent 的外置大脑初始化方案。它会帮你搭建一个可被人类使用、也可被 AI Agent 长期维护的个人知识库。

完成安装后，你会得到：

- 一个结构化 Obsidian vault。
- 一套 `00_System` 系统规则，让 Agent 知道如何读写知识库。
- 一套 Inbox、Sources、Notes、Maps、Projects、Areas、Outputs、Assets 目录。
- Claudian Obsidian 插件。
- Codex provider 配置。
- 两个 vault-level Codex skills：
  - `$g-ark-vault-steward`
  - `$g-ark-source-distiller`

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
powershell -ExecutionPolicy Bypass -File $script -VaultPath "D:\Code\WorkSpace\G-Ark"
```

如果 Claudian 没能自动识别 Codex，可以显式传入路径：

```powershell
powershell -ExecutionPolicy Bypass -File $script `
  -VaultPath "D:\Code\WorkSpace\G-Ark" `
  -CodexPath "C:\Users\<用户名>\AppData\Local\OpenAI\Codex\bin\codex.exe"
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
```

对应 GitHub 下载地址：

- Windows: `https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.ps1`
- macOS / Linux: `https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/install.sh`

脚本会自动完成：

- 创建 vault 目录结构。
- 写入 Obsidian 基础配置。
- 写入 `00_System` 系统文件。
- 写入初始 MOC、Areas、Templates。
- 下载并安装 Claudian。
- 从 GitHub 下载 vault-level Codex skills。
- 尝试写入 Claudian Codex provider 配置。

## 5. Skills 在哪里？

两个 skill 已从教程和本地 vault 中提取出来，统一放在：

```text
setup/skills/g-ark-vault-steward/SKILL.md
setup/skills/g-ark-source-distiller/SKILL.md
```

安装脚本会从 GitHub raw 地址下载它们，并安装到目标 vault：

```text
<vault>/.codex/skills/g-ark-vault-steward/SKILL.md
<vault>/.codex/skills/g-ark-source-distiller/SKILL.md
```

如果你只想更新 skills，不想重装 vault，可以手动下载：

```bash
mkdir -p "$VAULT/.codex/skills/g-ark-vault-steward"
mkdir -p "$VAULT/.codex/skills/g-ark-source-distiller"
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/skills/g-ark-vault-steward/SKILL.md -o "$VAULT/.codex/skills/g-ark-vault-steward/SKILL.md"
curl -fsSL https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/skills/g-ark-source-distiller/SKILL.md -o "$VAULT/.codex/skills/g-ark-source-distiller/SKILL.md"
```

Windows PowerShell：

```powershell
$VAULT = "$HOME\Documents\G-Ark"
New-Item -ItemType Directory -Path "$VAULT\.codex\skills\g-ark-vault-steward" -Force | Out-Null
New-Item -ItemType Directory -Path "$VAULT\.codex\skills\g-ark-source-distiller" -Force | Out-Null
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/skills/g-ark-vault-steward/SKILL.md" -OutFile "$VAULT\.codex\skills\g-ark-vault-steward\SKILL.md"
Invoke-WebRequest "https://raw.githubusercontent.com/Geniusay/ObsiChan/main/setup/skills/g-ark-source-distiller/SKILL.md" -OutFile "$VAULT\.codex\skills\g-ark-source-distiller\SKILL.md"
```

## 6. 用 Obsidian 打开 vault

1. 打开 Obsidian。
2. 选择 `Open folder as vault`。
3. 打开你的 vault 路径：
   - Windows: `D:\Code\WorkSpace\G-Ark` 或 `$HOME\Documents\G-Ark`
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

预期能看到：

```text
g-ark-vault-steward
g-ark-source-distiller
```

在 Obsidian 的 Claudian 设置页中，进入 `Codex Skills`，点击刷新，应该能看到：

```text
$g-ark-vault-steward
$g-ark-source-distiller
```

## 9. 常见问题

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
7. 验收 `.codex/skills` 中存在两个 SKILL.md，并且 Claudian 的 Codex Skills 页面能看到 `$g-ark-vault-steward` 和 `$g-ark-source-distiller`。
8. 如果出现 Claude Code native binary 报错，按本文档 9.1 清理旧 Claude 状态。
```
