@echo off
setlocal
cd /d "%~dp0"
title Tra cuu ho so PDF

python --version >nul 2>&1
if errorlevel 1 goto no_python

python "%~dp0bookmark_app.py"
if errorlevel 1 goto run_error
goto end

:no_python
echo ==============================================================
echo [LOI] Khong tim thay Python tren may tinh!
echo Vui long cai dat Python tu trang: https://www.python.org
echo Khi cai dat hay tich chon vao: Add Python to PATH
echo ==============================================================
echo.
pause
goto end

:run_error
echo.
echo ==============================================================
echo [THONG BAO] Chuong trinh gap loi khi khoi dong.
echo Vui long kiem tra lai thong bao loi o tren.
echo Neu thieu thu vien, hay chay file: build_installer.bat
echo Hoac go lenh: pip install -r requirements.txt
echo ==============================================================
echo.
pause
goto end

:end
endlocal
