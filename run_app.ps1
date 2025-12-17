Write-Host "Starting CDM Reservation App Setup..." -ForegroundColor Cyan

# Check for Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Node.js not found in PATH. Frontend might fail to start." -ForegroundColor Yellow
}

# Backend Setup
Write-Host "`n[1/2] Setting up Backend..." -ForegroundColor Cyan
cd backend
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}
.\venv\Scripts\activate

# Smart Dependency Check with Version Fix
Write-Host "Checking dependencies..."
try {
    # Check if bcrypt is the correct version (3.2.0)
    python -c "import bcrypt; assert bcrypt.__version__ == '3.2.0'"
    python -c "import fastapi; import uvicorn; import sqlalchemy; import jose; import passlib; import requests"
    Write-Host "Dependencies verified (bcrypt 3.2.0 detected)." -ForegroundColor Green
} catch {
    Write-Host "Incompatible or missing dependencies detected. Installing/Fixing..." -ForegroundColor Yellow
    # Retry loop for flaky connection
    for ($i=1; $i -le 3; $i++) {
        try {
            pip install -r requirements.txt
            break
        } catch {
            Write-Host "Install failed (Attempt $i/3). Retrying..." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
}

Write-Host "Starting Backend Server..." -ForegroundColor Green

# Use absolute path or relative from backend folder? We are in backend folder because of 'cd backend' above.
if (Test-Path "patch_db.py") {
    Write-Host "🛠️ Patching Database Schema..." -ForegroundColor Yellow
    python patch_db.py
}

Start-Process -FilePath "uvicorn" -ArgumentList "main:app --reload" -NoNewWindow
cd ..

# Frontend Setup
Write-Host "`n[2/2] Setting up Frontend..." -ForegroundColor Cyan
cd frontend
if (Get-Command npm -ErrorAction SilentlyContinue) {
    if (!(Test-Path "node_modules")) {
        Write-Host "Installing dependencies (first run)..."
        npm install
    } else {
        Write-Host "node_modules found. Skipping npm install." -ForegroundColor Green
    }
    
    Write-Host "Starting Frontend Server..." -ForegroundColor Green
    npm run dev
} else {
    Write-Host "ERROR: npm not found. Please ensure Node.js is installed and in your PATH." -ForegroundColor Red
}
