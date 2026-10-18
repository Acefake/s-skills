# 安装逻辑都在这个文件里。请运行 install.ps1，或双击仓库根目录的「安装技能.cmd」。
# 这个文件按 Windows PowerShell 5.1 来写：不用 PowerShell 7 才有的语法。
# 技能正文不会在这里被修改，脚本只复制文件夹。

Set-StrictMode -Version 2.0

$script:SSkillsRepoWeb = "https://github.com/Acefake/s-skills"

function ConvertTo-SSkillsArray {
    param($Value)
    if ($null -eq $Value) {
        return @()
    }
    if ($Value -is [string]) {
        return @($Value)
    }
    $items = @()
    foreach ($item in @($Value)) {
        if ($null -ne $item) {
            $items += $item
        }
    }
    return $items
}

function Get-SSkillsSkillNames {
    param($Value)
    $names = @()
    foreach ($item in @(ConvertTo-SSkillsArray $Value)) {
        if ($item -is [string]) {
            $names += $item
        }
        else {
            $names += [string]$item.name
        }
    }
    return $names
}

function Read-SSkillsJson {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $text = [System.Text.Encoding]::UTF8.GetString($bytes)
    if ($text.Length -gt 0 -and [int][char]$text[0] -eq 0xFEFF) {
        $text = $text.Substring(1)
    }
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }
    return ($text | ConvertFrom-Json)
}

function Write-SSkillsJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object
    )
    $json = $Object | ConvertTo-Json -Depth 8
    $utf8 = New-Object System.Text.UTF8Encoding $false
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $tmp = $Path + ".tmp"
    [System.IO.File]::WriteAllText($tmp, $json + "`n", $utf8)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
    Move-Item -LiteralPath $tmp -Destination $Path
}

function Join-SSkillsRepoPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )
    $current = $Root
    foreach ($part in @($RelativePath -split '[\\/]+')) {
        if ($part -eq "" -or $part -eq ".") {
            continue
        }
        if ($part -eq "..") {
            throw "路径里不能有 .. ：$RelativePath"
        }
        $current = Join-Path $current $part
    }
    return $current
}

function Get-SSkillsManifest {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    $path = Join-Path $RepoRoot "skills.json"
    $raw = Read-SSkillsJson $path
    if ($null -eq $raw) {
        throw "找不到技能清单 skills.json：$path"
    }
    $groups = @()
    foreach ($g in @(ConvertTo-SSkillsArray $raw.groups)) {
        $groups += [pscustomobject]@{
            Id           = [string]$g.id
            Title        = [string]$g.title
            Summary      = [string]$g.summary
            Path         = [string]$g.path
            License      = [string]$g.license
            LicenseFiles = @(Get-SSkillsSkillNames $g.licenseFiles)
            Skills       = @(Get-SSkillsSkillNames $g.skills)
        }
    }
    if ($groups.Count -eq 0) {
        throw "skills.json 里没有任何分组。"
    }
    return [pscustomobject]@{
        Schema        = $raw.schema
        Repo          = [string]$raw.repo
        DefaultGroups = @(Get-SSkillsSkillNames $raw.defaultGroups)
        Groups        = $groups
        Path          = $path
    }
}

function Get-SSkillsIndex {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)]$Manifest
    )
    $byName = @{}
    foreach ($g in @($Manifest.Groups)) {
        $groupDir = Join-SSkillsRepoPath -Root $RepoRoot -RelativePath $g.Path
        if (-not (Test-Path -LiteralPath $groupDir)) {
            throw "分组文件夹不存在：$($g.Path)"
        }
        $found = @()
        foreach ($dir in @(Get-ChildItem -LiteralPath $groupDir -Force -Directory)) {
            if ($null -eq $dir) { continue }
            $skillMd = Join-Path $dir.FullName "SKILL.md"
            if (Test-Path -LiteralPath $skillMd) {
                $found += $dir.Name
            }
        }
        $expected = @($g.Skills)
        $foundKey = ((@($found | Sort-Object)) -join "`n")
        $expectedKey = ((@($expected | Sort-Object)) -join "`n")
        if ($foundKey -ne $expectedKey) {
            throw "分组 $($g.Id) 的文件夹和 skills.json 不一致。请不要只改其中一边。"
        }
        foreach ($licenseName in @($g.LicenseFiles)) {
            $licensePath = Join-Path $groupDir $licenseName
            if (-not (Test-Path -LiteralPath $licensePath -PathType Leaf)) {
                throw "找不到许可证文件：$($g.Path)/$licenseName"
            }
        }
        foreach ($name in $expected) {
            if ($name -match '[\\/]' -or $name -eq "." -or $name -eq ".." -or [string]::IsNullOrWhiteSpace($name)) {
                throw "技能名字不合法：$name"
            }
            if ($byName.ContainsKey($name)) {
                throw "有两个技能都叫：$name"
            }
            $full = Join-Path $groupDir $name
            $byName[$name] = [pscustomobject]@{
                Name      = $name
                Group     = $g.Id
                SourceRel = ($g.Path.TrimEnd('/', '\') + "/" + $name)
                FullPath  = $full
            }
        }
    }
    return $byName
}

function Resolve-SSkillsGroups {
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [string]$Text
    )
    $all = @($Manifest.Groups)
    $byId = @{}
    foreach ($g in $all) {
        $byId[$g.Id] = $g
    }
    $trimmed = ""
    if ($null -ne $Text) {
        $trimmed = $Text.Trim()
    }
    $ids = @()
    if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed -eq "default" -or $trimmed -eq "默认") {
        $ids = @($Manifest.DefaultGroups)
    }
    elseif ($trimmed -eq "all" -or $trimmed -eq "全部" -or $trimmed -eq "*") {
        return $all
    }
    else {
        foreach ($part in @($trimmed -split '[,\s，、;；]+')) {
            if (-not [string]::IsNullOrWhiteSpace($part)) {
                $ids += $part.Trim()
            }
        }
    }
    if ($ids.Count -eq 0) {
        throw "没有选出任何分组。"
    }
    $picked = @()
    $seen = @{}
    foreach ($id in $ids) {
        if (-not $byId.ContainsKey($id)) {
            $known = ((@($all | ForEach-Object { $_.Id })) -join "、")
            throw "不认识的分组：$id。可以填这些英文 id：$known。全部请填 all。"
        }
        if (-not $seen.ContainsKey($id)) {
            $seen[$id] = $true
            $picked += $byId[$id]
        }
    }
    return $picked
}

