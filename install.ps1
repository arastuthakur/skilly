# Windows PowerShell Installer for Skilly
# Adds the Skilly directory or user bin to User PATH so 'skilly' can be run anywhere.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinDir = "$ScriptDir\bin"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Installing Skilly for Windows PowerShell..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Check if BinDir is already in User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    $NewPath = "$UserPath;$BinDir;$ScriptDir"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    $env:Path = "$env:Path;$BinDir;$ScriptDir"
    Write-Host "Added to User PATH: $BinDir" -ForegroundColor Green
    Write-Host "Restart open terminal sessions for changes to take full effect." -ForegroundColor Yellow
} else {
    Write-Host "Skilly is already present in your PATH." -ForegroundColor Green
}

Write-Host "`nYou can now run:" -ForegroundColor White
Write-Host "  skilly <project_directory>" -ForegroundColor Cyan
Write-Host "  skilly ." -ForegroundColor Cyan
Write-Host "  skilly my-project --serve" -ForegroundColor Cyan
