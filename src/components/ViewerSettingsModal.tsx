import React, { useState } from 'react';
import { Settings, X, Check } from 'lucide-react';

interface ViewerSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  viewerExe: string;
  viewerTemplate: string;
  onSave: (exe: string, template: string) => void;
}

const PRESETS: Record<string, string> = {
  'SumatraPDF (Windows)': '"{exe}" -page {page} "{file}"',
  'Foxit PhantomPDF / Foxit Reader (Windows)': '"{exe}" "{file}" /A page={page}',
  'Adobe Acrobat / Reader (Windows)': '"{exe}" /A "page={page}" "{file}"',
  'Evince (Linux)': '"{exe}" --page-index {page} "{file}"',
  'Okular (Linux)': '"{exe}" -p {page} "{file}"',
  'Xreader (Linux)': '"{exe}" --page-index {page} "{file}"',
  'Tuỳ chỉnh khác...': '"{exe}" "{file}"',
};

export const ViewerSettingsModal: React.FC<ViewerSettingsModalProps> = ({
  isOpen,
  onClose,
  viewerExe,
  viewerTemplate,
  onSave,
}) => {
  const [exe, setExe] = useState(viewerExe);
  const [template, setTemplate] = useState(viewerTemplate);

  if (!isOpen) return null;

  const handleSelectPreset = (presetName: string) => {
    if (PRESETS[presetName]) {
      setTemplate(PRESETS[presetName]);
    }
  };

  const handleSave = () => {
    onSave(exe.trim(), template.trim());
    alert('Đã lưu cấu hình phần mềm mở PDF.');
    onClose();
  };

  const handleClear = () => {
    setExe('');
    setTemplate('');
    onSave('', '');
    alert('Đã xoá cấu hình. Chương trình sẽ tự động dò phần mềm đọc PDF.');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] p-4">
      <div className="w-full max-w-xl bg-white rounded-lg shadow-2xl border border-[#E4E7EE] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-[#E4E7EE] flex items-start justify-between bg-[#F8FAFD]">
          <div>
            <h3 className="text-[14px] font-bold text-[#1E293B] flex items-center gap-2">
              <Settings className="w-4 h-4 text-[#2563EB]" strokeWidth={1.75} />
              Cấu hình phần mềm mở PDF
            </h3>
            <p className="text-[12px] text-[#64748B] mt-0.5">
              Cấu hình chương trình dùng để mở PDF và nhảy đúng trang bookmark.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[#64748B] hover:text-[#1E293B] p-1 rounded hover:bg-[#E4E7EE]/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4 text-[12.5px]">
          <div>
            <label className="block text-[#64748B] font-medium mb-1">
              Đường dẫn phần mềm đọc PDF (.exe):
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={exe}
                onChange={(e) => setExe(e.target.value)}
                placeholder="Ví dụ: C:\Program Files\SumatraPDF\SumatraPDF.exe"
                className="flex-1 px-3 py-1.5 border border-[#D2D7E2] rounded text-[12px] focus:outline-none focus:border-[#2563EB]"
              />
              <button
                type="button"
                onClick={() => {
                  const demo = 'C:/Program Files/SumatraPDF/SumatraPDF.exe';
                  setExe(demo);
                  setTemplate(PRESETS['SumatraPDF (Windows)']);
                }}
                className="px-3 py-1.5 bg-white border border-[#D2D7E2] rounded hover:bg-[#EAF2FF] text-[#1E293B] text-[12px]"
              >
                Gợi ý SumatraPDF
              </button>
            </div>
          </div>

          <div>
            <label className="block text-[#64748B] font-medium mb-1">Mẫu có sẵn:</label>
            <select
              onChange={(e) => handleSelectPreset(e.target.value)}
              className="w-full px-3 py-1.5 border border-[#D2D7E2] rounded text-[12px] bg-white focus:outline-none focus:border-[#2563EB]"
            >
              <option value="">-- Chọn phần mềm tương ứng --</option>
              {Object.keys(PRESETS).map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[#64748B] font-medium mb-1">
              Mẫu dòng lệnh ({'{exe}'}, {'{file}'}, {'{page}'}):
            </label>
            <input
              type="text"
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              placeholder='"{exe}" -page {page} "{file}"'
              className="w-full px-3 py-1.5 border border-[#D2D7E2] rounded text-[12px] font-mono focus:outline-none focus:border-[#2563EB]"
            />
          </div>

          <div className="p-3 bg-[#F8FAFD] border border-[#E4E7EE] rounded text-[11.5px] text-[#64748B]">
            💡 Để trống cả 2 ô trên nếu muốn chương trình TỰ ĐỘNG dò phần mềm đọc PDF có sẵn trên máy (SumatraPDF &gt; Foxit &gt; Acrobat &gt; Trình duyệt web).
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#E4E7EE] bg-[#F8FAFD] flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-4 py-1.5 text-[12px] bg-[#2563EB] text-white rounded hover:bg-[#1D4ED8] transition-colors font-medium flex items-center gap-1.5"
            >
              <Check className="w-3.5 h-3.5" />
              Lưu cấu hình
            </button>
            <button
              onClick={handleClear}
              className="px-3.5 py-1.5 text-[12px] bg-white border border-[#EF4444] text-[#EF4444] rounded hover:bg-[#FEE2E2] transition-colors"
            >
              Xoá cấu hình
            </button>
          </div>
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
