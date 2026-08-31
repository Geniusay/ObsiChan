[CmdletBinding()]
param(
    [switch]$Check,
    [string]$TargetPath = (Join-Path $env:USERPROFILE '.codex\skills\g-ark')
)

$ErrorActionPreference = 'Stop'
$sourcePath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$targetFullPath = [System.IO.Path]::GetFullPath($TargetPath)

if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
    throw "G-Ark skill source does not exist: $sourcePath"
}

$existing = Get-Item -LiteralPath $targetFullPath -Force -ErrorAction SilentlyContinue
if ($null -ne $existing) {
    $linkTarget = $existing.Target
    if ($linkTarget -is [array]) {
        $linkTarget = $linkTarget[0]
    }

    $resolvedTarget = if ($linkTarget) {
        [System.IO.Path]::GetFullPath($linkTarget)
    } else {
        $null
    }

    if ($existing.LinkType -eq 'Junction' -and $resolvedTarget -eq $sourcePath) {
        Write-Output "OK: $targetFullPath -> $sourcePath"
        exit 0
    }

    Write-Error "Target already exists and is not the expected junction: $targetFullPath"
    exit 1
}

if ($Check) {
    Write-Error "Global G-Ark skill junction is missing: $targetFullPath"
    exit 1
}

$parentPath = Split-Path -Parent $targetFullPath
if (-not (Test-Path -LiteralPath $parentPath -PathType Container)) {
    New-Item -ItemType Directory -Path $parentPath | Out-Null
}

New-Item -ItemType Junction -Path $targetFullPath -Target $sourcePath | Out-Null
Write-Output "Installed: $targetFullPath -> $sourcePath"
