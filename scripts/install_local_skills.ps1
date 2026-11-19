param(
    [ValidateSet('codex', 'workbuddy')]
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

$repoRoot = Split-Path $PSScriptRoot -Parent
$sourceRoot = Join-Path $repoRoot 'plugins/wukong/skills'
$legacySourceRoots = @(
    (Join-Path $repoRoot 'plugins\s-atlas\skills'),
    (Join-Path $repoRoot 'plugins\s-wukong\skills')
)
$adapterDirectory = if ($HostName -eq 'workbuddy') { '.codebuddy' } else { '.agents' }
$adapterRoot = Join-Path $repoRoot $adapterDirectory
$destinationRoot = Join-Path $adapterRoot 'skills'
$commonFiles = @((Get-Item -LiteralPath (Join-Path $repoRoot 'plugins/wukong/HOSTS.md')))
$commonFiles += @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'plugins/wukong') -File | Where-Object {
    $_.Name -like 'LICENSE*' -or $_.Name -like 'NOTICE*'
})
if ($HostName -eq 'workbuddy') {
    $ownershipPath = Join-Path $adapterRoot '.wukong-common-files.json'
    $legacyOwnershipPath = Join-Path $adapterRoot '.s-atlas-common-files.json'
    $previousOwnershipPath = Join-Path $adapterRoot '.s-wukong-common-files.json'
    $ownership = $null
    $recordPath = $ownershipPath
    if (-not (Test-Path -LiteralPath $ownershipPath) -and (Test-Path -LiteralPath $previousOwnershipPath)) {
        $recordPath = $previousOwnershipPath
    } elseif (-not (Test-Path -LiteralPath $ownershipPath) -and (Test-Path -LiteralPath $legacyOwnershipPath)) {
        $recordPath = $legacyOwnershipPath
    }
    if (Test-Path -LiteralPath $recordPath) {
        $ownership = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
        if ($ownership.schema -ne 1 -or -not $ownership.files) {
            throw "Invalid installation record: $recordPath"
        }
    }
    foreach ($sourceFile in $commonFiles) {
        $existingFile = Join-Path $adapterRoot $sourceFile.Name
        if (Test-Path -LiteralPath $existingFile) {
            $actualHash = (Get-FileHash -LiteralPath $existingFile).Hash
            $recordedHash = if ($ownership) { $ownership.files.PSObject.Properties[$sourceFile.Name].Value } else { $null }
            if ($actualHash -ne (Get-FileHash -LiteralPath $sourceFile.FullName).Hash -and $actualHash -ne $recordedHash) {
                throw "Existing file differs; reconcile it before installing: $existingFile"
            }
        }
    }
}
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
    if (Test-IsLegacySkillJunction -Item $entry -LegacyRoots $legacySourceRoots) {
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
if ($HostName -eq 'workbuddy') {
    $hashes = [ordered]@{}
    foreach ($sourceFile in $commonFiles) {
        $hashes[$sourceFile.Name] = (Get-FileHash -LiteralPath $sourceFile.FullName).Hash
    }
    $record = @{ schema = 1; files = $hashes } | ConvertTo-Json -Depth 4
    $temporaryPath = "$ownershipPath.$([guid]::NewGuid().ToString('N')).tmp"
    try {
        [System.IO.File]::WriteAllText($temporaryPath, $record, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $temporaryPath -Destination $ownershipPath -Force
    } finally {
        if (Test-Path -LiteralPath $temporaryPath) { Remove-Item -LiteralPath $temporaryPath }
    }
}
Write-Output "Linked $($skills.Count) skills for $HostName from $sourceRoot to $destinationRoot. Open a new project session to discover them."
