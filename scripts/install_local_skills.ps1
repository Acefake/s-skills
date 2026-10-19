$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$sourceRoot = Join-Path $repoRoot 'plugins/s/skills'
$destinationRoot = Join-Path $repoRoot '.agents/skills'
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
Copy-Item -LiteralPath (Join-Path $repoRoot 'plugins/s/HOSTS.md') -Destination (Join-Path $repoRoot '.agents/HOSTS.md')
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'plugins/s') -File | Where-Object { $_.Name -like 'LICENSE*' -or $_.Name -like 'NOTICE*' } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path (Join-Path $repoRoot '.agents') $_.Name)
}
Write-Output "Linked $($skills.Count) skills from $sourceRoot. Open a new project session to discover them."
