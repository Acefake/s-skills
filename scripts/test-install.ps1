# 在 Linux 的 pwsh 里检查安装脚本。不需要 Windows。
#requires -Version 5.1
Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "SSkills.ps1")

$script:Fail = 0
function Assert-True {
    param([bool]$Condition, [string]$Message)
    if ($Condition) {
        Write-Host "OK   $Message"
    }
    else {
        Write-Host "FAIL $Message"
        $script:Fail++
    }
}

function Write-Utf8File {
    param([string]$Path, [string]$Text)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Text, $utf8)
}

function New-Fixture {
    param([string]$Root)
    $alpha = Join-Path (Join-Path $Root "skills") "alpha"
    $beta = Join-Path (Join-Path $Root "skills") "beta"
    Write-Utf8File -Path (Join-Path (Join-Path $alpha "甲") "SKILL.md") -Text "---$([Environment]::NewLine)name: 甲$([Environment]::NewLine)description: 测试甲$([Environment]::NewLine)---$([Environment]::NewLine)甲的正文$([Environment]::NewLine)"
    Write-Utf8File -Path (Join-Path (Join-Path $alpha "乙") "SKILL.md") -Text "---$([Environment]::NewLine)name: 乙$([Environment]::NewLine)description: 测试乙$([Environment]::NewLine)---$([Environment]::NewLine)乙的正文$([Environment]::NewLine)"
    Write-Utf8File -Path (Join-Path $alpha "LICENSE-alpha") -Text "alpha license 许可证$([Environment]::NewLine)"
    Write-Utf8File -Path (Join-Path (Join-Path $beta "丙") "SKILL.md") -Text "---$([Environment]::NewLine)name: 丙$([Environment]::NewLine)description: 测试丙$([Environment]::NewLine)---$([Environment]::NewLine)丙的正文$([Environment]::NewLine)"
    $json = @'
{
  "schema": 1,
  "repo": "Acefake/s-skills",
  "defaultGroups": ["alpha"],
  "groups": [
    {
      "id": "alpha",
      "title": "甲组",
      "summary": "测试用的甲组",
      "license": "测试",
      "path": "skills/alpha",
      "licenseFiles": ["LICENSE-alpha"],
      "skills": [{ "name": "甲" }, { "name": "乙" }]
    },
    {
      "id": "beta",
      "title": "乙组",
      "summary": "测试用的乙组",
      "license": "测试",
      "path": "skills/beta",
      "licenseFiles": [],
      "skills": [{ "name": "丙" }]
    }
  ]
}
'@
    Write-Utf8File -Path (Join-Path $Root "skills.json") -Text $json
}

function Invoke-Install {
    param(
        [string]$Repo,
        [string]$UserHome,
        [string]$Data,
        [string]$Groups,
        [string]$Targets,
        [switch]$Preview
    )
    return Invoke-SSkillsMain -Groups $Groups -Targets $Targets -SourcePath $Repo -UserProfile $UserHome -DataRoot $Data -NonInteractive -Preview:$Preview -ScriptRoot $PSScriptRoot
}

