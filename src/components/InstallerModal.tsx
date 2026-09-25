import React from 'react';
import { Package, Download, CheckCircle, Terminal, HardDrive, X, ArrowRight } from 'lucide-react';
import { AppIcon } from './AppIcon';

interface InstallerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InstallerModal: React.FC<InstallerModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const handleDownloadZip = () => {
    const link = document.createElement('a');
    link.href = '/TraCuuBanVePDF_Installer_Package.zip';
    link.download = 'TraCuuBanVePDF_Installer_Package.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-[2px] p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-[#CBD5E1] overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#E2E8F0] bg-gradient-to-r from-[#F8FAFC] to-[#F1F5F9] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AppIcon size={32} />
            <div>
              <h3 className="text-[16px] font-bold text-[#0F172A] flex items-center gap-2">
                Xuất bản Bộ Cài Đặt Ứng Dụng Windows (.exe)
              </h3>
              <p className="text-[12px] text-[#64748B]">
                Đóng gói thành file cài đặt độc lập - cài trên bất kỳ máy tính nào cũng dùng được.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#0F172A] rounded-lg hover:bg-[#E2E8F0] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-[13px]">
          {/* Main Download Card */}
          <div className="p-5 bg-gradient-to-br from-[#EFF6FF] to-[#DBEAFE]/40 border-2 border-[#2563EB]/40 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center gap-3.5">
              <div className="w-13 h-13 rounded-2xl bg-white border border-[#CBD5E1] flex items-center justify-center shrink-0 shadow-sm p-1">
                <AppIcon size={38} />
              </div>
              <div>
                <h4 className="font-bold text-[#1E3A8A] text-[15px]">
                  Trọn bộ gói cài đặt Windows
                </h4>
                <p className="text-[12px] text-[#3B82F6] font-medium">
                  File: TraCuuBanVePDF_Installer_Package.zip (Bao gồm logo.ico mới, script .bat, Inno Setup &amp; mã nguồn)
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <a
                href="/logo.ico"
                download="logo.ico"
                className="px-3.5 py-2.5 bg-white hover:bg-[#F1F5F9] text-[#1E293B] border border-[#CBD5E1] font-semibold rounded-xl text-[12.5px] transition-all flex items-center gap-1.5 shadow-xs"
                title="Tải riêng file logo.ico chuẩn Windows"
              >
                <Download className="w-4 h-4 text-[#2563EB]" />
                <span>Tải logo.ico</span>
              </a>

              <button
                onClick={handleDownloadZip}
                className="px-5 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold rounded-xl text-[13px] shadow-md hover:shadow-lg transition-all flex items-center gap-2 shrink-0 cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Tải trọn bộ .ZIP</span>
              </button>
            </div>
          </div>

          {/* Quy trình cài đặt trên bất kỳ máy tính nào */}
          <div className="space-y-3">
            <h4 className="font-bold text-[#1E293B] text-[13.5px] flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-[#2563EB]" />
              Hướng dẫn đóng gói &amp; cài đặt trên máy tính:
            </h4>

            <div className="space-y-2.5">
              <div className="p-3.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-[#2563EB] text-white text-[12px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  1
                </span>
                <div>
                  <p className="font-semibold text-[#1E293B]">
                    Giải nén file ZIP vừa tải về
                  </p>
                  <p className="text-[12px] text-[#64748B] mt-0.5">
                    Nhấp chuột phải vào <code className="bg-white px-1.5 py-0.5 border rounded text-[#2563EB]">TraCuuBanVePDF_Installer_Package.zip</code> và chọn <b>Extract All...</b> (Giải nén).
                  </p>
                </div>
              </div>

              <div className="p-3.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-[#2563EB] text-white text-[12px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  2
                </span>
                <div>
                  <p className="font-semibold text-[#1E293B]">
                    Nhấp đúp chuột vào file: <span className="text-[#2563EB]">build_installer.bat</span>
                  </p>
                  <p className="text-[12px] text-[#64748B] mt-0.5">
                    File này sẽ tự động đóng gói ứng dụng thành file <code className="bg-white px-1.5 py-0.5 border rounded text-[#059669] font-bold">TraCuuBanVePDF.exe</code> độc lập (chạy không cần cài Python).
                  </p>
                </div>
              </div>

              <div className="p-3.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-[#2563EB] text-white text-[12px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  3
                </span>
                <div>
                  <p className="font-semibold text-[#1E293B]">
                    Xuất bản thành file cài đặt Setup_TraCuuBanVePDF_v1.0.exe (Inno Setup)
                  </p>
                  <p className="text-[12px] text-[#64748B] mt-0.5">
                    Mở file <code className="bg-white px-1.5 py-0.5 border rounded text-[#2563EB]">installer_script.iss</code> bằng phần mềm <b>Inno Setup</b> (miễn phí), bấm <b>Build &gt; Compile</b>. Bạn sẽ nhận được file cài đặt chuyên nghiệp có icon ngoài Desktop, khởi động cùng Windows, và gỡ cài đặt sạch sẽ trong Control Panel.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Các ưu điểm khi đóng gói */}
          <div className="p-4 bg-[#F0FDF4] border border-[#BBF7D0] rounded-xl space-y-1.5 text-[12px] text-[#166534]">
            <p className="font-bold flex items-center gap-1.5 text-[12.5px]">
              <CheckCircle className="w-4 h-4 text-[#16A34A]" />
              Đặc điểm bộ cài đặt được đóng gói:
            </p>
            <ul className="list-disc list-inside space-y-1 text-[#15803D]">
              <li>Mang sang bất kỳ máy tính Windows nào (kể cả máy cơ quan không có quyền cài Python) đều mở lên dùng ngay.</li>
              <li>Tự động gắn Logo phần mềm sắc nét vào thanh Taskbar và góc Khay hệ thống.</li>
              <li>Chạy ngầm êm ái, người dùng bấm <b>Shift Shift</b> ở bất kỳ đâu để gọi tìm kiếm bản vẽ.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-[#E2E8F0] bg-[#F8FAFC] flex items-center justify-between">
          <span className="text-[12px] text-[#64748B]">
            Hỗ trợ tất cả các phiên bản Windows 7, 8, 10, 11 (64-bit &amp; 32-bit).
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-[12.5px] bg-[#E2E8F0] hover:bg-[#CBD5E1] text-[#1E293B] font-medium rounded-lg transition-colors"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};
