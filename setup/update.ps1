param(
  [string]$VaultPath = "$HOME\Documents\G-Ark",
  [string]$Branch = "main",
  [string]$RepoRawBase = "https://raw.githubusercontent.com/Geniusay/ObsiChan",
  [string]$ClaudianVersion = "2.0.11",
  [switch]$UpdateClaudian
)

$ErrorActionPreference = "Stop"

function Write-Info {
  param([string]$Message)
  Write-Host "[ObsiChan Update] $Message"
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
  Invoke-WebRequest -Uri $Url -OutFile $OutFile -Headers @{ "User-Agent" = "ObsiChan-Updater" }
}

$VaultPath = [System.IO.Path]::GetFullPath($VaultPath)
$RawBase = "$RepoRawBase/$Branch"

if (-not (Test-Path -LiteralPath $VaultPath)) {
  throw "Vault path does not exist: $VaultPath"
}

Write-Info "Updating vault-level Codex skills in $VaultPath"

foreach ($skill in @("g-ark-vault-steward", "g-ark-source-distiller")) {
  $skillDir = Join-Path $VaultPath ".codex\skills\$skill"
  New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
  Download-File -Url "$RawBase/setup/skills/$skill/SKILL.md" -OutFile (Join-Path $skillDir "SKILL.md")
  Write-Info "Updated $skill"
}

$collectionsDir = Join-Path $VaultPath "20_Sources\Collections"
if (-not (Test-Path -LiteralPath $collectionsDir)) {
  New-Item -ItemType Directory -Path $collectionsDir -Force | Out-Null
  Write-Info "Created 20_Sources\Collections for resource-list sources"
}

if ($UpdateClaudian) {
  Write-Info "Updating Claudian plugin to $ClaudianVersion"
  $pluginDir = Join-Path $VaultPath ".obsidian\plugins\claudian"
  $claudianBase = "https://github.com/YishenTu/claudian/releases/download/$ClaudianVersion"
  Download-File -Url "$claudianBase/main.js" -OutFile (Join-Path $pluginDir "main.js")
  Download-File -Url "$claudianBase/manifest.json" -OutFile (Join-Path $pluginDir "manifest.json")
  Download-File -Url "$claudianBase/styles.css" -OutFile (Join-Path $pluginDir "styles.css")
}

Write-Info "Done. Restart Obsidian or refresh Claudian Codex Skills."
