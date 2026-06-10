# Renders an identity-card HTML file to PNG via headless Edge.
# Usage: .\render.ps1 -Html path\to\card.html [-Height 700] [-Out path\to\out.png]
param(
    [Parameter(Mandatory = $true)][string]$Html,
    [int]$Height = 700,
    [string]$Out
)

$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) { $edge = "C:\Program Files\Microsoft\Edge\Application\msedge.exe" }

$htmlPath = (Resolve-Path $Html).Path
if (-not $Out) { $Out = [System.IO.Path]::ChangeExtension($htmlPath, ".png") }

& $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 `
    --screenshot="$Out" --window-size="1200,$Height" "file:///$($htmlPath -replace '\\','/')" 2>$null | Out-Null
Start-Sleep -Seconds 2
Get-Item $Out | Select-Object FullName, Length
