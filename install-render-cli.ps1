# PowerShell script to install Render CLI on Windows

$renderVersion = "v2.1.4"
$renderUrl = "https://github.com/render-oss/cli/releases/download/$renderVersion/render-windows-x86_64.exe"
$installPath = "$env:USERPROFILE\.render"
$binPath = "$installPath\bin"

Write-Host "Installing Render CLI $renderVersion..." -ForegroundColor Green

# Create installation directory
if (!(Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
}
if (!(Test-Path $binPath)) {
    New-Item -ItemType Directory -Path $binPath -Force | Out-Null
}

# Download the CLI executable
$exePath = "$binPath\render.exe"
Write-Host "Downloading from $renderUrl..."
Invoke-WebRequest -Uri $renderUrl -OutFile $exePath

# Add to PATH if not already there
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$binPath*") {
    Write-Host "Adding $binPath to PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "User")
    $env:Path = "$env:Path;$binPath"
}

Write-Host "Render CLI installed successfully!" -ForegroundColor Green
Write-Host "Please restart your terminal or run: `$env:Path = `"`$env:Path;$binPath`"" -ForegroundColor Yellow
Write-Host "Then run 'render login' to authenticate" -ForegroundColor Yellow