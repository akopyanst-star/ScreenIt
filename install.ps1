<#
.SYNOPSIS
    Install ScreenIt: download the latest ScreenIt.exe, add it to startup and
    the Start Menu, and launch it. No Python required.

.EXAMPLE
    irm https://github.com/akopyanst-star/ScreenIt/raw/main/install.ps1 | iex
#>

$ErrorActionPreference = 'Stop'

$Repo      = 'akopyanst-star/ScreenIt'
$InstallDir = Join-Path $env:LOCALAPPDATA 'ScreenIt'
$ExePath    = Join-Path $InstallDir 'ScreenIt.exe'

Write-Host "Installing ScreenIt..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Find the ScreenIt.exe asset on the latest GitHub release.
$api    = "https://api.github.com/repos/$Repo/releases/latest"
$release = Invoke-RestMethod -Uri $api -Headers @{ 'User-Agent' = 'ScreenIt-Installer' }
$asset  = $release.assets | Where-Object { $_.name -eq 'ScreenIt.exe' } | Select-Object -First 1
if (-not $asset) { throw "ScreenIt.exe not found in the latest release of $Repo" }

Write-Host "Downloading $($release.tag_name)..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $ExePath

# Start Menu shortcut.
$startMenu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
$shell     = New-Object -ComObject WScript.Shell
$shortcut  = $shell.CreateShortcut((Join-Path $startMenu 'ScreenIt.lnk'))
$shortcut.TargetPath = $ExePath
$shortcut.Save()

# Run at logon.
$runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
Set-ItemProperty -Path $runKey -Name 'ScreenIt' -Value "`"$ExePath`""

Start-Process $ExePath
Write-Host "Done. ScreenIt is running in the tray. Press Ctrl+Shift+S to capture." -ForegroundColor Green
