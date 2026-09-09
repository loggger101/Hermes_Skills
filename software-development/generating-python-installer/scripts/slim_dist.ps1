param(
    [string]$DistPath
)

$ErrorActionPreference = "Continue"  # do not silently swallow errors: a failed deletion must be visible, never masquerade as success

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "dist slimming (production strategy)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path $DistPath)) {
    Write-Host "[ERROR] Directory not found: $DistPath" -ForegroundColor Red
    exit 1
}

# Measure initial size
$InitialSize = (Get-ChildItem -Path $DistPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "`nInitial size: $([math]::Round($InitialSize, 2)) MB" -ForegroundColor Yellow

# Production profile: no .pdb, .pyi, __pycache__, test dirs, etc.
Write-Host "`n[Applying production cleanup strategy...]" -ForegroundColor Green

# 1. Remove debug symbols
Write-Host "`n[1/7] Removing .pdb debug symbols..." -ForegroundColor Green
$pdbFiles = Get-ChildItem -Path $DistPath -Recurse -Include *.pdb -File
$pdbSize = ($pdbFiles | Measure-Object -Property Length -Sum).Sum / 1MB
if ($pdbFiles.Count -gt 0) {
    $pdbFiles | Remove-Item -Force
    Write-Host "  Removed $($pdbFiles.Count) files, saved $([math]::Round($pdbSize, 2)) MB"
} else {
    Write-Host "  No .pdb files found (already optimized)" -ForegroundColor Gray
}

# 2. Remove type stubs
Write-Host "`n[2/7] Removing .pyi type stubs..." -ForegroundColor Green
$pyiFiles = Get-ChildItem -Path $DistPath -Recurse -Include *.pyi -File
$pyiSize = ($pyiFiles | Measure-Object -Property Length -Sum).Sum / 1MB
if ($pyiFiles.Count -gt 0) {
    $pyiFiles | Remove-Item -Force
    Write-Host "  Removed $($pyiFiles.Count) files, saved $([math]::Round($pyiSize, 2)) MB"
} else {
    Write-Host "  No .pyi files found (already optimized)" -ForegroundColor Gray
}

# 3. Remove __pycache__
Write-Host "`n[3/7] Removing __pycache__ caches..." -ForegroundColor Green
$pycacheDirs = Get-ChildItem -Path $DistPath -Recurse -Directory -Filter "__pycache__"
$pycacheSize = 0
foreach ($dir in $pycacheDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $pycacheSize += $size
    Remove-Item -Path $dir.FullName -Recurse -Force
}
if ($pycacheDirs.Count -gt 0) {
    Write-Host "  Removed $($pycacheDirs.Count) directories, saved $([math]::Round($pycacheSize / 1MB, 2)) MB"
} else {
    Write-Host "  No __pycache__ found (already optimized)" -ForegroundColor Gray
}

# 4. Remove test directories
Write-Host "`n[4/7] Removing test/tests directories..." -ForegroundColor Green
$testDirs = Get-ChildItem -Path $DistPath -Recurse -Directory | Where-Object { $_.Name -match '^tests?$' }
$testSize = 0
foreach ($dir in $testDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $testSize += $size
    Remove-Item -Path $dir.FullName -Recurse -Force
}
if ($testDirs.Count -gt 0) {
    Write-Host "  Removed $($testDirs.Count) directories, saved $([math]::Round($testSize / 1MB, 2)) MB"
} else {
    Write-Host "  No test directories found (already optimized)" -ForegroundColor Gray
}

# 5. Remove docs and examples
Write-Host "`n[5/7] Removing docs/examples directories..." -ForegroundColor Green
$docDirs = Get-ChildItem -Path $DistPath -Recurse -Directory | Where-Object { $_.Name -match '^(docs|examples|samples|demo)$' }
$docSize = 0
foreach ($dir in $docDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $docSize += $size
    Remove-Item -Path $dir.FullName -Recurse -Force
}
if ($docDirs.Count -gt 0) {
    Write-Host "  Removed $($docDirs.Count) directories, saved $([math]::Round($docSize / 1MB, 2)) MB"
} else {
    Write-Host "  No docs directories found (already optimized)" -ForegroundColor Gray
}

# 6. Remove .pyc bytecode
Write-Host "`n[6/7] Removing .pyc bytecode..." -ForegroundColor Green
$pycFiles = Get-ChildItem -Path $DistPath -Recurse -Include *.pyc -File
$pycSize = ($pycFiles | Measure-Object -Property Length -Sum).Sum / 1MB
if ($pycFiles.Count -gt 0) {
    $pycFiles | Remove-Item -Force
    Write-Host "  Removed $($pycFiles.Count) files, saved $([math]::Round($pycSize, 2)) MB"
} else {
    Write-Host "  No .pyc files found (already optimized)" -ForegroundColor Gray
}

# 7. Trim .dist-info metadata
Write-Host "`n[7/7] Trimming .dist-info metadata..." -ForegroundColor Green
$distInfoDirs = Get-ChildItem -Path $DistPath -Recurse -Directory -Filter "*.dist-info"
$removedCount = 0
$removedSize = 0
foreach ($infoDir in $distInfoDirs) {
    # Remove install-time bookkeeping files ONLY. Keep METADATA and entry_points.txt:
    # they are read at runtime by importlib.metadata, and deleting them breaks plugin discovery.
    $filesToRemove = @("RECORD", "INSTALLER", "direct_url.json")
    foreach ($fileName in $filesToRemove) {
        $file = Join-Path $infoDir.FullName $fileName
        if (Test-Path $file) {
            $size = (Get-Item $file).Length
            $removedSize += $size
            Remove-Item $file -Force
            $removedCount++
        }
    }
}
if ($removedCount -gt 0) {
    Write-Host "  Removed $removedCount metadata files, saved $([math]::Round($removedSize / 1MB, 2)) MB"
} else {
    Write-Host "  No cleanable metadata found (already optimized)" -ForegroundColor Gray
}

# Measure final size
$FinalSize = (Get-ChildItem -Path $DistPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
$SavedSize = $InitialSize - $FinalSize
$SavedPercent = if ($InitialSize -gt 0) { ($SavedSize / $InitialSize) * 100 } else { 0 }

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Slimming complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Initial size: $([math]::Round($InitialSize, 2)) MB" -ForegroundColor Yellow
Write-Host "Final size:   $([math]::Round($FinalSize, 2)) MB" -ForegroundColor Green
Write-Host "Saved:        $([math]::Round($SavedSize, 2)) MB ($([math]::Round($SavedPercent, 1))%)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Reference comparison
Write-Host "[Reference]" -ForegroundColor Yellow
Write-Host "Production reference build: 323 MB total (PyQt + OpenCV + Playwright heavy libs included)" -ForegroundColor Gray
Write-Host "If your project is pure Tkinter + stdlib, target should be 80-150 MB" -ForegroundColor Gray
