import React, { useState } from 'react';
import { FileCode, Download, Copy, Check, X } from 'lucide-react';
import { AppIcon } from './AppIcon';

interface SourceCodeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SourceCodeModal: React.FC<SourceCodeModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<
    'bookmark_app' | 'app_icon' | 'installer_bat' | 'build_exe' | 'installer_iss' | 'pdf_parser' | 'text_search' | 'requirements'
  >('bookmark_app');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const files = {
    bookmark_app: {
      name: 'bookmark_app.py',
      desc: 'Ứng dụng chính Tkinter (logo phần mềm trên Taskbar, khay hệ thống, chuyển đổi ẩn/hiện, ghim công cụ...).',
      downloadUrl: '/bookmark_app.py',
    },
    app_icon: {
      name: 'app_icon.png',
      desc: 'Biểu tượng logo phần mềm màu sắc rõ nét dùng cho thanh Taskbar, khay hệ thống (System Tray) và cửa sổ ứng dụng.',
      downloadUrl: '/app_icon.png',
    },
    installer_bat: {
      name: 'build_installer.bat',
      desc: 'Script 1-click đóng gói ứng dụng thành file .exe độc lập hoặc bộ cài đặt tự động cho Windows.',
      downloadUrl: '/build_installer.bat',
    },
    build_exe: {
      name: 'build_exe.py',
      desc: 'Script PyInstaller tự động biên dịch ứng dụng thành file thực thi TraCuuBanVePDF.exe độc lập.',
      downloadUrl: '/build_exe.py',
    },
    installer_iss: {
      name: 'installer_script.iss',
      desc: 'Kịch bản Inno Setup để xuất bản bộ cài đặt Setup_TraCuuBanVePDF_v1.0.exe (có icon Desktop, chạy cùng Windows).',
      downloadUrl: '/installer_script.iss',
    },
    pdf_parser: {
      name: 'pdf_bookmark_parser.py',
      desc: 'Module phân tích đọc bookmark (outline) trực tiếp từ file PDF với pikepdf.',
      downloadUrl: '/pdf_bookmark_parser.py',
    },
    text_search: {
      name: 'text_search.py',
      desc: 'Thuật toán tìm kiếm linh động chuẩn tiếng Việt, không phân biệt hoa/thường, bỏ dấu tiếng Việt, xếp hạng Listary.',
      downloadUrl: '/text_search.py',
    },
    requirements: {
      name: 'requirements.txt',
      desc: 'Các gói thư viện Python cần thiết (pikepdf, pandas, pystray, Pillow, keyboard, pyinstaller).',
      downloadUrl: '/requirements.txt',
    },
  };

  const currentFile = files[activeTab];

  const handleDownload = (filename: string) => {
    const element = document.createElement('a');
    element.setAttribute('href', `/${filename}`);
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-[2px] p-4">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-2xl border border-[#E4E7EE] overflow-hidden flex flex-col h-[85vh]">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-[#E4E7EE] bg-[#F8FAFD] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-[#2563EB]" />
            <div>
              <h3 className="text-[14px] font-bold text-[#1E293B]">
                Mã nguồn Python đã cập nhật (5 mục chỉnh sửa)
              </h3>
              <p className="text-[11.5px] text-[#64748B]">
                File hoàn chỉnh sẵn sàng tải về chạy trực tiếp trên máy tính.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-[#64748B] hover:text-[#1E293B] rounded hover:bg-[#E4E7EE]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[#E4E7EE] bg-[#F1F5F9] px-4 pt-2 gap-1">
          {(Object.keys(files) as Array<keyof typeof files>).map((key) => {
            const f = files[key];
            const isActive = activeTab === key;
            return (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`px-3.5 py-1.5 text-[12px] font-medium rounded-t border-t border-x transition-colors ${
                  isActive
                    ? 'bg-white border-[#E4E7EE] text-[#2563EB] font-bold shadow-sm'
                    : 'border-transparent text-[#64748B] hover:text-[#1E293B] hover:bg-white/50'
                }`}
              >
                {f.name}
              </button>
            );
          })}
        </div>

        {/* File description & actions bar */}
        <div className="px-5 py-2.5 bg-white border-b border-[#E4E7EE] flex items-center justify-between">
          <span className="text-[12px] text-[#475569]">{currentFile.desc}</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleDownload(currentFile.name)}
              className="px-3 py-1 bg-[#2563EB] text-white text-[11.5px] rounded hover:bg-[#1D4ED8] flex items-center gap-1.5 font-medium transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Tải file {currentFile.name}
            </button>
          </div>
        </div>

        {/* Code View Area */}
        <div className="flex-1 bg-[#1E293B] text-[#F8FAFC] p-4 overflow-auto font-mono text-[12px] leading-relaxed">
          <pre className="select-text">
            {activeTab === 'bookmark_app' && `# Xem trực tiếp file: /bookmark_app.py
# Đã cập nhật đầy đủ 5 yêu cầu của bạn:
# 1. Bật thanh tìm kiếm nhanh thì ẩn bảng điều khiển đầy đủ (withdraw) và ngược lại (deiconify).
# 2. Khi thêm nhiều nhóm: phần CÔNG CỤ được pack ở BOTTOM (không bao giờ bị che khuất).
#    Căn lề các nút chức năng sang bên trái cho đều và đẹp.
#    Nút "＋ Thêm file PDF" bỏ màu nền, dùng style secondary đồng bộ các nút khác.
# 3. Hộp thoại "Danh sách file PDF đã thêm": dòng nhắc nhở giữ gọn trên 1 dòng duy nhất.
#    Highlight khi chọn được đổi sang màu #CFE4FF rõ nét, tương phản trên nền sáng.
# 4. Hộp thoại chính: bỏ dòng "Tra cứu hồ sơ Bản vẽ PDF" trùng lặp dưới title.
#    Chỉnh lại cỡ chữ, kích thước nút nhấn hài hòa theo Listary.
# 5. Thanh tìm kiếm nhanh: bo 4 góc xung quanh đẹp mắt, bỏ dòng "Gõ để tìm...",
#    đổi biểu tượng tìm kiếm sang ký hiệu thanh mảnh ⌕ phù hợp nền sáng.
`}
            {activeTab === 'app_icon' && (
              <div className="font-sans space-y-4">
                <div className="flex items-center gap-5 p-4 rounded-xl bg-[#0F172A] border border-[#334155]">
                  <div className="w-20 h-20 bg-white rounded-2xl p-2 flex items-center justify-center shadow-lg">
                    <AppIcon size={64} />
                  </div>
                  <div>
                    <h4 className="text-white font-bold text-[15px]">Biểu tượng Logo mới (PDF đỏ + Kính lúp xanh cán cam)</h4>
                    <p className="text-slate-300 text-[12px] mt-1">
                      Đã cập nhật đồng bộ các định dạng: <b>logo.ico</b> (multi-resolution), <b>app_icon.png</b>, <b>app_icon.svg</b>.
                    </p>
                    <div className="flex items-center gap-2 mt-3">
                      <a
                        href="/logo.ico"
                        download="logo.ico"
                        className="px-3 py-1 bg-[#2563EB] hover:bg-[#1D4ED8] text-white rounded text-[11px] font-semibold flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" /> Tải logo.ico
                      </a>
                      <a
                        href="/app_icon.svg"
                        download="app_icon.svg"
                        className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-[11px] font-semibold flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" /> Tải app_icon.svg
                      </a>
                    </div>
                  </div>
                </div>
                <pre className="text-slate-300 text-[12px] font-mono leading-relaxed select-text whitespace-pre-wrap">
{`# Ứng dụng tự động dùng logo mới này cho:
# 1. Biểu tượng cửa sổ ứng dụng (Titlebar & Taskbar Windows).
# 2. Biểu tượng chạy ngầm trên Khay hệ thống (System Tray).
# 3. Biểu tượng file cài đặt .exe độc lập xuất bản từ PyInstaller & Inno Setup.
# 4. Favicon trình duyệt web (app_icon.svg, app_icon.png).`}
                </pre>
              </div>
            )}
            {activeTab === 'installer_bat' && `@echo off
chcp 65001 >nul
title Đóng gói ứng dụng Tra cứu hồ sơ Bản vẽ PDF

echo ======================================================================
echo    CÔNG CỤ ĐÓNG GÓI BỘ CÀI ĐẶT ỨNG DỤNG TRA CỨU BẢN VẼ PDF (WINDOWS)
echo ======================================================================
echo [1/3] Đang cập nhật thư viện và cài đặt PyInstaller...
pip install --upgrade pip
pip install -r requirements.txt pyinstaller

echo [2/3] Đang đóng gói phần mềm thành file thực thi độc lập (TraCuuBanVePDF.exe)...
python build_exe.py

echo [3/3] Đóng gói thành công!
echo Thư mục ứng dụng đã sẵn sàng tại: dist\\TraCuuBanVePDF\\
echo File chạy chính: dist\\TraCuuBanVePDF\\TraCuuBanVePDF.exe
pause`}
            {activeTab === 'build_exe' && `import os, sys, shutil, subprocess
from pathlib import Path

# Biên dịch ứng dụng thành file độc lập với PyInstaller
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--name=TraCuuBanVePDF",
    "--icon=app_icon.ico",
    "bookmark_app.py"
]
subprocess.check_call(cmd)`}
            {activeTab === 'installer_iss' && `; Inno Setup Script tạo bộ cài đặt Setup_TraCuuBanVePDF_v1.0.exe
#define MyAppName "Tra cứu hồ sơ Bản vẽ PDF"
#define MyAppVersion "1.0.0"
#define MyAppExeName "TraCuuBanVePDF.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\\{#MyAppName}
OutputDir=setup_output
OutputBaseFilename=Setup_TraCuuBanVePDF_v1.0
SetupIconFile=app_icon.ico`}
            {activeTab === 'pdf_parser' && `# Xem trực tiếp file: /pdf_bookmark_parser.py
# Đọc trực tiếp bookmark (outlines) từ PDF bằng pikepdf.`}
            {activeTab === 'text_search' && `# Xem trực tiếp file: /text_search.py
# Thuật toán tìm kiếm linh động chuẩn tiếng Việt, bỏ dấu, xếp hạng Listary.`}
            {activeTab === 'requirements' && `pikepdf>=8.0
pandas>=2.0
pystray>=0.19.5
Pillow>=10.0
keyboard>=0.13.5
pyinstaller>=6.0`}
          </pre>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#E4E7EE] bg-[#F8FAFD] flex items-center justify-between">
          <span className="text-[11.5px] text-[#64748B]">
            Các file Python này được lưu đồng thời trong thư mục gốc của dự án.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-[12px] bg-[#E4E7EE] hover:bg-[#D2D7E2] text-[#1E293B] rounded transition-colors"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};
