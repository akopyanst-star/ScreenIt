<#
.SYNOPSIS
    Install ScreenIt: download the latest ScreenIt.exe, add it to startup and
    the Start Menu, and launch it. No Python required.

.EXAMPLE
    irm https://github.com/akopyanst-star/ScreenIt/raw/master/install.ps1 | iex
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

# Uninstaller, placed next to the app.
$UninstallPath = Join-Path $InstallDir 'uninstall.ps1'
Invoke-WebRequest -Uri "https://github.com/$Repo/raw/master/uninstall.ps1" -OutFile $UninstallPath
$uninstallCmd = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$UninstallPath`""

# Start Menu + Desktop shortcuts (+ an Uninstall shortcut in the Start Menu).
$shell     = New-Object -ComObject WScript.Shell
$startMenu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
foreach ($dir in @($startMenu, [Environment]::GetFolderPath('Desktop'))) {
    $lnk = $shell.CreateShortcut((Join-Path $dir 'ScreenIt.lnk'))
    $lnk.TargetPath = $ExePath
    $lnk.Save()
}
$unlnk = $shell.CreateShortcut((Join-Path $startMenu 'Uninstall ScreenIt.lnk'))
$unlnk.TargetPath = 'powershell.exe'
$unlnk.Arguments  = "-NoProfile -ExecutionPolicy Bypass -File `"$UninstallPath`""
$unlnk.Save()

# Run at logon.
$runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
Set-ItemProperty -Path $runKey -Name 'ScreenIt' -Value "`"$ExePath`""

# Register in Windows "Programs & Features" so it can be uninstalled from there.
$unkey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\ScreenIt'
New-Item -Path $unkey -Force | Out-Null
$ver = ($release.tag_name -replace '^v', '')
Set-ItemProperty $unkey DisplayName     'ScreenIt'
Set-ItemProperty $unkey DisplayVersion  $ver
Set-ItemProperty $unkey Publisher       'ScreenIt'
Set-ItemProperty $unkey DisplayIcon     $ExePath
Set-ItemProperty $unkey InstallLocation $InstallDir
Set-ItemProperty $unkey UninstallString $uninstallCmd
Set-ItemProperty $unkey NoModify 1 -Type DWord
Set-ItemProperty $unkey NoRepair 1 -Type DWord

Start-Process $ExePath
Write-Host "Done. ScreenIt is running in the tray. Press Ctrl+Shift+S to capture." -ForegroundColor Green
Write-Host "Uninstall later from Settings > Apps, or the 'Uninstall ScreenIt' Start Menu item." -ForegroundColor Green
