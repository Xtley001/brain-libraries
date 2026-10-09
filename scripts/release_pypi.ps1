# PyPI Release Script for Brain Libraries Suite
param(
    [string]$Token = $env:PYPI_API_TOKEN
)

if (-not $Token) {
    Write-Error "Please provide a PyPI token via -Token or set the PYPI_API_TOKEN environment variable."
    exit 1
}

$distDir = Join-Path (Split-Path -Parent $PSScriptRoot) "dist"
$wheels = Get-ChildItem -Path $distDir -Filter "*.whl"

Write-Host "Found $($wheels.Count) wheels in $distDir" -ForegroundColor Cyan

foreach ($whl in $wheels) {
    Write-Host "Uploading $($whl.Name)..." -ForegroundColor Yellow
    python -m twine upload -u __token__ -p $Token $whl.FullName --skip-existing
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Upload for $($whl.Name) encountered rate limit or error. PyPI enforces cooldown between new projects."
    }
}
