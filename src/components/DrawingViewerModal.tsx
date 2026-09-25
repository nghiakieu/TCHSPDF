import React from 'react';
import { X, FileText, ExternalLink, Bookmark, CheckCircle } from 'lucide-react';
import { BookmarkRow } from '../data/mockData';

interface DrawingViewerModalProps {
  bookmark: BookmarkRow | null;
  onClose: () => void;
}

export const DrawingViewerModal: React.FC<DrawingViewerModalProps> = ({ bookmark, onClose }) => {
  if (!bookmark) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-[2px] p-4">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-2xl border border-[#E4E7EE] overflow-hidden flex flex-col h-[82vh]">
        {/* Header */}
        <div className="px-5 py-3 border-b border-[#E4E7EE] bg-[#F8FAFD] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="p-1.5 bg-[#EAF2FF] text-[#2563EB] rounded-md">
              <FileText className="w-4 h-4" />
            </span>
            <div>
              <h3 className="text-[13.5px] font-bold text-[#1E293B] flex items-center gap-2">
                {bookmark.title}
                <span className="text-[11px] font-normal px-2 py-0.5 rounded-full bg-[#EAF2FF] text-[#2563EB]">
                  Trang {bookmark.page}
                </span>
              </h3>
              <p className="text-[11px] text-[#64748B] font-mono">{bookmark.pdf_path}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-[#64748B] hover:text-[#1E293B] rounded hover:bg-[#E4E7EE]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Drawing Canvas / Mock Sheet Representation */}
        <div className="flex-1 bg-[#F1F5F9] p-6 overflow-auto flex items-center justify-center">
          <div className="w-full max-w-2xl bg-white aspect-[1.414/1] shadow-md border border-[#D2D7E2] rounded p-6 flex flex-col justify-between relative select-none">
            {/* Corner CAD info block */}
            <div className="flex justify-between items-start border-b border-dashed border-[#CBD5E1] pb-3">
              <div>
                <span className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase">
                  HỒ SƠ BẢN VẼ KỸ THUẬT XÂY DỰNG
                </span>
                <h2 className="text-[16px] font-extrabold text-[#1E293B] mt-0.5">
                  {bookmark.title}
                </h2>
                {bookmark.parent_path && (
                  <span className="text-[11.5px] text-[#64748B]">Mục: {bookmark.parent_path}</span>
                )}
              </div>
              <div className="text-right">
                <span className="px-2 py-0.5 rounded bg-[#2563EB] text-white text-[11px] font-bold">
                  BẢN VẼ SỐ: {bookmark.page}
                </span>
                <p className="text-[10px] text-[#64748B] mt-1">TỈ LỆ: 1/100</p>
              </div>
            </div>

            {/* Drawing Blueprint Graphic Representation */}
            <div className="my-auto py-8 flex flex-col items-center justify-center text-center">
              <div className="w-48 h-32 border-2 border-[#94A3B8] border-dashed rounded flex flex-col items-center justify-center bg-[#F8FAFC] relative">
                <div className="absolute inset-2 border border-[#CBD5E1]"></div>
                <Bookmark className="w-8 h-8 text-[#2563EB] mb-1" />
                <span className="text-[12px] font-bold text-[#334155]">{bookmark.pdf_name}</span>
                <span className="text-[10px] text-[#64748B]">Nhảy đến trang {bookmark.page}</span>
              </div>
              <p className="text-[11.5px] text-[#64748B] mt-4 max-w-md">
                Lệnh gọi mở PDF thực tế trên máy tính đã gửi tín hiệu tới trình đọc PDF (SumatraPDF, Foxit, Acrobat...) để nhảy trực tiếp đến trang {bookmark.page}.
              </p>
            </div>

            {/* Title block frame typical in CAD/PDF drawings */}
            <div className="border border-[#1E293B] grid grid-cols-4 text-[10px] divide-x divide-[#1E293B] bg-white">
              <div className="p-2">
                <p className="text-[#64748B]">CÔNG TRÌNH:</p>
                <p className="font-bold text-[#1E293B] truncate">NHÀ PHỐ HIỆN ĐẠI</p>
              </div>
              <div className="p-2">
                <p className="text-[#64748B]">HẠNG MỤC:</p>
                <p className="font-bold text-[#1E293B] truncate">
                  {bookmark.groups[0] || 'KIẾN TRÚC & KẾT CẤU'}
                </p>
              </div>
              <div className="p-2">
                <p className="text-[#64748B]">GIAI ĐOẠN:</p>
                <p className="font-bold text-[#1E293B]">THIẾT KẾ THI CÔNG</p>
              </div>
              <div className="p-2 bg-[#F8FAFD] flex items-center justify-center">
                <span className="font-bold text-[#2563EB]">TRANG {bookmark.page}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#E4E7EE] bg-white flex items-center justify-between">
          <span className="text-[12px] text-[#10B981] flex items-center gap-1.5 font-medium">
            <CheckCircle className="w-4 h-4" />
            Đã kết nối bookmark thành công với file PDF
          </span>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-1.5 text-[12px] bg-[#2563EB] text-white rounded hover:bg-[#1D4ED8]"
            >
              Đóng xem trước
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
