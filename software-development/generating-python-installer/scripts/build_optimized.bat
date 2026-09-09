@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Nuitka optimized build (production strategy)
echo ========================================

REM === Configuration area (edit these three lines for your project) ===
set APP_NAME=YourAppName
set MAIN_FILE=main.py
set ICON_FILE=icon.ico

REM === Auto-detect CPU core count ===
REM Use the built-in Windows env var. wmic was removed in Win11 22H2+; a failed
REM probe would silently compile single-threaded with --jobs=0.
set CPU_CORES=%NUMBER_OF_PROCESSORS%
if not defined CPU_CORES set CPU_CORES=4
set /a BUILD_JOBS=%CPU_CORES%

REM === Production-verified module exclusion list ===
set EXCLUDE_MODULES=unittest,test,pytest,_pytest,doctest,pdb,pdbpp
set EXCLUDE_MODULES=%EXCLUDE_MODULES%,setuptools,pip,distutils,pkg_resources
set EXCLUDE_MODULES=%EXCLUDE_MODULES%,email.mime,http.server,xmlrpc,pydoc

echo.
echo [1/4] Cleaning previous build...
if exist dist rd /s /q dist
if exist build rd /s /q build

echo.
echo [2/4] Compiling with Nuitka (production optimization strategy)...
echo - CPU cores: %CPU_CORES% (using %BUILD_JOBS% threads)
echo - Module exclusions: %EXCLUDE_MODULES%
echo.

nuitka --standalone ^
    --windows-console-mode=disable ^
    --lto=yes ^
    --jobs=%BUILD_JOBS% ^
    --enable-plugin=anti-bloat ^
    --enable-plugin=tk-inter ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --nofollow-import-to=%EXCLUDE_MODULES% ^
    --python-flag=no_docstrings ^
    --output-dir=dist ^
    --windows-icon-from-ico=%ICON_FILE% ^
    --remove-output ^
    %MAIN_FILE%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Compilation failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Measuring build output...
for /f %%a in ('powershell -NoProfile -Command "(Get-ChildItem -LiteralPath 'dist\%APP_NAME%.dist' -Recurse -File | Measure-Object -Property Length -Sum).Sum"') do set TOTAL_SIZE=%%a
set TOTAL_SIZE=%TOTAL_SIZE:,=%
set /a SIZE_MB=%TOTAL_SIZE% / 1048576
echo - Build size: %SIZE_MB% MB

echo.
echo [4/4] Running dist slimming (production strategy)...
powershell -ExecutionPolicy Bypass -File "%~dp0slim_dist.ps1" -DistPath "dist\%APP_NAME%.dist"

echo.
echo ========================================
echo Build complete!
echo Next: py scripts\analyze_dlls.py dist\%APP_NAME%.dist
echo ========================================
pause
