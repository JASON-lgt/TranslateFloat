# Build portable zip for GitHub / Gitee Release
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw "Missing venv python: $Py" }

Write-Host "== install pyinstaller =="
& $Py -m pip install -U pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

# Prefer ASCII build dir to avoid Chinese-path issues
$OutRoot = "E:\translate-float-build"
if (-not (Test-Path "E:\")) { $OutRoot = Join-Path $Root "release_build" }
New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null
$Dist = Join-Path $OutRoot "dist"
$Work = Join-Path $OutRoot "work"
Remove-Item -Recurse -Force $Dist, $Work -ErrorAction SilentlyContinue

Write-Host "== pyinstaller -> $OutRoot =="
& $Py -m PyInstaller --noconfirm --clean `
  --distpath $Dist `
  --workpath $Work `
  (Join-Path $Root "translate_float.spec")

$AppDir = Join-Path $Dist "TranslateFloat"
if (-not (Test-Path (Join-Path $AppDir "TranslateFloat.exe"))) {
  throw "Build failed: exe not found in $AppDir"
}

# Side-by-side assets / docs (avoid hardcoding non-ASCII names in this script)
$AssetsOut = Join-Path $AppDir "assets"
New-Item -ItemType Directory -Force -Path $AssetsOut | Out-Null
Copy-Item -LiteralPath (Join-Path $Root "assets\donate.png") (Join-Path $AssetsOut "donate.png") -Force
Copy-Item -LiteralPath (Join-Path $Root "assets\app.ico") (Join-Path $AssetsOut "app.ico") -Force
Copy-Item -LiteralPath (Join-Path $Root "assets\app.png") (Join-Path $AssetsOut "app.png") -Force
Copy-Item -LiteralPath (Join-Path $Root "SUPPORT.md") (Join-Path $AppDir "SUPPORT.md") -Force
Copy-Item -LiteralPath (Join-Path $Root "LICENSE") (Join-Path $AppDir "LICENSE") -Force
Get-ChildItem -LiteralPath $Root -Filter "*.txt" -File | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $AppDir $_.Name) -Force
}
Copy-Item -LiteralPath (Join-Path $Root "RELEASE.md") (Join-Path $AppDir "RELEASE.md") -Force -ErrorAction SilentlyContinue

# version from branding
$Ver = & $Py -c "from services.branding import APP_VERSION; print(APP_VERSION)"
$ZipName = "TranslateFloat-v$Ver-windows-x64.zip"
$ZipPath = Join-Path $OutRoot $ZipName
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

Write-Host "== zip $ZipPath =="
Compress-Archive -Path $AppDir -DestinationPath $ZipPath -Force

$Hash = (Get-FileHash -Algorithm SHA256 $ZipPath).Hash
$HashFile = "$ZipPath.sha256"
Set-Content -Path $HashFile -Value "$Hash  $ZipName" -Encoding ASCII

Write-Host ""
Write-Host "DONE"
Write-Host "ZIP : $ZipPath"
Write-Host "SHA256: $Hash"
Write-Host "Upload this zip + sha256 to GitHub/Gitee Release."
