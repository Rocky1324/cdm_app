Write-Host "Fixing Login/Bcrypt issue..." -ForegroundColor Cyan

cd backend
# Activate Venv
if (Test-Path "venv") {
    .\venv\Scripts\activate
} else {
    python -m venv venv
    .\venv\Scripts\activate
}

# Force remove incorrect version
Write-Host "Uninstalling incorrect bcrypt..."
pip uninstall -y bcrypt

# Install correct version
Write-Host "Installing bcrypt 3.2.0..."
pip install bcrypt==3.2.0

# Verify
try {
    python -c "import bcrypt; assert bcrypt.__version__ == '3.2.0'; print('SUCCESS: Bcrypt 3.2.0 installed.')"
    Write-Host "Fix applied successfully!" -ForegroundColor Green
    Write-Host "You can now run '.\run_app.ps1' again." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Could not verify bcrypt version." -ForegroundColor Red
}
