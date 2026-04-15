@echo off
REM =============================================================================
REM Batch slicer - Slices ALL project STL files
REM =============================================================================
setlocal enabledelayedexpansion

set "SLICER=C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe"
set "PROFILE=%~dp0elegoo_centauri_carbon_petg.ini"
set "PROJECTS=%~dp0projects"
set COUNT=0
set FAIL=0

echo.
echo  ============================================
echo   BATCH SLICER - Elegoo Centauri Carbon PETG
echo  ============================================
echo.

for /R "%PROJECTS%" %%F in (*.stl) do (
    set "STL=%%F"
    set "GCODE=%%~dpnF.gcode"
    echo  Slicing: %%~nxF
    "%SLICER%" -g --load "%PROFILE%" "%%F" -o "%%~dpnF.gcode" >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo    OK -> %%~nxF.gcode
        set /a COUNT+=1
    ) else (
        echo    FAIL
        set /a FAIL+=1
    )
)

echo.
echo  ============================================
echo   Done: !COUNT! succeeded, !FAIL! failed
echo  ============================================
