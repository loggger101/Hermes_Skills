<#
.SYNOPSIS
    Make this repo's skills available to Claude Code everywhere on this machine.

.DESCRIPTION
    Claude Code auto-loads every directory under ~/.claude/skills/ as a plugin
    (source: <name>@skills-dir). This script points one junction there at this
    repo, so all 199 exposed skills load in every Claude Code session, in every
    project, with the repo staying the single source of truth -- `git pull` is
    immediately live, because nothing is copied.

    Requires .claude-plugin/plugin.json, which lists the nested skill paths.
    Regenerate it after adding or renaming skills:

        py tools/gen-claude-plugin.py

    A directory junction is used rather than a symlink because junctions need no
    administrator rights and no Developer Mode on Windows.

.PARAMETER Uninstall
    Remove the junction. The repo itself is never touched.

.PARAMETER Force
    Replace whatever currently sits at the install path, including a real
    directory. Without this, an existing real directory is left alone.

.EXAMPLE
    py tools/gen-claude-plugin.py; powershell -File tools/install-claude-code.ps1

.NOTES
    Restart Claude Code (or start a new session) after running -- skills are
    loaded once at session start.
#>
[CmdletBinding()]
param(
    [switch]$Uninstall,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$SkillsDir = Join-Path $env:USERPROFILE '.claude\skills'
$LinkPath  = Join-Path $SkillsDir 'hermes'

# Removing a junction needs the reparse-point-only delete. Remove-Item -Recurse
# on a junction in Windows PowerShell 5.1 can follow the link and delete the
# TARGET's contents -- here that would be the repo itself. Never use it.
function Remove-Junction([string]$Path) {
    [System.IO.Directory]::Delete($Path, $false)
}

function Get-LinkTarget([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if (-not ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { return $null }
    if ($item.PSObject.Properties.Name -contains 'Target' -and $item.Target) {
        return @($item.Target)[0]
    }
    # PS 5.1 fallback: parse `dir` output for the [target] suffix.
    $line = (cmd /c dir /al (Split-Path -Parent $Path) 2>$null) |
            Where-Object { $_ -match [regex]::Escape((Split-Path -Leaf $Path)) }
    if ($line -match '\[(.+)\]') { return $Matches[1] }
    return $null
}

if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $LinkPath)) {
        Write-Host "[OK] nothing installed at $LinkPath"
        exit 0
    }
    if (Get-LinkTarget $LinkPath) {
        Remove-Junction $LinkPath
        Write-Host "[OK] removed junction $LinkPath (repo untouched)"
    } else {
        Write-Host "[SKIP] $LinkPath is a real directory, not our junction. Remove it yourself if intended."
        exit 1
    }
    Write-Host "      Restart Claude Code to drop the skills from new sessions."
    exit 0
}

$manifest = Join-Path $RepoRoot '.claude-plugin\plugin.json'
if (-not (Test-Path -LiteralPath $manifest)) {
    Write-Host "[FATAL] $manifest is missing. Run: py tools/gen-claude-plugin.py"
    exit 1
}
$skillCount = (Get-Content -Raw -LiteralPath $manifest | ConvertFrom-Json).skills.Count

if (-not (Test-Path -LiteralPath $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

if (Test-Path -LiteralPath $LinkPath) {
    $target = Get-LinkTarget $LinkPath
    if ($target -and ($target.TrimEnd('\') -ieq $RepoRoot.TrimEnd('\'))) {
        Write-Host "[OK] already installed: $LinkPath -> $RepoRoot"
        Write-Host "     $skillCount skills exposed. Nothing to do."
        exit 0
    }
    if ($target) {
        Remove-Junction $LinkPath          # stale junction, points somewhere else
    } elseif ($Force) {
        Remove-Item -LiteralPath $LinkPath -Recurse -Force   # safe: proven not a link
    } else {
        Write-Host "[FATAL] $LinkPath exists and is a real directory, not a junction."
        Write-Host "        Re-run with -Force to replace it, or move it aside first."
        exit 1
    }
}

New-Item -ItemType Junction -Path $LinkPath -Target $RepoRoot | Out-Null
Write-Host "[OK] installed: $LinkPath -> $RepoRoot"
Write-Host "     $skillCount skills will load as hermes@skills-dir."
Write-Host "     Restart Claude Code (new session) to pick them up."
