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

echo [1/3] Dang cap nhat thu vien va cai dat PyInstaller...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt" pyinstaller
if errorlevel 1 goto install_error

echo.
echo [2/3] Dang dong goi phan mem thanh file .exe doc lap...
python "%~dp0build_exe.py"
if errorlevel 1 goto build_error

echo.
echo [3/3] Dong goi thanh cong!
echo ----------------------------------------------------------------------
echo Thu muc ung dung da san sang tai: dist\TraCuuBanVePDF\
echo File chay chinh: dist\TraCuuBanVePDF\TraCuuBanVePDF.exe
echo.
echo Ban co the:
echo 1. Chep thu muc 'dist\TraCuuBanVePDF' vao USB de mang sang may khac dung ngay.
echo 2. Hoac mo file 'installer_script.iss' bang Inno Setup de tao Setup.exe.
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