$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("s-skills-test-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $temp -Force | Out-Null
try {
    $repo = Join-Path $temp "repo"
    New-Fixture -Root $repo
    $manifest = Get-SSkillsManifest -RepoRoot $repo
    Assert-True ($manifest.DefaultGroups.Count -eq 1 -and $manifest.DefaultGroups[0] -eq "alpha") "单个默认分组不会被拆成一个个字母"
    $alpha = $manifest.Groups | Where-Object { $_.Id -eq "alpha" }
    Assert-True (@($alpha.LicenseFiles).Count -eq 1 -and $alpha.LicenseFiles[0] -eq "LICENSE-alpha") "单个许可证文件名保持完整"
    $beta = $manifest.Groups | Where-Object { $_.Id -eq "beta" }
    Assert-True (@($beta.Skills).Count -eq 1 -and $beta.Skills[0] -eq "丙") "只有一个技能时名字仍然是「丙」"
    $index = Get-SSkillsIndex -RepoRoot $repo -Manifest $manifest
    Assert-True ($index.Count -eq 3) "清单里有 3 个技能"

    $bad = $false
    try { Resolve-SSkillsGroups -Manifest $manifest -Text "没有这组" | Out-Null } catch { $bad = $true }
    Assert-True $bad "不认识的分组会报错"

    $picked = @(Resolve-SSkillsGroups -Manifest $manifest -Text "")
    Assert-True ($picked.Count -eq 1 -and $picked[0].Id -eq "alpha") "空输入等于默认分组"
    $allGroups = @(Resolve-SSkillsGroups -Manifest $manifest -Text "全部")
    Assert-True ($allGroups.Count -eq 2) "「全部」会选中所有分组"

    $home1 = Join-Path $temp "home1"
    New-Item -ItemType Directory -Path (Join-Path $home1 ".cursor") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $home1 ".codex") -Force | Out-Null
    $known = @(Get-SSkillsKnownTargets -UserProfile $home1)
    $cursor = $known | Where-Object { $_.Id -eq "cursor" }
    $legacy = $known | Where-Object { $_.Id -eq "codex-legacy" }
    $codex = $known | Where-Object { $_.Id -eq "codex" }
    Assert-True ($cursor.Detected -and $cursor.DefaultSelected) "有 .cursor 文件夹时，Cursor 默认会装"
    Assert-True ($codex.Detected -and $codex.DefaultSelected) "有 .codex 时，Codex 现行目录默认会装"
    Assert-True ($legacy.Detected -and -not $legacy.DefaultSelected) "Codex 旧目录检测到了，但默认不装"
    $defaults = @(Resolve-SSkillsTargets -Known $known -Text "")
    $defaultIds = @($defaults | ForEach-Object { $_.Id })
    Assert-True ($defaultIds -contains "cursor" -and $defaultIds -contains "codex" -and -not ($defaultIds -contains "codex-legacy")) "回车不会把 Codex 旧目录算进去"

    $data1 = Join-Path $temp "data1"
    $skillsDir = Join-Path (Join-Path $home1 ".cursor") "skills"
    $stranger = Join-Path $skillsDir "不要动"
    Write-Utf8File -Path (Join-Path $stranger "SKILL.md") -Text "别人的技能，不要动$([Environment]::NewLine)"
    Write-Utf8File -Path (Join-Path $skillsDir "我的笔记.txt") -Text "笔记$([Environment]::NewLine)"
    Write-Utf8File -Path (Join-Path (Join-Path $skillsDir "甲") "SKILL.md") -Text "这是我自己原来的甲$([Environment]::NewLine)"
    $strangerHash = Get-SSkillsFileHash (Join-Path $stranger "SKILL.md")
    $noteHash = Get-SSkillsFileHash (Join-Path $skillsDir "我的笔记.txt")

    $previewHome = Join-Path $temp "preview-home"
    $previewData = Join-Path $temp "preview-data"
    $previewCode = Invoke-Install -Repo $repo -UserHome $previewHome -Data $previewData -Groups "alpha" -Targets "cursor" -Preview
    Assert-True ($previewCode -eq 0) "预览的退出码是 0"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path (Join-Path $previewHome ".cursor") "skills"))) "预览不会创建技能文件夹"

    $code = Invoke-Install -Repo $repo -UserHome $home1 -Data $data1 -Groups "alpha" -Targets "cursor"
    Assert-True ($code -eq 0) "安装甲组成功"
    Assert-True (Test-Path -LiteralPath (Join-Path (Join-Path $skillsDir "甲") "SKILL.md")) "装上了「甲」"
    Assert-True (Test-Path -LiteralPath (Join-Path (Join-Path $skillsDir "乙") "SKILL.md")) "装上了「乙」"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $skillsDir "丙"))) "没选的分组不会装上"
    Assert-True ((Get-SSkillsFileHash (Join-Path $stranger "SKILL.md")) -eq $strangerHash) "没装过的「不要动」保持原样"
    Assert-True ((Get-SSkillsFileHash (Join-Path $skillsDir "我的笔记.txt")) -eq $noteHash) "技能目录里原有的笔记文件保持原样"
    $licenseText = [System.IO.File]::ReadAllText((Join-Path $skillsDir "LICENSE-alpha"))
    Assert-True ($licenseText.Contains("alpha license")) "许可证被复制到技能文件夹的上一级"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path (Join-Path $skillsDir "甲") "LICENSE-alpha"))) "许可证不会被塞进技能自己的文件夹"
    $backupRoot = Join-Path (Join-Path $data1 "backups") "cursor"
    $backupHits = @(Get-ChildItem -LiteralPath $backupRoot -Recurse -Filter "SKILL.md" -File -ErrorAction SilentlyContinue)
    Assert-True ($backupHits.Count -ge 1) "原来就有的同名「甲」被备份了"
    $installed = Get-SSkillsInstalled -SkillsDir $skillsDir
    Assert-True ($installed.Skills.ContainsKey("甲") -and $installed.Skills.ContainsKey("乙") -and -not $installed.Skills.ContainsKey("不要动")) "清单只记录脚本装上的技能"
    Assert-True ($installed.Files.ContainsKey("LICENSE-alpha")) "清单记录了脚本复制的许可证"

    $code2 = Invoke-Install -Repo $repo -UserHome $home1 -Data $data1 -Groups "alpha" -Targets "cursor"
    Assert-True ($code2 -eq 0) "再运行一次成功"
    $backupHits2 = @(Get-ChildItem -LiteralPath $backupRoot -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "甲" })
    Assert-True ($backupHits.Count -eq $backupHits2.Count) "已经由脚本管理的文件夹，更新时不会再备份一次"

    Write-Utf8File -Path (Join-Path (Join-Path $skillsDir "甲") "SKILL.md") -Text "被改坏了$([Environment]::NewLine)"
    $code3 = Invoke-Install -Repo $repo -UserHome $home1 -Data $data1 -Groups "alpha" -Targets "cursor"
    Assert-True ($code3 -eq 0) "修复被改过的文件成功"
    $restored = [System.IO.File]::ReadAllText((Join-Path (Join-Path $skillsDir "甲") "SKILL.md"))
    Assert-True ($restored.Contains("甲的正文")) "更新把脚本装过的文件改回仓库里的内容"

    $repo2 = Join-Path $temp "repo2"
    New-Fixture -Root $repo2
    Remove-Item -LiteralPath (Join-Path (Join-Path (Join-Path $repo2 "skills") "alpha") "乙") -Recurse -Force
    $json2 = [System.IO.File]::ReadAllText((Join-Path $repo2 "skills.json"))
    $json2 = $json2.Replace(', { "name": "乙" }', '')
    Write-Utf8File -Path (Join-Path $repo2 "skills.json") -Text $json2
    $home2 = Join-Path $temp "home2"
    $data2 = Join-Path $temp "data2"
    New-Item -ItemType Directory -Path (Join-Path $home2 ".cursor") -Force | Out-Null
    Assert-True ((Invoke-Install -Repo $repo -UserHome $home2 -Data $data2 -Groups "all" -Targets "cursor") -eq 0) "先装全部分组"
    $skills2 = Join-Path (Join-Path $home2 ".cursor") "skills"
    Assert-True (Test-Path -LiteralPath (Join-Path $skills2 "丙")) "全部分组包含「丙」"
    Assert-True ((Invoke-Install -Repo $repo2 -UserHome $home2 -Data $data2 -Groups "alpha" -Targets "cursor") -eq 0) "仓库删掉「乙」之后再次安装"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $skills2 "乙"))) "脚本以前装的、仓库里已经没有的「乙」被删掉"
    Assert-True (Test-Path -LiteralPath (Join-Path $skills2 "甲")) "还在仓库里的「甲」还在"
    Assert-True (Test-Path -LiteralPath (Join-Path $skills2 "丙")) "这次没选、但以前装过、仓库里还有的「丙」不会被删"
    $state2 = Get-SSkillsInstalled -SkillsDir $skills2
    Assert-True ($state2.Skills.ContainsKey("丙") -and -not $state2.Skills.ContainsKey("乙")) "清单和删掉的技能一致"

    $emptyHome = Join-Path $temp "empty-home"
    New-Item -ItemType Directory -Path $emptyHome -Force | Out-Null
    $emptyCode = Invoke-Install -Repo $repo -UserHome $emptyHome -Data (Join-Path $temp "empty-data") -Groups "alpha" -Targets ""
    Assert-True ($emptyCode -eq 2) "一个软件都没检测到、又没指定位置时，退出码是 2"

    $zipRoot = Join-Path $temp "zip-src"
    $zipInner = Join-Path $zipRoot "s-skills-main"
    New-Fixture -Root $zipInner
    $zipPath = Join-Path $temp "skills.zip"
    python3 -c "import zipfile,sys,os; root=sys.argv[1]; dest=sys.argv[2]; z=zipfile.ZipFile(dest,'w');
