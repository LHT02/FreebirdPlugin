param(
    [string]$Destination = "$env:USERPROFILE\.freebird\plugins\freebird_curve_editor"
)

$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$source = (Resolve-Path -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'freebird_curve_editor')).Path
$pluginsRoot = Split-Path -Parent $Destination
[System.IO.Directory]::CreateDirectory($pluginsRoot) | Out-Null

if (Test-Path -LiteralPath $Destination) {
    $item = Get-Item -LiteralPath $Destination -Force
    if ($item.LinkType -eq 'Junction' -and $item.Target -contains $source) {
        Write-Output "Development junction already exists: $Destination"
        exit 0
    }
    throw "Destination already exists and was left unchanged: $Destination"
}

New-Item -ItemType Junction -Path $Destination -Target $source | Out-Null
Write-Output "Installed development junction: $Destination -> $source"
Write-Output 'Use Freebird Settings > Reload All when it is safe to reload the running Blender session.'