function Get-SSkillsUserProfile {
    param([string]$Override)
    if (-not [string]::IsNullOrWhiteSpace($Override)) {
        return $Override
    }
    if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
        return $env:USERPROFILE
    }
    if (-not [string]::IsNullOrWhiteSpace($env:HOME)) {
        return $env:HOME
    }
    $folder = [Environment]::GetFolderPath("UserProfile")
    if ([string]::IsNullOrWhiteSpace($folder)) {
        throw "找不到你的用户文件夹。请用 -UserProfile 指定。"
    }
    return $folder
}

function Get-SSkillsDataRoot {
    param(
        [string]$Override,
        [Parameter(Mandatory = $true)][string]$UserProfile
    )
    if (-not [string]::IsNullOrWhiteSpace($Override)) {
        return $Override
    }
    if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        return (Join-Path $env:LOCALAPPDATA "s-skills")
    }
    return (Join-Path (Join-Path (Join-Path $UserProfile ".local") "share") "s-skills")
}

function Test-SSkillsAnyPath {
    param([string[]]$Paths)
    foreach ($path in @($Paths)) {
        if (-not [string]::IsNullOrWhiteSpace($path) -and (Test-Path -LiteralPath $path)) {
            return $true
        }
    }
    return $false
}

function Get-SSkillsKnownTargets {
    param([Parameter(Mandatory = $true)][string]$UserProfile)
    $defs = @(
        @{
            Id = "workbuddy"
            Title = "WorkBuddy"
            Skills = (Join-Path (Join-Path $UserProfile ".workbuddy") "skills")
            Detect = @((Join-Path $UserProfile ".workbuddy"))
            DefaultWhenDetected = $true
            Note = "腾讯云社区文章，以及 WorkBuddy 自带的「创建技能」示例，用的是这个文件夹。官方技能市场页面没有写死完整路径。"
        },
        @{
            Id = "codebuddy"
            Title = "CodeBuddy（WorkBuddy 文档里的引擎目录）"
            Skills = (Join-Path (Join-Path $UserProfile ".codebuddy") "skills")
            Detect = @((Join-Path $UserProfile ".codebuddy"))
            DefaultWhenDetected = $true
            Note = "workbuddy.cn 上 CodeBuddy 的说明写的用户技能目录是这个。WorkBuddy 和 CodeBuddy 共用引擎时会读到。没检测到这个文件夹就不会默认安装。"
        },
        @{
            Id = "cursor"
            Title = "Cursor"
            Skills = (Join-Path (Join-Path $UserProfile ".cursor") "skills")
            Detect = @((Join-Path $UserProfile ".cursor"))
            DefaultWhenDetected = $true
            Note = "Cursor 官方文档写的用户技能目录。文档也说 Cursor 还会顺便读取 Claude、Codex 的技能文件夹。"
        },
        @{
            Id = "codex"
            Title = "Codex（现行目录）"
            Skills = (Join-Path (Join-Path $UserProfile ".agents") "skills")
            Detect = @((Join-Path $UserProfile ".codex"))
            DefaultWhenDetected = $true
            Note = "OpenAI 现在的说明把用户技能放在这里。检测到 Codex 的配置文件夹 .codex 时，默认装到这个现行目录。"
        },
        @{
            Id = "codex-legacy"
            Title = "Codex（旧目录）"
            Skills = (Join-Path (Join-Path $UserProfile ".codex") "skills")
            Detect = @((Join-Path $UserProfile ".codex"))
            DefaultWhenDetected = $false
            Note = "旧位置。OpenAI 说它已被现行目录取代，但旧版本和 npx skills 仍会用它。和现行目录一起装，可能看到两份一样的技能，所以默认不装。"
        },
        @{
            Id = "opencode"
            Title = "OpenCode"
            Skills = (Join-Path (Join-Path (Join-Path $UserProfile ".config") "opencode") "skills")
            Detect = @((Join-Path (Join-Path $UserProfile ".config") "opencode"))
            DefaultWhenDetected = $true
            Note = "OpenCode 官方文档写的全局技能目录。在 Windows 上就是你的用户文件夹下的 .config\opencode\skills。"
        },
        @{
            Id = "claude"
            Title = "Claude Code"
            Skills = (Join-Path (Join-Path $UserProfile ".claude") "skills")
            Detect = @((Join-Path $UserProfile ".claude"))
            DefaultWhenDetected = $true
            Note = "Claude Code 官方文档写的个人技能目录。在 Windows 上，~ 就是你的用户文件夹。"
        }
    )
    $targets = @()
    foreach ($def in $defs) {
        $detected = Test-SSkillsAnyPath -Paths $def.Detect
        $targets += [pscustomobject]@{
            Id              = $def.Id
            Title           = $def.Title
            Skills          = $def.Skills
            Detect          = $def.Detect
            Detected        = $detected
            DefaultSelected = ($detected -and $def.DefaultWhenDetected)
            Note            = $def.Note
        }
    }
    return $targets
}

