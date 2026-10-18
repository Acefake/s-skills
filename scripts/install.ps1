#requires -Version 5.1
<#
.SYNOPSIS
把这个仓库里的中文技能安装到本机的 AI 软件里。再运行一次就是更新。

.DESCRIPTION
技能（skill）是一份写给 AI 的做事说明。本脚本只复制文件夹，不修改技能正文。
默认只安装 pstack 这一组，并安装到已经检测到的软件。不会改动脚本没有安装过的文件夹。

.PARAMETER Groups
要安装的分组。直接回车的默认值是 pstack。all 表示全部。也可以写英文 id，用逗号分开，例如 pstack,figma。

.PARAMETER Targets
要装进哪些软件。默认是已经检测到的软件。all 表示全部已知位置。id 有：workbuddy、codebuddy、cursor、codex、codex-legacy、opencode、claude。

.PARAMETER Preview
只显示将要做什么，不改文件。

.PARAMETER NonInteractive
不问问题。没写 Groups 就用默认分组，没写 Targets 就用检测到的软件。

.PARAMETER SourcePath
用这个本地文件夹，不从网上重新下载。测试时会用到。
#>
param(
    [string]$Groups,
    [string]$Targets,
    [string]$SourcePath,
    [string]$UserProfile,
    [string]$DataRoot,
    [string]$RepoUrl = "https://github.com/Acefake/s-skills.git",
    [string]$ZipUrl = "https://github.com/Acefake/s-skills/archive/refs/heads/main.zip",
    [switch]$NonInteractive,
    [switch]$Preview
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "SSkills.ps1")

$exitCode = Invoke-SSkillsMain -Groups $Groups -Targets $Targets -SourcePath $SourcePath -UserProfile $UserProfile -DataRoot $DataRoot -RepoUrl $RepoUrl -ZipUrl $ZipUrl -ScriptRoot $PSScriptRoot -NonInteractive:$NonInteractive -Preview:$Preview
exit $exitCode
