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

Write-Info "Updating the unified G-Ark Codex skill in $VaultPath"

$garkRoot = Join-Path $VaultPath ".gark"
$skillRoot = Join-Path $garkRoot "skill"
$skillFiles = @(
  "SKILL.md",
  "agents/openai.yaml",
  "references/archive.md",
  "references/audit.md",
  "references/capture.md",
  "references/connect.md",
  "references/distill.md",
  "references/retrieve.md",
  "references/review.md",
  "references/session.md",
  "references/write-safety.md",
  "scripts/gark.py",
  "scripts/install-global.ps1"
)
foreach ($relativePath in $skillFiles) {
  $localPath = $relativePath.Replace("/", "\")
  Download-File -Url "$RawBase/setup/skills/g-ark/$relativePath" -OutFile (Join-Path $skillRoot $localPath)
}
Write-Info "Updated g-ark"

$configPath = Join-Path $garkRoot "config.toml"
if (-not (Test-Path -LiteralPath $configPath)) {
  Download-File -Url "$RawBase/setup/gark/config.toml" -OutFile $configPath
  Write-Info "Created the default relative .gark\config.toml"
}

$schemaPath = Join-Path $VaultPath "00_System\GARK_SCHEMA.json"
if (-not (Test-Path -LiteralPath $schemaPath)) {
  Download-File -Url "$RawBase/setup/gark/GARK_SCHEMA.json" -OutFile $schemaPath
  Write-Info "Installed the canonical GARK_SCHEMA.json"
}

$skillsDir = Join-Path $VaultPath ".codex\skills"
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
$skillLink = Join-Path $skillsDir "g-ark"
if (-not (Test-Path -LiteralPath $skillLink)) {
  New-Item -ItemType Junction -Path $skillLink -Target $skillRoot | Out-Null
} else {
  $existingLink = Get-Item -Force -LiteralPath $skillLink
  if (-not $existingLink.LinkType) {
    throw "Cannot enable g-ark because a non-link path already exists: $skillLink"
  }
  Remove-Item -Force -LiteralPath $skillLink
  New-Item -ItemType Junction -Path $skillLink -Target $skillRoot | Out-Null
}

$legacyRoot = Join-Path $garkRoot "legacy-skills"
foreach ($legacyName in @("g-ark-vault-steward", "g-ark-source-distiller", "g-ark-session-distiller")) {
  $legacyPath = Join-Path $skillsDir $legacyName
  if (Test-Path -LiteralPath $legacyPath) {
    New-Item -ItemType Directory -Path $legacyRoot -Force | Out-Null
    $backupPath = Join-Path $legacyRoot $legacyName
    if (Test-Path -LiteralPath $backupPath) {
      Write-Warning "Legacy backup already exists; leaving $legacyName unchanged."
    } else {
      Move-Item -LiteralPath $legacyPath -Destination $backupPath
      Write-Info "Disabled legacy skill $legacyName and preserved it under .gark\legacy-skills"
    }
  }
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

Write-Info "Done. Existing configuration was preserved. Restart Obsidian or refresh Claudian Codex Skills."
