param(
    [switch]$SkipAntigravity
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$pluginRoot = Join-Path $repoRoot 'plugins\wukong'
$globalScript = Join-Path $pluginRoot 'skills\wukong-init\scripts\global_instructions.py'
$python = if (Test-Path (Join-Path $repoRoot '.venv\Scripts\python.exe')) {
    Join-Path $repoRoot '.venv\Scripts\python.exe'
} else {
    'python'
}

Write-Host "=== wukong 新机器一键引导 ==="
Write-Host "仓库路径: $repoRoot"

# 1. Codex 本项目技能链接
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'install_local_skills.ps1') -HostName codex

# 2. Antigravity 零复制挂载（~/.gemini/config/plugins.json）
$geminiConfig = Join-Path $env:USERPROFILE '.gemini\config'
if (-not $SkipAntigravity -and (Test-Path $geminiConfig)) {
    $pluginsJson = Join-Path $geminiConfig 'plugins.json'
    $pluginsDir = (Join-Path $repoRoot 'plugins').Replace('\', '/')
    $homeNorm = $env:USERPROFILE.Replace('\', '/')
    $entryPath = if ($pluginsDir.StartsWith($homeNorm + '/', [System.StringComparison]::OrdinalIgnoreCase)) {
        '~/' + $pluginsDir.Substring($homeNorm.Length + 1)
    } else {
        $pluginsDir
    }
    $data = if (Test-Path $pluginsJson) {
        Get-Content -LiteralPath $pluginsJson -Raw -Encoding UTF8 | ConvertFrom-Json
    } else {
        [pscustomobject]@{ entries = @() }
    }
    $entries = @($data.entries)
    if (-not ($entries | Where-Object { $_.path -eq $entryPath })) {
        $entries += [pscustomobject]@{ path = $entryPath }
        $out = [ordered]@{ entries = $entries } | ConvertTo-Json -Depth 5
        [System.IO.File]::WriteAllText($pluginsJson, $out + "`n", (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "已注册 Antigravity 插件目录: $entryPath -> $pluginsJson"
    } else {
        Write-Host "Antigravity 插件目录已注册: $entryPath"
    }
}

# 3. 只读检测已安装宿主的全局规则状态
$hosts = @(
    @{ Name = 'claude-code'; Dir = (Join-Path $env:USERPROFILE '.claude') },
    @{ Name = 'codex';       Dir = (Join-Path $env:USERPROFILE '.codex') },
    @{ Name = 'antigravity'; Dir = (Join-Path $env:USERPROFILE '.gemini\config') }
)
Write-Host "`n=== 全局规则只读体检 ==="
foreach ($h in $hosts) {
    if (Test-Path $h.Dir) {
        $json = & $python -B $globalScript --host $h.Name 2>$null
        if ($json) {
            $parsed = $json | ConvertFrom-Json
            Write-Host ("  {0,-12} status={1}  target={2}" -f $h.Name, $parsed.status, $parsed.target)
        }
    }
}

Write-Host "`n下一步：打开新会话执行 /wukong-init。"