function Resolve-SSkillsTargets {
    param(
        [Parameter(Mandatory = $true)]$Known,
        [string]$Text
    )
    $all = @($Known)
    $trimmed = ""
    if ($null -ne $Text) {
        $trimmed = $Text.Trim()
    }
    if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed -eq "detected" -or $trimmed -eq "默认") {
        $picked = @()
        foreach ($target in $all) {
            if ($target.DefaultSelected) {
                $picked += $target
            }
        }
        return $picked
    }
    if ($trimmed -eq "all" -or $trimmed -eq "全部" -or $trimmed -eq "*") {
        return $all
    }
    $tokens = @()
    foreach ($part in @($trimmed -split '[,\s，、;；]+')) {
        if (-not [string]::IsNullOrWhiteSpace($part)) {
            $tokens += $part.Trim()
        }
    }
    $picked = @()
    $seen = @{}
    foreach ($token in $tokens) {
        $hit = $null
        if ($token -match '^[0-9]+$') {
            $number = [int]$token
            if ($number -ge 1 -and $number -le $all.Count) {
                $hit = $all[$number - 1]
            }
        }
        if ($null -eq $hit) {
            foreach ($target in $all) {
                if ($target.Id -eq $token) {
                    $hit = $target
                    break
                }
            }
        }
        if ($null -eq $hit) {
            $ids = ((@($all | ForEach-Object { $_.Id })) -join "、")
            throw "不认识的安装位置：$token。可以填编号，或这些英文 id：$ids。"
        }
        if (-not $seen.ContainsKey($hit.Id)) {
            $seen[$hit.Id] = $true
            $picked += $hit
        }
    }
    return $picked
}

function Get-SSkillsInstalled {
    param([Parameter(Mandatory = $true)][string]$SkillsDir)
    $path = Join-Path $SkillsDir "s-skills-installed.json"
    $state = @{
        Skills = @{}
        Files  = @{}
        Path   = $path
    }
    if (-not (Test-Path -LiteralPath $path)) {
        return $state
    }
    $raw = Read-SSkillsJson $path
    if ($null -eq $raw) {
        return $state
    }
    $schema = 0
    if ($raw.PSObject.Properties.Name -contains "schema") {
        $schema = [int]$raw.schema
    }
    if ($schema -ne 1) {
        throw "安装清单的版本不是 1，脚本停下来了，没有删除任何技能：$path"
    }
    $manager = ""
    if ($raw.PSObject.Properties.Name -contains "manager") {
        $manager = [string]$raw.manager
    }
    if ($manager -ne "s-skills") {
        throw "这个清单不是本脚本写的，脚本停下来了，没有删除任何技能：$path"
    }
    if ($raw.PSObject.Properties.Name -contains "skills" -and $null -ne $raw.skills) {
        foreach ($property in @($raw.skills.PSObject.Properties)) {
            $state.Skills[$property.Name] = @{
                group  = [string]$property.Value.group
                source = [string]$property.Value.source
            }
        }
    }
    if ($raw.PSObject.Properties.Name -contains "files" -and $null -ne $raw.files) {
        foreach ($property in @($raw.files.PSObject.Properties)) {
            $state.Files[$property.Name] = @{
                source = [string]$property.Value.source
            }
        }
    }
    return $state
}

