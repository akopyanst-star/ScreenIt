<#
.SYNOPSIS
    Remove ScreenIt completely: stop it, delete the app, shortcuts, autostart,
    settings and the Windows "Programs & Features" entry.

    A copy of this script is placed in the install folder
    (%LOCALAPPDATA%\ScreenIt) and is what the Control Panel "Uninstall" button
    runs. You can also just double-run it from there.
#>

$ErrorActionPreference = 'SilentlyContinue'
$InstallDir = Join-Path $env:LOCALAPPDATA 'ScreenIt'

Write-Host "Removing ScreenIt..." -ForegroundColor Cyan

# Stop the running app.
Get-Process ScreenIt | Stop-Process -Force
Start-Sleep -Milliseconds 500

# Run-at-startup entry.
Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name ScreenIt

# Shortcuts (Start Menu + Desktop).
$startMenu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
Remove-Item (Join-Path $startMenu 'ScreenIt.lnk')
Remove-Item (Join-Path $startMenu 'Uninstall ScreenIt.lnk')
Remove-Item (Join-Path ([Environment]::GetFolderPath('Desktop')) 'ScreenIt.lnk')

# Programs & Features registration.
Remove-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\ScreenIt' -Recurse

# Per-user settings and log.
Remove-Item (Join-Path $env:APPDATA 'ScreenIt') -Recurse -Force

# Finally remove the install folder. This script lives inside it, so hand the
# deletion to a detached cmd that waits for us to exit first.
Start-Process cmd -WindowStyle Hidden -ArgumentList "/c timeout /t 2 /nobreak >nul & rmdir /s /q `"$InstallDir`""

Write-Host "ScreenIt removed." -ForegroundColor Green
