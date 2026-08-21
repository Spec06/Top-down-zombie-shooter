<#
.\run_game.ps1 [-Entry <path>]

Sichere Startmethode für dieses Projekt (PowerShell).
- Legt bei Bedarf eine virtuelle Umgebung `.venv` an.
- Aktiviert die venv innerhalb des Skripts.
- Versucht `requirements.txt` zu installieren; bei Build-/SSL-Fehlern wechselt zu `pygame-ce`-Fallback.
- Startet `game.py` oder `Projekt\main.py` (auto-detektiert) oder den Pfad aus `-Entry`.

Beispiele:
  .\run_game.ps1          # auto-detect entry file
  .\run_game.ps1 -Entry Projekt\main.py
#>

[CmdletBinding()]
param(
    [string]$Entry = "auto"
)

function Write-Info($s) { Write-Host "[INFO]" $s }
function Write-Warn($s) { Write-Warning "[WARN] $s" }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Info "Working directory: $scriptDir"

if ($Entry -eq 'auto') {
    if (Test-Path (Join-Path $scriptDir 'game.py')) {
        $entryPath = 'game.py'
    } elseif (Test-Path (Join-Path $scriptDir 'Projekt\main.py')) {
        $entryPath = 'Projekt\main.py'
    } else {
        Write-Error "Keine Startdatei gefunden (weder 'game.py' noch 'Projekt\main.py'). Verwende -Entry <Pfad>"
        exit 1
    }
} else {
    $entryPath = $Entry
}

Write-Info "Will starten: $entryPath"

# Create virtualenv if missing
if (-not (Test-Path (Join-Path $scriptDir '.venv'))) {
    Write-Info "Erstelle virtuelle Umgebung .venv..."
    py -3 -m venv .venv
}

# Activate venv for this script
Write-Info "Aktiviere virtuelle Umgebung..."
& "$scriptDir\.venv\Scripts\Activate.ps1"

Write-Info "Upgrade pip..."
py -m pip install --upgrade pip -q

# Try installing requirements, with fallback to safe packages if install fails
$didInstall = $false
if (Test-Path (Join-Path $scriptDir 'requirements.txt')) {
    Write-Info "Installiere Abhängigkeiten aus requirements.txt..."
    try {
        py -m pip install -r requirements.txt
        $didInstall = $true
    } catch {
        Write-Warn "Fehler beim Installieren aus requirements.txt: $_"
        $err = $_.Exception.Message
        if ($err -match 'Failed to build' -or $err -match 'CERTIFICATE_VERIFY_FAILED' -or $err -match 'ssl') {
            Write-Warn "Wechsel zu sicherer Installation mit 'pygame-ce' (Fallback)."
            try {
                py -m pip install pygame-ce PyOpenGL numpy pytest -q
                $didInstall = $true
            } catch {
                Write-Warn "Fallback-Install fehlgeschlagen: $_"
            }
        }
    }
}

if (-not $didInstall) {
    Write-Info "Installiere Kernpakete (pygame-ce, PyOpenGL, numpy, pytest)..."
    try {
        py -m pip install pygame-ce PyOpenGL numpy pytest -q
    } catch {
        Write-Warn "Kerninstallation fehlgeschlagen: $_"
        Write-Warn "Versuche Standard-pygame als letzte Option..."
        py -m pip install pygame PyOpenGL numpy pytest
    }
}

Write-Info "Starte Spiel: py $entryPath"
py $entryPath
