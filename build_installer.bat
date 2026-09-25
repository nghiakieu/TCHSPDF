@echo off
setlocal
cd /d "%~dp0"
title Dong goi ung dung Tra cuu ho so PDF

echo ======================================================================
echo    CONG CU DONG GOI BO CAI DAT UNG DUNG TRA CUU HO SO PDF (WINDOWS)
echo ======================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 goto no_python

echo [1/4] Dang cap nhat thu vien va cai dat PyInstaller...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt" pyinstaller
if errorlevel 1 goto install_error

echo.
echo [2/4] Dang dong goi phan mem thanh file .exe doc lap...
python "%~dp0build_exe.py"
if errorlevel 1 goto build_error

echo.
echo [3/4] Kiem tra va tao bo cai dat Setup (Inno Setup)...
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC (
    echo Dang tao file Setup_TraCuuBanVePDF_v1.0.exe bang Inno Setup...
    "%ISCC%" "%~dp0installer_script.iss"
    if errorlevel 1 (
        echo [Canh bao] Tao bo cai dat that bai. Vui long tu mo 'installer_script.iss' bang Inno Setup.
    ) else (
        echo Thanh cong! File cai dat da duoc tao tai thu muc setup_output\
    )
) else (
    echo Khong tim thay Inno Setup 6 tren may. 
    echo Ban co the tu mo file 'installer_script.iss' bang Inno Setup de tao Setup.exe.
    echo (Tai Inno Setup tai: https://jrsoftware.org/isdl.php)
)

echo.
echo [4/4] Dong goi hoan tat!
echo ----------------------------------------------------------------------
echo Thu muc ung dung (chay truc tiep khong can cai): dist\TraCuuBanVePDF\
if defined ISCC echo File cai dat (Setup): setup_output\Setup_TraCuuBanVePDF_v1.0.exe
echo ======================================================================
echo.
pause
goto end

:no_python
echo [LOI] Khong tim thay Python tren may tinh!
echo Vui long cai dat Python tu trang: https://www.python.org
echo Khi cai dat hay tich chon vao: Add Python to PATH
echo.
pause
goto end

:install_error
echo.
echo [LOI] Khong the cai dat thu vien. Vui long kiem tra ket noi Internet.
pause
goto end

:build_error
echo.
echo [LOI] Qua trinh dong goi gap loi. Vui long xem thong bao ben tren.
pause
goto end

:end
endlocal
