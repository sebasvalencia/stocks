# Dump or restore the Postgres database from docker compose (service: db).
# Run from anywhere. Compose and .env live in the repo root (parent of this folder).
# Usage:
#   .\backups\backup.ps1
#   .\backups\backup.ps1 -Keep 12
#   .\backups\backup.ps1 -Restore acciones_2026-09-10_1431.sql
#   .\backups\backup.ps1 -Restore demo\demo.sql -Force
#   .\backups\backup.ps1 -Out demo\demo.sql

param(
    [string]$Restore,
    [string]$Out,
    [switch]$Force,
    [int]$Keep = 0
)

$ErrorActionPreference = "Stop"
$BackupDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $BackupDir
Set-Location $Root

function Get-DotEnv([string]$Path) {
    $map = @{}
    if (-not (Test-Path $Path)) { return $map }
    Get-Content -Path $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim().Trim('"').Trim("'")
        $map[$key] = $val
    }
    return $map
}

function Resolve-DumpPath([string]$Path) {
    if ([System.IO.Path]::IsPathRooted($Path) -and (Test-Path $Path)) {
        return (Resolve-Path $Path).Path
    }
    foreach ($base in @($BackupDir, (Join-Path $Root "demo"), $Root, (Get-Location).Path)) {
        $candidate = Join-Path $base $Path
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }
    throw "Backup file not found: $Path"
}

$envFile = Join-Path $Root ".env"
if (-not (Test-Path $envFile)) {
    throw "Missing .env. Copy .env.example to .env and set POSTGRES_USER / POSTGRES_DB."
}
$dotEnv = Get-DotEnv $envFile
$User = if ($dotEnv["POSTGRES_USER"]) { $dotEnv["POSTGRES_USER"] } else { "acciones" }
$DbName = if ($dotEnv["POSTGRES_DB"]) { $dotEnv["POSTGRES_DB"] } else { "acciones" }

function Wait-Db {
    docker compose up -d db | Out-Null
    for ($i = 0; $i -lt 30; $i++) {
        docker compose exec -T db pg_isready -U $User -d $DbName 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { return }
        Start-Sleep -Seconds 2
    }
    throw "PostgreSQL did not become ready. Is Docker running? Try: docker compose up -d db"
}

function Assert-Exit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE)" }
}

Wait-Db
New-Item -ItemType Directory -Force $BackupDir | Out-Null

if ($Restore) {
    $file = Resolve-DumpPath $Restore

    if (-not $Force) {
        $answer = Read-Host "This will overwrite the current database. Continue? (y/N)"
        if ($answer -notin @("y", "Y", "s", "S")) {
            Write-Host "Cancelled."
            exit 0
        }
    }

    $remote = "/tmp/acciones_restore.sql"
    docker compose cp $file "db:${remote}"
    Assert-Exit "Copy dump into container"
    docker compose exec -T db psql -U $User -d $DbName -v ON_ERROR_STOP=1 -f $remote
    Assert-Exit "psql restore"
    docker compose exec -T db rm -f $remote | Out-Null
    Write-Host "Restored $file"
    exit 0
}

$stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
if ($Out) {
    $out = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $Root $Out }
    New-Item -ItemType Directory -Force (Split-Path -Parent $out) | Out-Null
} else {
    $out = Join-Path $BackupDir "acciones_$stamp.sql"
}
$remote = "/tmp/acciones_dump.sql"

docker compose exec -T db pg_dump -U $User -d $DbName --clean --if-exists --no-owner --no-acl -f $remote
Assert-Exit "pg_dump"
docker compose cp "db:${remote}" $out
Assert-Exit "Copy dump out of container"
docker compose exec -T db rm -f $remote | Out-Null

if ($Keep -gt 0) {
    Get-ChildItem $BackupDir -Filter "acciones_*.sql" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -Skip $Keep |
        Remove-Item -Force
}

Write-Host "Backup saved: $out"
