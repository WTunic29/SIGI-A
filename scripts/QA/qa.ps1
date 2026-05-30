# SIGI-A QA — entrada única (pytest + validación Postman + Newman opcional)
param(
    [Parameter(Position = 0)]
    [ValidateSet("check", "smoke", "install")]
    [string]$Command = "check"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Invoke-QaCheck {
    python scripts/validate_postman_workspace.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    python scripts/check_xfail_budget.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($args.Count -gt 0) {
        python -m pytest tests -q --tb=line @args
    } else {
        python -m pytest tests -q --tb=line
    }
    exit $LASTEXITCODE
}

function Get-PnpmCmd {
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        return @{ exe = "pnpm"; prefix = @() }
    }
    Write-Host "pnpm no en PATH; usando npx pnpm@9.15.9 (misma versión que packageManager)"
    return @{ exe = "npx"; prefix = @("--yes", "pnpm@9.15.9") }
}

function Invoke-Pnpm {
    param([string[]]$PnpmArgs)
    $p = Get-PnpmCmd
    & $p.exe @($p.prefix + $PnpmArgs)
}

function Invoke-QaSmoke {
    if (-not (Test-Path "node_modules")) {
        Invoke-Pnpm @("install")
    }
    Invoke-Pnpm @("run", "postman:newman:smoke") + $args
    exit $LASTEXITCODE
}

function Invoke-QaInstall {
    Invoke-Pnpm @("install")
    Write-Host "Python (desde la raíz del repo o con venv activo):"
    Write-Host "  pip install -r ..\backend\requirements.txt -r requirements-ci.txt"
}

switch ($Command) {
    "check" { Invoke-QaCheck }
    "smoke" { Invoke-QaSmoke }
    "install" { Invoke-QaInstall }
}
