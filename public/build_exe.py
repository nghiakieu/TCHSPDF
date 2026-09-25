"""
Script tự động đóng gói ứng dụng 'Tra cứu hồ sơ Bản vẽ PDF' thành file thực thi (.exe) độc lập cho Windows.
Chạy: python build_exe.py
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
APP_NAME = "TraCuuBanVePDF"

def build():
    print("=" * 60)
    print("BẮT ĐẦU ĐÓNG GÓI ỨNG DỤNG THÀNH FILE .EXE CHO WINDOWS")
    print("=" * 60)

    # 1. Cài đặt các thư viện cần thiết nếu chưa có
    print("\n[1/4] Kiểm tra thư viện PyInstaller và thư viện phụ thuộc...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--upgrade",
        "pyinstaller", "pikepdf", "pandas", "pystray", "Pillow", "keyboard"
    ])

    # 2. Xóa các bản build cũ
    print("\n[2/4] Dọn dẹp thư mục bản build cũ...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR, ignore_errors=True)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # 3. Chạy PyInstaller
    icon_arg = []
    logo_ico = BASE_DIR / "logo.ico"
    app_ico = BASE_DIR / "app_icon.ico"
    png_file = BASE_DIR / "app_icon.png"
    if logo_ico.is_file():
        icon_arg = [f"--icon={logo_ico}"]
    elif app_ico.is_file():
        icon_arg = [f"--icon={app_ico}"]
    elif png_file.is_file():
        icon_arg = [f"--icon={png_file}"]

    add_data_args = [
        f"--add-data={BASE_DIR / 'pdf_bookmark_parser.py'}{os.pathsep}.",
        f"--add-data={BASE_DIR / 'text_search.py'}{os.pathsep}.",
    ]
    if logo_ico.is_file():
        add_data_args.append(f"--add-data={logo_ico}{os.pathsep}.")
    if app_ico.is_file():
        add_data_args.append(f"--add-data={app_ico}{os.pathsep}.")
    if png_file.is_file():
        add_data_args.append(f"--add-data={png_file}{os.pathsep}.")

    print("\n[3/4] Đang biên dịch mã nguồn thành file .exe độc lập (không cần cài Python)...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",                       # Đóng gói dạng thư mục hoặc đổi thành --onefile
        "--windowed",                     # Chế độ GUI không hiện màn hình đen dòng lệnh
        f"--name={APP_NAME}",
        *add_data_args,
        *icon_arg,
        str(BASE_DIR / "bookmark_app.py")
    ]

    subprocess.check_call(cmd)

    output_exe = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    print("\n[4/4] Hoàn tất đóng gói!")
    print(f"File thực thi đã sẵn sàng tại: {output_exe}")
    print("Bạn có thể chép toàn bộ thư mục 'dist/TraCuuBanVePDF' sang bất kỳ máy tính nào để chạy ngay lập tức!")

if __name__ == "__main__":
    build()
