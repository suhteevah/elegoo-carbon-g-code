@echo off
REM =============================================================================
REM Elegoo Centauri Carbon - STL to G-code Slicer (PETG Default)
REM =============================================================================
REM Usage:
REM   slice.bat model.stl                    (outputs model.gcode)
REM   slice.bat model.stl output.gcode       (custom output name)
REM   slice.bat model.stl output.gcode 0.16  (custom layer height)
REM =============================================================================

setlocal enabledelayedexpansion

set "SLICER=C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe"
set "PROFILE=%~dp0elegoo_centauri_carbon_petg.ini"

if "%~1"=="" (
    echo.
    echo  Elegoo Centauri Carbon - CLI Slicer
    echo  ====================================
    echo.
    echo  Usage: slice.bat ^<input.stl^> [output.gcode] [layer_height]
    echo.
    echo  Examples:
    echo    slice.bat cup.stl
    echo    slice.bat cup.stl cup_fine.gcode 0.12
    echo    slice.bat cup.stl cup_draft.gcode 0.28
    echo.
    echo  Profile: %PROFILE%
    echo  Slicer:  %SLICER%
    echo.
    exit /b 1
)

REM Check if slicer exists
if not exist "%SLICER%" (
    echo ERROR: PrusaSlicer not found at: %SLICER%
    echo Install it via: winget install Prusa3D.PrusaSlicer
    exit /b 1
)

REM Check if profile exists
if not exist "%PROFILE%" (
    echo ERROR: Profile not found at: %PROFILE%
    exit /b 1
)

REM Check if input file exists
if not exist "%~1" (
    echo ERROR: Input file not found: %~1
    exit /b 1
)

REM Set output filename
if "%~2"=="" (
    set "OUTPUT=%~dpn1.gcode"
) else (
    set "OUTPUT=%~2"
)

REM Set layer height override
set "LAYER_OPT="
if not "%~3"=="" (
    set "LAYER_OPT=--layer-height %~3"
)

echo.
echo  Slicing: %~1
echo  Output:  %OUTPUT%
if not "%~3"=="" echo  Layer:   %~3 mm
echo  Profile: PETG @ Elegoo Centauri Carbon
echo.

"%SLICER%" -g --load "%PROFILE%" %LAYER_OPT% "%~1" -o "%OUTPUT%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo  SUCCESS: G-code saved to %OUTPUT%
    echo.
) else (
    echo.
    echo  ERROR: Slicing failed with error code %ERRORLEVEL%
    echo.
    exit /b %ERRORLEVEL%
)