function Save-SSkillsInstalled {
    param(
        [Parameter(Mandatory = $true)]$State,
        [Parameter(Mandatory = $true)][string]$RepoUrl
    )
    $skills = [ordered]@{}
    foreach ($name in @($State.Skills.Keys | Sort-Object)) {
        $skills[$name] = [ordered]@{
            group  = [string]$State.Skills[$name].group
            source = [string]$State.Skills[$name].source
        }
    }
    $files = [ordered]@{}
    foreach ($name in @($State.Files.Keys | Sort-Object)) {
        $files[$name] = [ordered]@{
            source = [string]$State.Files[$name].source
        }
    }
    $root = [ordered]@{
        schema    = 1
        manager   = "s-skills"
        repo      = $RepoUrl
        updatedAt = ([DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss") + "Z")
        skills    = $skills
        files     = $files
    }
    Write-SSkillsJson -Path $State.Path -Object $root
}

function Get-SSkillsFingerprint {
    param([Parameter(Mandatory = $true)][string]$Root)
    $resolved = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\', '/')
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $utf8 = New-Object System.Text.UTF8Encoding $false
    try {
        $lines = New-Object System.Collections.Generic.List[string]
        foreach ($item in @(Get-ChildItem -LiteralPath $resolved -Recurse -File -Force)) {
            if ($null -eq $item) { continue }
            $relative = $item.FullName.Substring($resolved.Length).TrimStart('\', '/').Replace('\', '/')
            $hash = [System.BitConverter]::ToString($sha.ComputeHash([System.IO.File]::ReadAllBytes($item.FullName))).Replace("-", "").ToLower()
            $lines.Add($relative + ":" + $hash)
        }
        $sorted = @($lines | Sort-Object)
        $text = $sorted -join "`n"
        $sha2 = [System.Security.Cryptography.SHA256]::Create()
        try {
            return ([System.BitConverter]::ToString($sha2.ComputeHash($utf8.GetBytes($text))).Replace("-", "").ToLower())
        }
        finally {
            $sha2.Dispose()
        }
    }
    finally {
        $sha.Dispose()
    }
}

function Get-SSkillsFileHash {
    param([Parameter(Mandatory = $true)][string]$Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "").ToLower())
    }
    finally {
        $sha.Dispose()
    }
}

function Copy-SSkillsTree {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "找不到要复制的文件夹：$Source"
    }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    foreach ($item in @(Get-ChildItem -LiteralPath $Source -Force)) {
        if ($null -eq $item) { continue }
        $target = Join-Path $Destination $item.Name
        if ($item.PSIsContainer) {
            Copy-SSkillsTree -Source $item.FullName -Destination $target
        }
        else {
            [System.IO.File]::Copy($item.FullName, $target, $true)
        }
    }
}

function Move-SSkillsBackup {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$BackupRoot,
        [Parameter(Mandatory = $true)][string]$Name
    )
    if (-not (Test-Path -LiteralPath $BackupRoot)) {
        New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    }
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $bag = Join-Path $BackupRoot $stamp
    if (-not (Test-Path -LiteralPath $bag)) {
        New-Item -ItemType Directory -Path $bag -Force | Out-Null
    }
    $dest = Join-Path $bag $Name
    if (Test-Path -LiteralPath $dest) {
        $dest = Join-Path $bag ($Name + "-" + [guid]::NewGuid().ToString("N").Substring(0, 6))
    }
    Move-Item -LiteralPath $Path -Destination $dest
    return $dest
}

function Publish-SSkillsPath {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string]$BackupRoot,
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [Parameter(Mandatory = $true)][bool]$Owned,
        [Parameter(Mandatory = $true)][string]$Name
    )
    $stagingParent = Join-Path $DataRoot "staging"
    if (-not (Test-Path -LiteralPath $stagingParent)) {
        New-Item -ItemType Directory -Path $stagingParent -Force | Out-Null
    }
    $staging = Join-Path $stagingParent ([guid]::NewGuid().ToString("N"))
    $backupPath = $null
    $displaced = $null
    $sourceIsDir = Test-Path -LiteralPath $Source -PathType Container
    try {
        if ($sourceIsDir) {
            Copy-SSkillsTree -Source $Source -Destination $staging
        }
        else {
            $stageParent = Split-Path -Parent $staging
            if (-not (Test-Path -LiteralPath $stageParent)) {
                New-Item -ItemType Directory -Path $stageParent -Force | Out-Null
            }
            [System.IO.File]::Copy($Source, $staging, $true)
        }
        $destParent = Split-Path -Parent $Destination
        if (-not (Test-Path -LiteralPath $destParent)) {
            New-Item -ItemType Directory -Path $destParent -Force | Out-Null
        }
        if (Test-Path -LiteralPath $Destination) {
            if ($Owned) {
                $displaced = Join-Path $stagingParent ("old-" + [guid]::NewGuid().ToString("N"))
                Move-Item -LiteralPath $Destination -Destination $displaced
            }
            else {
                $backupPath = Move-SSkillsBackup -Path $Destination -BackupRoot $BackupRoot -Name $Name
            }
        }
        Move-Item -LiteralPath $staging -Destination $Destination
        if ($null -ne $displaced -and (Test-Path -LiteralPath $displaced)) {
            Remove-Item -LiteralPath $displaced -Recurse -Force
            $displaced = $null
        }
        return $backupPath
    }
    catch {
        if ($null -ne $displaced -and (Test-Path -LiteralPath $displaced)) {
            if (Test-Path -LiteralPath $Destination) {
                Remove-Item -LiteralPath $Destination -Recurse -Force
            }
            Move-Item -LiteralPath $displaced -Destination $Destination
        }
        if ($null -ne $backupPath -and (Test-Path -LiteralPath $backupPath) -and -not (Test-Path -LiteralPath $Destination)) {
            $restoreParent = Split-Path -Parent $Destination
            if (-not (Test-Path -LiteralPath $restoreParent)) {
                New-Item -ItemType Directory -Path $restoreParent -Force | Out-Null
            }
            Move-Item -LiteralPath $backupPath -Destination $Destination
        }
        if (Test-Path -LiteralPath $staging) {
            Remove-Item -LiteralPath $staging -Recurse -Force
        }
        throw
    }
}

function Remove-SSkillsOwnedPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    Remove-Item -LiteralPath $Path -Recurse -Force
}

