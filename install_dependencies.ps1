param(
    [string]$VenvName = ".venv",
    [switch]$ForcePythonInstall
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[setup] $Message" -ForegroundColor Cyan
}

function Find-Python {
    $candidates = @()

    $commands = @("python", "py")
    foreach ($command in $commands) {
        try {
            $cmd = Get-Command $command -ErrorAction Stop
            if ($cmd -and $cmd.Source) {
                $candidates += $cmd.Source
            }
        } catch {
        }
    }

    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python310\python.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $candidates += $path
        }
    }

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        try {
            & $candidate --version | Out-Null
            return $candidate
        } catch {
        }
    }

    return $null
}

function Install-Python {
    Write-Step "Python was not found. Attempting install via winget."

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "Python is missing and winget is not available. Install Python 3.10+ manually, then rerun this script."
    }

    & winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Step "Looking for Python."
$pythonExe = Find-Python

if (-not $pythonExe -or $ForcePythonInstall) {
    Install-Python
    $pythonExe = Find-Python
}

if (-not $pythonExe) {
    throw "Python is still not available after installation attempt. Open a new terminal and rerun this script."
}

Write-Step "Using Python at $pythonExe"

$venvPath = Join-Path $projectRoot $VenvName
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Step "Creating virtual environment at $venvPath"
    & $pythonExe -m venv $venvPath
} else {
    Write-Step "Virtual environment already exists at $venvPath"
}

Write-Step "Upgrading pip"
& $venvPython -m pip install --upgrade pip

Write-Step "Installing project requirements"
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Write-Step "Creating .env from .env.example"
    Copy-Item ".env.example" ".env"
}

Write-Step "Setup complete."
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Activate the virtual environment:"
Write-Host "   $VenvName\Scripts\Activate.ps1"
Write-Host "2. Fill in API keys in .env if needed."
Write-Host "3. Run the app:"
Write-Host "   $VenvName\Scripts\python.exe app.py"
