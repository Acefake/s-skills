param(
    [ValidateSet('codex')]
    [string]$HostName = 'codex'
)

$ErrorActionPreference = 'Stop'

# 只认指向本仓库旧插件目录（改名前的 s-atlas、s-wukong）的 Junction；其他目录一律不碰。
function Test-IsLegacySkillJunction {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string[]]$LegacyRoots
    )
    if ($Item.LinkType -ne 'Junction') {
        return $false
    }
    $rawTarget = @($Item.Target) | Where-Object { $_ } | Select-Object -First 1
    if (-not $rawTarget) {
        return $false
    }
    $normalizedTarget = ([System.IO.Path]::GetFullPath([string]$rawTarget)).TrimEnd('\')
    foreach ($legacyRoot in $LegacyRoots) {
        $prefix = ([System.IO.Path]::GetFullPath($legacyRoot)).TrimEnd('\') + '\'
        if ($normalizedTarget.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

# 指向本仓库当前技能目录、但技能已被删除的 Junction：目标不存在才算。
function Test-IsRemovedSkillJunction {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$SourceRoot
    )
    if ($Item.LinkType -ne 'Junction') {
        return $false
    }
    $rawTarget = @($Item.Target) | Where-Object { $_ } | Select-Object -First 1
    if (-not $rawTarget) {
        return $false
    }
    $normalizedTarget = ([System.IO.Path]::GetFullPath([string]$rawTarget)).TrimEnd('\')
    $prefix = ([System.IO.Path]::GetFullPath($SourceRoot)).TrimEnd('\') + '\'
    return $normalizedTarget.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) -and -not (Test-Path -LiteralPath $normalizedTarget)
}

$repoRoot = Split-Path $PSScriptRoot -Parent
$sourceRoot = Join-Path $repoRoot 'plugins/wukong/skills'
$legacySourceRoots = @(
    (Join-Path $repoRoot 'plugins\s-atlas\skills'),
    (Join-Path $repoRoot 'plugins\s-wukong\skills')
)
$adapterDirectory = '.agents'
$adapterRoot = Join-Path $repoRoot $adapterDirectory
$destinationRoot = Join-Path $adapterRoot 'skills'
$commonFiles = @((Get-Item -LiteralPath (Join-Path $repoRoot 'plugins/wukong/HOSTS.md')))
$commonFiles += @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'plugins/wukong') -File | Where-Object {
    $_.Name -like 'LICENSE*' -or $_.Name -like 'NOTICE*'
})
New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
$skills = Get-ChildItem -LiteralPath $sourceRoot -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }
# Validate every destination before creating or migrating any links.
foreach ($skill in $skills) {
    $destination = Join-Path $destinationRoot $skill.Name
    if (Test-Path -LiteralPath $destination) {
        $existing = Get-Item -LiteralPath $destination -Force
        $isCurrent = $existing.LinkType -eq 'Junction' -and [string]$existing.Target -eq $skill.FullName
        $isLegacy = Test-IsLegacySkillJunction -Item $existing -LegacyRoots $legacySourceRoots
        if (-not ($isCurrent -or $isLegacy)) {
            throw "Destination belongs to another installation: $destination"
        }
    }
}
foreach ($entry in @(Get-ChildItem -LiteralPath $destinationRoot -Force)) {
    if ((Test-IsLegacySkillJunction -Item $entry -LegacyRoots $legacySourceRoots) -or (Test-IsRemovedSkillJunction -Item $entry -SourceRoot $sourceRoot)) {
        [System.IO.Directory]::Delete($entry.FullName, $false)
    }
}
foreach ($skill in $skills) {
    $destination = Join-Path $destinationRoot $skill.Name
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Junction -Path $destination -Target $skill.FullName | Out-Null
    }
}
foreach ($sourceFile in $commonFiles) {
    Copy-Item -LiteralPath $sourceFile.FullName -Destination (Join-Path $adapterRoot $sourceFile.Name)
}
Write-Output "Linked $($skills.Count) skills for $HostName from $sourceRoot to $destinationRoot. Open a new project session to discover them."