function Update-SSkillsTarget {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)]$RepoIndex,
        [Parameter(Mandatory = $true)]$SelectedGroups,
        [Parameter(Mandatory = $true)]$Target,
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [switch]$Preview
    )
    $result = [pscustomobject]@{
        Id        = $Target.Id
        Title     = $Target.Title
        Path      = $Target.Skills
        Added     = 0
        Updated   = 0
        Unchanged = 0
        Replaced  = 0
        Removed   = 0
        Failed    = (New-Object System.Collections.Generic.List[string])
        Backups   = (New-Object System.Collections.Generic.List[string])
    }
    $backupRoot = Join-Path (Join-Path $DataRoot "backups") $Target.Id
    $state = Get-SSkillsInstalled -SkillsDir $Target.Skills
    $selectedIds = @{}
    foreach ($group in @($SelectedGroups)) {
        $selectedIds[$group.Id] = $true
    }

    $operations = @()
    foreach ($group in @($SelectedGroups)) {
        foreach ($name in @($group.Skills)) {
            if (-not $RepoIndex.ContainsKey($name)) {
                $result.Failed.Add("清单里有「$name」，但仓库里找不到这个文件夹。")
                continue
            }
            $skill = $RepoIndex[$name]
            $dest = Join-Path $Target.Skills $name
            $owned = $state.Skills.ContainsKey($name)
            $exists = Test-Path -LiteralPath $dest
            if ($exists -and $owned) {
                $same = $false
                try {
                    $same = (Get-SSkillsFingerprint $skill.FullPath) -eq (Get-SSkillsFingerprint $dest)
                }
                catch {
                    $same = $false
                }
                if ($same) {
                    $operations += [pscustomobject]@{ Kind = "unchanged"; Name = $name; Skill = $skill; Dest = $dest }
                }
                else {
                    $operations += [pscustomobject]@{ Kind = "update"; Name = $name; Skill = $skill; Dest = $dest }
                }
            }
            elseif ($exists -and -not $owned) {
                $operations += [pscustomobject]@{ Kind = "replace"; Name = $name; Skill = $skill; Dest = $dest }
            }
            else {
                $operations += [pscustomobject]@{ Kind = "add"; Name = $name; Skill = $skill; Dest = $dest }
            }
        }
    }

    foreach ($name in @($state.Skills.Keys)) {
        $stillSelected = $false
        foreach ($op in $operations) {
            if ($op.Name -eq $name) {
                $stillSelected = $true
                break
            }
        }
        if ($stillSelected) {
            continue
        }
        if (-not $RepoIndex.ContainsKey($name)) {
            $operations += [pscustomobject]@{ Kind = "remove"; Name = $name; Skill = $null; Dest = (Join-Path $Target.Skills $name) }
            continue
        }
        $current = $RepoIndex[$name]
        $recorded = [string]$state.Skills[$name].source
        if ($recorded -ne $current.SourceRel) {
            $dest = Join-Path $Target.Skills $name
            $operations += [pscustomobject]@{ Kind = "update"; Name = $name; Skill = $current; Dest = $dest }
        }
    }

    foreach ($op in $operations) {
        try {
            if ($op.Kind -eq "unchanged") {
                $state.Skills[$op.Name] = @{ group = $op.Skill.Group; source = $op.Skill.SourceRel }
                $result.Unchanged++
                continue
            }
            if ($op.Kind -eq "remove") {
                if (-not $Preview) {
                    Remove-SSkillsOwnedPath -Path $op.Dest
                }
                $state.Skills.Remove($op.Name) | Out-Null
                $result.Removed++
                continue
            }
            $owned = $state.Skills.ContainsKey($op.Name)
            if (-not $Preview) {
                $backup = Publish-SSkillsPath -Source $op.Skill.FullPath -Destination $op.Dest -BackupRoot $backupRoot -DataRoot $DataRoot -Owned $owned -Name $op.Name
                if ($null -ne $backup) {
                    $result.Backups.Add($backup)
                }
            }
            elseif ($op.Kind -eq "replace" -and (Test-Path -LiteralPath $op.Dest)) {
                $result.Backups.Add((Join-Path $backupRoot ("预览-" + $op.Name)))
            }
            $state.Skills[$op.Name] = @{ group = $op.Skill.Group; source = $op.Skill.SourceRel }
            if ($op.Kind -eq "add") { $result.Added++ }
            elseif ($op.Kind -eq "update") { $result.Updated++ }
            elseif ($op.Kind -eq "replace") { $result.Replaced++ }
        }
        catch {
            $result.Failed.Add(("「{0}」没有装上：{1}" -f $op.Name, $_.Exception.Message))
        }
    }

    $remainingGroups = @{}
    foreach ($name in @($state.Skills.Keys)) {
        $remainingGroups[$state.Skills[$name].group] = $true
    }
    $neededFiles = @{}
    foreach ($group in @($Manifest.Groups)) {
        if (-not $remainingGroups.ContainsKey($group.Id)) {
            continue
        }
        foreach ($fileName in @($group.LicenseFiles)) {
            $neededFiles[$fileName] = (Join-SSkillsRepoPath -Root $RepoRoot -RelativePath ($group.Path.TrimEnd('/', '\') + "/" + $fileName))
        }
    }
    foreach ($fileName in @($neededFiles.Keys)) {
        try {
            $source = $neededFiles[$fileName]
            $dest = Join-Path $Target.Skills $fileName
            $owned = $state.Files.ContainsKey($fileName)
            $exists = Test-Path -LiteralPath $dest
            $sourceRel = ""
            foreach ($group in @($Manifest.Groups)) {
                foreach ($candidate in @($group.LicenseFiles)) {
                    if ($candidate -eq $fileName) {
                        $sourceRel = ($group.Path.TrimEnd('/', '\') + "/" + $fileName)
                    }
                }
            }
            if ($exists -and $owned) {
                $same = $false
                if ((Test-Path -LiteralPath $dest -PathType Leaf) -and (Test-Path -LiteralPath $source -PathType Leaf)) {
                    $same = (Get-SSkillsFileHash $source) -eq (Get-SSkillsFileHash $dest)
                }
                if ($same) {
                    $state.Files[$fileName] = @{ source = $sourceRel }
                    continue
                }
            }
            if (-not $Preview) {
                $backup = Publish-SSkillsPath -Source $source -Destination $dest -BackupRoot $backupRoot -DataRoot $DataRoot -Owned $owned -Name $fileName
                if ($null -ne $backup) {
                    $result.Backups.Add($backup)
                    $result.Replaced++
                }
            }
            elseif ($exists -and -not $owned) {
                $result.Backups.Add((Join-Path $backupRoot ("预览-" + $fileName)))
                $result.Replaced++
            }
            $state.Files[$fileName] = @{ source = $sourceRel }
        }
        catch {
            $result.Failed.Add(("许可证文件「{0}」没有复制：{1}" -f $fileName, $_.Exception.Message))
        }
    }
    foreach ($fileName in @($state.Files.Keys)) {
        if ($neededFiles.ContainsKey($fileName)) {
            continue
        }
        try {
            if (-not $Preview) {
                Remove-SSkillsOwnedPath -Path (Join-Path $Target.Skills $fileName)
            }
            $state.Files.Remove($fileName) | Out-Null
            $result.Removed++
        }
        catch {
            $result.Failed.Add(("没有删掉以前复制的「{0}」：{1}" -f $fileName, $_.Exception.Message))
        }
    }

    if (-not $Preview) {
        if (-not (Test-Path -LiteralPath $Target.Skills)) {
            New-Item -ItemType Directory -Path $Target.Skills -Force | Out-Null
        }
        Save-SSkillsInstalled -State $state -RepoUrl $script:SSkillsRepoWeb
    }
    return $result
}

function Write-SSkillsGroupMenu {
    param($Manifest)
    Write-Host ""
    Write-Host "要安装哪些分组？"
    Write-Host "技能（skill）就是一份写给 AI 的做事说明，一个文件夹，里面主要是 SKILL.md。"
    Write-Host "直接回车 = 只装默认分组 pstack（你现在常用的那一套）。"
    Write-Host "输入 all = 全部分组都装。也可以输入英文 id，用逗号分开，例如：pstack,figma,my-skills"
    Write-Host ""
    foreach ($group in @($Manifest.Groups)) {
        $mark = ""
        foreach ($id in @($Manifest.DefaultGroups)) {
            if ($id -eq $group.Id) { $mark = "  [默认]" }
        }
        Write-Host ("  {0}    {1} 个{2}" -f $group.Id, @($group.Skills).Count, $mark)
        Write-Host ("    {0}" -f $group.Summary)
    }
}

function Write-SSkillsTargetMenu {
    param($Targets)
    Write-Host ""
    Write-Host "要装进哪些软件？"
    Write-Host "直接回车 = 安装下面标了「默认」的。那些是已经检测到的软件。"
    Write-Host "输入 all = 连没检测到的软件、以及 Codex 旧目录一起装，并新建文件夹。"
    Write-Host "也可以输入编号或英文 id，用逗号分开，例如：1,5 或 cursor,opencode"
    Write-Host ""
    $index = 1
    foreach ($target in @($Targets)) {
        $flag = "未检测到"
        if ($target.Detected -and $target.DefaultSelected) {
            $flag = "默认"
        }
        elseif ($target.Detected) {
            $flag = "已检测到，默认不装"
        }
        Write-Host ("  {0}. [{1}] {2}    id={3}" -f $index, $flag, $target.Title, $target.Id)
        Write-Host ("     文件夹：{0}" -f $target.Skills)
        Write-Host ("     说明：{0}" -f $target.Note)
        $index++
    }
}

function Write-SSkillsSummary {
    param($Results, [switch]$Preview)
    Write-Host ""
    Write-Host "======== 结果 ========"
    if ($Preview) {
        Write-Host "这是预览，没有改任何文件。"
    }
    $totalFail = 0
    foreach ($result in @($Results)) {
        Write-Host ""
        Write-Host $result.Title
        Write-Host ("  位置：{0}" -f $result.Path)
        Write-Host ("  新装 {0} 个，更新 {1} 个，已是最新 {2} 个，备份后换上 {3} 个，删掉 {4} 个" -f $result.Added, $result.Updated, $result.Unchanged, $result.Replaced, $result.Removed)
        if ($result.Backups.Count -gt 0) {
            Write-Host "  备份（你原来的同名文件夹，不是这个脚本创建的，已挪走）："
            $shown = 0
            foreach ($backup in @($result.Backups)) {
                if ($shown -ge 8) { break }
                Write-Host ("    {0}" -f $backup)
                $shown++
            }
            if ($result.Backups.Count -gt 8) {
                Write-Host ("    还有 {0} 个备份没列在这里。" -f ($result.Backups.Count - 8))
            }
        }
        foreach ($failure in @($result.Failed)) {
            Write-Host ("  失败：{0}" -f $failure)
            $totalFail++
        }
    }
    Write-Host ""
    Write-Host "没有改动清单以外的文件夹。清单文件叫 s-skills-installed.json，放在每个软件的技能目录里。"
    Write-Host "许可证文件会跟技能放在同一层。技能正文写着许可证在上一级文件夹，所以要一起复制。脚本复制过的许可证也记在清单里。"
    Write-Host "以后再运行一次这个脚本，就是把你选中的分组更新到仓库里的最新版。"
    Write-Host "仓库里已经删掉、而且以前是这个脚本装上的技能，会被删掉。你自己放进去的文件夹不会动。"
    if (@($Results).Count -gt 1) {
        Write-Host ""
        Write-Host "提醒：Cursor 还会读取 Claude Code 和 Codex 的技能文件夹。OpenCode 也会读取 Claude Code 和 .agents\skills。"
        Write-Host "几个软件都装了的话，同一个技能可能在列表里出现多次。内容是一样的。如果觉得烦，下次只选一个软件。"
    }
    return $totalFail
}

function Invoke-SSkillsGit {
    param([Parameter(Mandatory = $true)][string[]]$GitArgs)
    $output = & git @GitArgs 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw ("git 失败（退出码 {0}）。命令：git {1}`n{2}" -f $LASTEXITCODE, ($GitArgs -join " "), $output.Trim())
    }
}

function Update-SSkillsCheckout {
    param(
        [Parameter(Mandatory = $true)][string]$DataRoot,
        [Parameter(Mandatory = $true)][string]$RepoUrl,
        [Parameter(Mandatory = $true)][string]$ZipUrl
    )
    if (-not (Test-Path -LiteralPath $DataRoot)) {
        New-Item -ItemType Directory -Path $DataRoot -Force | Out-Null
    }
    $errors = New-Object System.Collections.Generic.List[string]
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($null -ne $git) {
        $cache = Join-Path $DataRoot "repo"
        $previousPrompt = $env:GIT_TERMINAL_PROMPT
        $env:GIT_TERMINAL_PROMPT = "0"
        try {
            $gitDir = Join-Path $cache ".git"
            if (Test-Path -LiteralPath $gitDir) {
                Invoke-SSkillsGit -GitArgs @("-C", $cache, "remote", "set-url", "origin", $RepoUrl)
                Invoke-SSkillsGit -GitArgs @("-C", $cache, "fetch", "--depth", "1", "origin", "main")
                Invoke-SSkillsGit -GitArgs @("-C", $cache, "reset", "--hard", "origin/main")
                Invoke-SSkillsGit -GitArgs @("-C", $cache, "clean", "-fd")
            }
            else {
                if (Test-Path -LiteralPath $cache) {
                    Remove-Item -LiteralPath $cache -Recurse -Force
                }
                Invoke-SSkillsGit -GitArgs @("clone", "--depth", "1", "--branch", "main", $RepoUrl, $cache)
            }
            return (Resolve-Path -LiteralPath $cache).Path
        }
        catch {
            $errors.Add($_.Exception.Message)
        }
        finally {
            if ($null -eq $previousPrompt) {
                Remove-Item Env:GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue
            }
            else {
                $env:GIT_TERMINAL_PROMPT = $previousPrompt
            }
        }
    }
    else {
        $errors.Add("这台电脑没有 git。Git 是用来下载仓库历史的工具，装上它，中文文件夹名更不容易坏。下载地址：https://git-scm.com/download/win")
    }

    try {
        $zipPath = Join-Path $DataRoot "main.zip"
        $extract = Join-Path $DataRoot "zip-extract"
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        }
        catch {
            Write-Verbose "这台系统不能改传输加密协议，继续用原来的设置。"
        }
        $client = New-Object System.Net.WebClient
        try {
            $client.DownloadFile($ZipUrl, $zipPath)
        }
        finally {
            $client.Dispose()
        }
        Expand-SSkillsZip -ZipPath $zipPath -Destination $extract
        return (Resolve-SSkillsExtractedRoot -Destination $extract)
    }
    catch {
        $errors.Add($_.Exception.Message)
    }
    throw ("没能下载最新的仓库。`n" + ([string]::Join("`n", @($errors))))
}

function Expand-SSkillsZip {
    param(
        [Parameter(Mandatory = $true)][string]$ZipPath,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    $tar = $null
    foreach ($name in @("tar.exe", "tar")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($null -ne $cmd) {
            $tar = $cmd
            break
        }
    }
    if ($null -ne $tar) {
        & $tar.Source "-xf" $ZipPath "-C" $Destination 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            return
        }
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $Destination)
}

function Resolve-SSkillsExtractedRoot {
    param([Parameter(Mandatory = $true)][string]$Destination)
    $direct = Join-Path $Destination "skills.json"
    if (Test-Path -LiteralPath $direct) {
        return $Destination
    }
    $found = @()
    foreach ($dir in @(Get-ChildItem -LiteralPath $Destination -Force -Directory)) {
        if ($null -eq $dir) { continue }
        if (Test-Path -LiteralPath (Join-Path $dir.FullName "skills.json")) {
            $found += $dir.FullName
        }
    }
    if ($found.Count -eq 1) {
        return $found[0]
    }
    throw "解压之后找不到 skills.json。如果文件夹名变成了乱码，请安装 Git 后再运行。Git 下载地址：https://git-scm.com/download/win"
}

function Invoke-SSkillsMain {
    param(
        [string]$Groups,
        [string]$Targets,
        [string]$SourcePath,
        [string]$UserProfile,
        [string]$DataRoot,
        [string]$RepoUrl = "https://github.com/Acefake/s-skills.git",
        [string]$ZipUrl = "https://github.com/Acefake/s-skills/archive/refs/heads/main.zip",
        [string]$ScriptRoot,
        [switch]$NonInteractive,
        [switch]$Preview
    )
    try {
        try {
            [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        }
        catch {
            Write-Verbose "当前窗口不能改成 UTF-8，中文可能显示成乱码。脚本仍会按 UTF-8 读写文件。"
        }
        $OutputEncoding = New-Object System.Text.UTF8Encoding $false

        $profilePath = Get-SSkillsUserProfile -Override $UserProfile
        $data = Get-SSkillsDataRoot -Override $DataRoot -UserProfile $profilePath
        Write-Host "S 的中文技能库：安装或更新"
        Write-Host "你的用户文件夹：$profilePath"
        Write-Host "脚本用这个文件夹找各个软件，不会把某一个用户名写死在脚本里。"
        Write-Host "下载缓存和备份放在：$data"
        Write-Host "备份不放进技能文件夹，免得软件把备份又当成一份技能。"

        $repoRoot = $null
        $usedLocal = $false
        if (-not [string]::IsNullOrWhiteSpace($SourcePath)) {
            $repoRoot = $SourcePath
            Write-Host "使用指定的本地副本，不从网上重新下载：$SourcePath"
        }
        else {
            Write-Host "正在下载 GitHub 上的最新副本（公开仓库，不需要登录）……"
            try {
                $repoRoot = Update-SSkillsCheckout -DataRoot $data -RepoUrl $RepoUrl -ZipUrl $ZipUrl
                Write-Host "已拿到最新副本。"
            }
            catch {
                $localRoot = $null
                if (-not [string]::IsNullOrWhiteSpace($ScriptRoot)) {
                    $localRoot = Split-Path -Parent $ScriptRoot
                }
                $localManifest = $null
                if ($null -ne $localRoot) {
                    $localManifest = Join-Path $localRoot "skills.json"
                }
                if ($null -ne $localManifest -and (Test-Path -LiteralPath $localManifest)) {
                    $repoRoot = $localRoot
                    $usedLocal = $true
                    Write-Host "没能从网上更新。改为使用脚本旁边的这份文件，它可能不是最新的。"
                    Write-Host $_.Exception.Message
                }
                else {
                    throw
                }
            }
        }

        $manifest = Get-SSkillsManifest -RepoRoot $repoRoot
        $index = Get-SSkillsIndex -RepoRoot $repoRoot -Manifest $manifest

        $groupText = $Groups
        if ([string]::IsNullOrWhiteSpace($groupText) -and -not $NonInteractive) {
            Write-SSkillsGroupMenu -Manifest $manifest
            $groupText = Read-Host "请输入分组，或直接回车"
        }
        $selectedGroups = @(Resolve-SSkillsGroups -Manifest $manifest -Text $groupText)
        Write-Host ""
        Write-Host ("这次要安装的分组：" + ((@($selectedGroups | ForEach-Object { $_.Id })) -join "、"))

        $knownTargets = @(Get-SSkillsKnownTargets -UserProfile $profilePath)
        $targetText = $Targets
        if ([string]::IsNullOrWhiteSpace($targetText) -and -not $NonInteractive) {
            Write-SSkillsTargetMenu -Targets $knownTargets
            $targetText = Read-Host "请输入安装位置，或直接回车"
        }
        $selectedTargets = @(Resolve-SSkillsTargets -Known $knownTargets -Text $targetText)
        if ($selectedTargets.Count -eq 0) {
            Write-Host ""
            Write-Host "没有可安装的位置。"
            Write-Host "没有检测到软件时，请先打开一次那个软件，或加上 -Targets 指定。例如："
            Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Targets cursor,workbuddy,opencode"
            Write-Host "可选 id：workbuddy、codebuddy、cursor、codex、codex-legacy、opencode、claude"
            return 2
        }

        $results = @()
        foreach ($target in $selectedTargets) {
            Write-Host ""
            Write-Host ("正在处理：{0}" -f $target.Title)
            $results += Update-SSkillsTarget -RepoRoot $repoRoot -Manifest $manifest -RepoIndex $index -SelectedGroups $selectedGroups -Target $target -DataRoot $data -Preview:$Preview
        }
        $failCount = Write-SSkillsSummary -Results $results -Preview:$Preview
        if ($usedLocal) {
            Write-Host "注意：这次用的是脚本旁边的旧副本，不是刚刚从网上更新的。"
        }
        if ($failCount -gt 0) {
            return 1
        }
        return 0
    }
    catch {
        Write-Host ""
        Write-Host ("出错了，安装停了下来：{0}" -f $_.Exception.Message)
        return 1
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    Write-Host "请不要直接运行这个文件。"
    Write-Host "请双击仓库里的「安装技能.cmd」，或在 PowerShell 里运行 scripts\install.ps1。"
    exit 1
}
