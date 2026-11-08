# Deploys a ready image version to a contour (dev or prod) and runs a smoke test.
#
#   $env:DB_PASSWORD = '...'
#   .\deploy\deploy.ps1 -Target dev -Tag sha-1a2b3c4
#
# The pipeline (deploy jobs and the Rollback workflow) calls exactly this script.
# Messages are ASCII on purpose: Windows PowerShell 5.1 misreads UTF-8 without BOM.

param(
    [Parameter(Mandatory = $true)][ValidateSet('dev', 'prod')][string]$Target,
    [Parameter(Mandatory = $true)][ValidatePattern('^sha-[0-9a-f]{7}$')][string]$Tag
)

$ErrorActionPreference = 'Stop'

if (-not $env:DB_PASSWORD) { throw 'DB_PASSWORD is not set' }
if (-not $env:IMAGE_PREFIX) { $env:IMAGE_PREFIX = 'ghcr.io/ski11s100/cicd-practice' }
$env:IMAGE_TAG = $Tag

$project = "todo-$Target"
$envFile = Join-Path $PSScriptRoot "$Target.env"
$composeFile = Join-Path $PSScriptRoot 'compose.yaml'
$port = ((Get-Content $envFile) -match '^HTTP_PORT=') -replace '^HTTP_PORT=', ''

function Invoke-Compose {
    # docker compose prints progress to stderr: show it as plain text and judge success by the exit code.
    $ErrorActionPreference = 'Continue'
    & docker compose -p $project --env-file $envFile -f $composeFile @args 2>&1 | ForEach-Object { "$_" }
    if ($LASTEXITCODE -ne 0) { throw "docker compose $args failed with exit code $LASTEXITCODE" }
}

Write-Host "==> Deploying $Tag to $Target (project $project, port $port)"
Invoke-Compose pull
Invoke-Compose up -d --wait --wait-timeout 120

Write-Host '==> Smoke test'
$health = Invoke-RestMethod "http://localhost:$port/api/health"
$info = Invoke-RestMethod "http://localhost:$port/api/info"
if ($health.status -ne 'ok') { throw "Smoke test failed: health = $($health | ConvertTo-Json -Compress)" }
if ($info.env -ne $Target -or $info.version -ne $Tag) {
    throw "Smoke test failed: expected $Target/$Tag, got $($info.env)/$($info.version)"
}

Invoke-Compose ps
Write-Host "==> OK: $Target is running $Tag at http://localhost:$port"
