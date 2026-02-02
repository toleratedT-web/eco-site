# build.ps1 - Build executable from Flask app
$projectRoot = $PSScriptRoot


# Create a clean build (optional - removes previous builds)
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Run PyInstaller with optimized settings for Flask
# Removed --windowed to show console for debugging
python -m PyInstaller `
  --name "ncd_matthew" `
  --onefile `
  --add-data "app/templates:app/templates" `
  --add-data "app/static:app/static" `
  --hidden-import flask `
  --hidden-import flask_login `
  --hidden-import flask_mail `
  --hidden-import flask_sqlalchemy `
  --hidden-import flask_wtf `
  --hidden-import flask_migrate `
  --collect-all flask `
  --collect-all wtforms `
  "$projectRoot\run.py"

Write-Host "Build complete! Your executable is in the 'dist' folder."