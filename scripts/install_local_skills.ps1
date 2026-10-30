param(
    [ValidateSet('codex', 'workbuddy')]
    [string]$HostName = 'codex'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$sourceRoot = Join-Path $repoRoot 'plugins/s-atlas/skills'
$adapterDirectory = if ($HostName -eq 'workbuddy') { '.codebuddy' } else { '.agents' }
$adapterRoot = Join-Path $repoRoot $adapterDirectory
$destinationRoot = Join-Path $adapterRoot 'skills'
$commonFiles = @((Get-Item -LiteralPath (Join-Path $repoRoot 'plugins/s-atlas/HOSTS.md')))
$commonFiles += @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'plugins/s-atlas') -File | Where-Object {
    $_.Name -like 'LICENSE*' -or $_.Name -like 'NOTICE*'
})
if ($HostName -eq 'workbuddy') {
    $ownershipPath = Join-Path $adapterRoot '.s-atlas-common-files.json'
    $ownership = $null
    if (Test-Path -LiteralPath $ownershipPath) {
        $ownership = Get-Content -LiteralPath $ownershipPath -Raw | ConvertFrom-Json
        if ($ownership.schema -ne 1 -or -not $ownership.files) {
            throw "Invalid installation record: $ownershipPath"
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
# Validate every destination before creating any links.
foreach ($skill in $skills) {
    $destination = Join-Path $destinationRoot $skill.Name
    if (Test-Path -LiteralPath $destination) {
        $existing = Get-Item -LiteralPath $destination -Force
        if ($existing.LinkType -ne 'Junction' -or [string]$existing.Target -ne $skill.FullName) {
            throw "Destination belongs to another installation: $destination"
        }
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