import os
for dp, dns, fns in os.walk(root):
  for fn in fns:
    full=os.path.join(dp, fn); rel=os.path.relpath(full, root).replace('\\\\','/'); info=zipfile.ZipInfo(rel); info.flag_bits |= 0x800; z.writestr(info, open(full,'rb').read())
z.close()" $zipRoot $zipPath
    $extract = Join-Path $temp "zip-out"
    Expand-SSkillsZip -ZipPath $zipPath -Destination $extract
    $extractedRoot = Resolve-SSkillsExtractedRoot -Destination $extract
    Assert-True (Test-Path -LiteralPath (Join-Path (Join-Path (Join-Path $extractedRoot "skills") "alpha") "甲")) "压缩包里的中文文件夹名能解出来"

    $gitOrigin = Join-Path $temp "git-origin"
    New-Fixture -Root $gitOrigin
    & git -C $gitOrigin init -b main | Out-Null
    & git -C $gitOrigin config user.email "s@example.com"
    & git -C $gitOrigin config user.name "S"
    & git -C $gitOrigin add skills skills.json
    & git -C $gitOrigin commit -m "init" | Out-Null
    $gitData = Join-Path $temp "git-data"
    $cloned = Update-SSkillsCheckout -DataRoot $gitData -RepoUrl $gitOrigin -ZipUrl "http://127.0.0.1/unused"
    Assert-True (Test-Path -LiteralPath (Join-Path $cloned "skills.json")) "git 能下载本地仓库"
    Write-Utf8File -Path (Join-Path $gitOrigin "新文件.txt") -Text "第二次$([Environment]::NewLine)"
    & git -C $gitOrigin add "新文件.txt"
    & git -C $gitOrigin commit -m "second" | Out-Null
    $cloned2 = Update-SSkillsCheckout -DataRoot $gitData -RepoUrl $gitOrigin -ZipUrl "http://127.0.0.1/unused"
    Assert-True (Test-Path -LiteralPath (Join-Path $cloned2 "新文件.txt")) "再运行会用 git 更新到新提交"

    $real = Split-Path -Parent $PSScriptRoot
    $realManifest = Get-SSkillsManifest -RepoRoot $real
    $counts = @{}
    foreach ($group in @($realManifest.Groups)) {
        $counts[$group.Id] = @($group.Skills).Count
    }
    Assert-True ($counts["pstack"] -eq 54) "真实仓库的 pstack 有 54 个"
    Assert-True ($counts["compound-engineering"] -eq 15) "compound-engineering 有 15 个"
    Assert-True ($counts["superpowers"] -eq 1) "superpowers 有 1 个"
    Assert-True ($counts["ui-ux"] -eq 18) "ui-ux 有 18 个"
    Assert-True ($counts["figma"] -eq 16) "figma 有 16 个"
    Assert-True ($counts["my-skills"] -eq 5) "my-skills 有 5 个"
    $realIndex = Get-SSkillsIndex -RepoRoot $real -Manifest $realManifest
    Assert-True ($realIndex.Count -eq 109) "清单和文件夹一致，一共 109 个"
    $realHome = Join-Path $temp "real-home"
    $realData = Join-Path $temp "real-data"
    New-Item -ItemType Directory -Path (Join-Path $realHome ".cursor") -Force | Out-Null
    $realCode = Invoke-Install -Repo $real -UserHome $realHome -Data $realData -Groups "pstack,my-skills" -Targets "cursor"
    Assert-True ($realCode -eq 0) "真实的 pstack 和我自己的技能能装上"
    $realSkills = Join-Path (Join-Path $realHome ".cursor") "skills"
    $sample = "原则-证明真能用"
    $srcSample = Join-Path (Join-Path (Join-Path $real "skills") "pstack") $sample
    $dstSample = Join-Path $realSkills $sample
    Assert-True ((Get-SSkillsFingerprint $srcSample) -eq (Get-SSkillsFingerprint $dstSample)) "中文技能文件夹和仓库逐字节一致"
    Assert-True (Test-Path -LiteralPath (Join-Path $realSkills "LICENSE-pstack")) "pstack 的许可证在上一级文件夹"
    Assert-True (Test-Path -LiteralPath (Join-Path $realSkills "make-bot-ui")) "自己的 make-bot-ui 也装上了"
    $again = Invoke-Install -Repo $real -UserHome $realHome -Data $realData -Groups "pstack,my-skills" -Targets "cursor"
    Assert-True ($again -eq 0) "真实技能再安装一次成功"

    if (Get-Module -ListAvailable -Name PSScriptAnalyzer) {
        $analyzer = Invoke-ScriptAnalyzer -Path (Join-Path $PSScriptRoot "SSkills.ps1") -Settings @{
            Rules = @{ PSUseCompatibleSyntax = @{ Enable = $true; TargetVersions = @("5.1", "7.0") } }
        }
        $syntax = @($analyzer | Where-Object { $_.RuleName -eq "PSUseCompatibleSyntax" })
        Assert-True ($syntax.Count -eq 0) "PSScriptAnalyzer 没有发现 PowerShell 5.1 不兼容的语法"
        foreach ($item in $syntax) {
            Write-Host ("  {0}:{1} {2}" -f $item.ScriptName, $item.Line, $item.Message)
        }
    }
    else {
        Write-Host "SKIP 没有安装 PSScriptAnalyzer"
    }
}
finally {
    if (Test-Path -LiteralPath $temp) {
        Remove-Item -LiteralPath $temp -Recurse -Force
    }
}

if ($script:Fail -gt 0) {
    Write-Host ("失败 {0} 项" -f $script:Fail)
    exit 1
}
Write-Host "全部检查通过"
exit 0
