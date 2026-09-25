import React, { useState } from 'react';
import { Keyboard, X, Check, RotateCcw } from 'lucide-react';

interface HotkeySettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentHotkey: string;
  onSave: (hotkey: string) => void;
}

export const HotkeySettingsModal: React.FC<HotkeySettingsModalProps> = ({
  isOpen,
  onClose,
  currentHotkey,
  onSave,
}) => {
  const [hotkey, setHotkey] = useState(currentHotkey || 'double_shift');

  if (!isOpen) return null;

  const displayLabel =
    hotkey === 'double_shift' ? 'Shift Shift (Bấm 2 lần liên tiếp)' : hotkey;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] p-4">
      <div className="w-full max-w-lg bg-white rounded-lg shadow-2xl border border-[#E4E7EE] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-[#E4E7EE] flex items-start justify-between bg-[#F8FAFD]">
          <div>
            <h3 className="text-[14px] font-bold text-[#1E293B] flex items-center gap-2">
              <Keyboard className="w-4 h-4 text-[#2563EB]" strokeWidth={1.75} />
              Đặt phím tắt gọi ô tìm kiếm nhanh
            </h3>
            <p className="text-[12px] text-[#64748B] mt-0.5">
              Gọi ô tìm kiếm nổi ở bất kỳ đâu trên máy tính (phong cách Listary).
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[#64748B] hover:text-[#1E293B] p-1 rounded hover:bg-[#E4E7EE]/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <label className="block text-[12px] text-[#64748B] font-medium mb-1.5">
              Phím tắt hiện tại:
            </label>
            <div className="p-4 bg-[#F8FAFD] border-2 border-[#2563EB]/40 rounded-lg text-center font-bold text-[15px] text-[#2563EB]">
              {displayLabel}
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-[12px] font-medium text-[#64748B]">Chọn phím tắt nhanh:</span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setHotkey('double_shift')}
                className={`px-3 py-2 text-[12px] rounded border transition-colors text-left flex items-center justify-between ${
                  hotkey === 'double_shift'
                    ? 'bg-[#CFE4FF] border-[#2563EB] text-[#0A2540] font-bold'
                    : 'bg-white border-[#D2D7E2] hover:bg-[#F1F5F9] text-[#1E293B]'
                }`}
              >
                <span>Shift Shift (Listary)</span>
                {hotkey === 'double_shift' && <Check className="w-3.5 h-3.5 text-[#2563EB]" />}
              </button>

              <button
                type="button"
                onClick={() => setHotkey('ctrl+alt+space')}
                className={`px-3 py-2 text-[12px] rounded border transition-colors text-left flex items-center justify-between ${
                  hotkey === 'ctrl+alt+space'
                    ? 'bg-[#CFE4FF] border-[#2563EB] text-[#0A2540] font-bold'
                    : 'bg-white border-[#D2D7E2] hover:bg-[#F1F5F9] text-[#1E293B]'
                }`}
              >
                <span>Ctrl + Alt + Space</span>
                {hotkey === 'ctrl+alt+space' && <Check className="w-3.5 h-3.5 text-[#2563EB]" />}
              </button>

              <button
                type="button"
                onClick={() => setHotkey('alt+space')}
                className={`px-3 py-2 text-[12px] rounded border transition-colors text-left flex items-center justify-between ${
                  hotkey === 'alt+space'
                    ? 'bg-[#CFE4FF] border-[#2563EB] text-[#0A2540] font-bold'
                    : 'bg-white border-[#D2D7E2] hover:bg-[#F1F5F9] text-[#1E293B]'
                }`}
              >
                <span>Alt + Space</span>
                {hotkey === 'alt+space' && <Check className="w-3.5 h-3.5 text-[#2563EB]" />}
              </button>

              <button
                type="button"
                onClick={() => setHotkey('ctrl+shift+f')}
                className={`px-3 py-2 text-[12px] rounded border transition-colors text-left flex items-center justify-between ${
                  hotkey === 'ctrl+shift+f'
                    ? 'bg-[#CFE4FF] border-[#2563EB] text-[#0A2540] font-bold'
                    : 'bg-white border-[#D2D7E2] hover:bg-[#F1F5F9] text-[#1E293B]'
                }`}
              >
                <span>Ctrl + Shift + F</span>
                {hotkey === 'ctrl+shift+f' && <Check className="w-3.5 h-3.5 text-[#2563EB]" />}
              </button>
            </div>
          </div>

          <div className="p-3 bg-[#F8FAFD] border border-[#E4E7EE] rounded text-[11.5px] text-[#64748B]">
            💡 Trong ứng dụng Python chạy ngầm trên Windows, bạn có thể gõ đúp phím Shift ở bất kỳ ứng dụng nào (AutoCAD, Word, Excel...) để lập tức mở ô tìm kiếm hồ sơ bản vẽ.
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#E4E7EE] bg-[#F8FAFD] flex items-center justify-between">
          <button
            onClick={() => setHotkey('double_shift')}
            className="px-3 py-1.5 text-[12px] bg-white border border-[#D2D7E2] rounded hover:bg-[#F1F5F9] text-[#64748B] flex items-center gap-1.5"
          >
            <RotateCcw className="w-3 h-3" />
            Mặc định (Shift Shift)
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 text-[12px] text-[#64748B] hover:text-[#1E293B]"
            >
              Hủy
            </button>
            <button
              onClick={() => {
                onSave(hotkey);
                alert(`Đã lưu phím tắt: ${displayLabel}`);
                onClose();
              }}
              className="px-4 py-1.5 text-[12px] bg-[#2563EB] text-white rounded hover:bg-[#1D4ED8] font-medium"
            >
              Lưu phím tắt
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
