#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the AI Kitchen Platform for local development (no Docker required).
    Uses Python 3.11, SQLite, and npm dev server.
.USAGE
    .\start-dev.ps1
#>

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$VenvDir = Join-Path $BackendDir ".venv"
$ReqFile = Join-Path $Root "requirements-dev.txt"

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  AI Kitchen Platform — Local Dev Startup" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Create Python 3.11 virtual environment ─────────────────────────────────
if (-not (Test-Path $VenvDir)) {
    Write-Host "[1/5] Creating Python 3.11 virtual environment..." -ForegroundColor Yellow
    py -3.11 -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Could not create venv with Python 3.11" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/5] Virtual environment already exists — skipping." -ForegroundColor Green
}

$PipExe  = Join-Path $VenvDir "Scripts\pip.exe"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$UvicornExe = Join-Path $VenvDir "Scripts\uvicorn.exe"

# ── 2. Install backend dependencies ──────────────────────────────────────────
Write-Host "[2/5] Installing backend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
& $PipExe install --quiet --upgrade pip
& $PipExe install --quiet -r $ReqFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Check requirements-dev.txt." -ForegroundColor Red
    exit 1
}
Write-Host "      Backend dependencies installed." -ForegroundColor Green

# ── 3. Seed the database ──────────────────────────────────────────────────────
Write-Host "[3/5] Seeding SQLite database..." -ForegroundColor Yellow
Push-Location $BackendDir
& $PythonExe database/seed.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Seed script failed or already seeded — continuing." -ForegroundColor DarkYellow
}
Pop-Location

# ── 4. Install frontend dependencies ─────────────────────────────────────────
Write-Host "[4/5] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    npm install --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: npm install failed." -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "      node_modules already exists — skipping." -ForegroundColor Green
}
Pop-Location

# ── 5. Start backend + frontend ──────────────────────────────────────────────
Write-Host "[5/5] Starting services..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Backend  → http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs → http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Frontend → http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop all services." -ForegroundColor Gray
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Start backend in a new PowerShell window
$BackendCmd = "Set-Location '$BackendDir'; & '$UvicornExe' main:app --reload --port 8000"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $BackendCmd -WindowStyle Normal

# Give backend a moment to start
Start-Sleep -Seconds 2

# Start frontend in foreground (blocks until Ctrl+C)
Push-Location $FrontendDir
npm run dev
Pop-Location
