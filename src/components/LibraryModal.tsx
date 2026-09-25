import React, { useState } from 'react';
import { LibraryFile } from '../data/mockData';
import { Folder, X, RefreshCw, FolderPlus, Trash2, Check } from 'lucide-react';

interface LibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  library: LibraryFile[];
  onRemoveFiles: (paths: string[]) => void;
  onUpdatePaths: (updates: Record<string, string>) => void;
  onAddToGroup: (groupName: string, paths: string[]) => void;
  groupNames: string[];
}

export const LibraryModal: React.FC<LibraryModalProps> = ({
  isOpen,
  onClose,
  library,
  onRemoveFiles,
  onUpdatePaths,
  onAddToGroup,
  groupNames,
}) => {
  const [selectedPaths, setSelectedPaths] = useState<string[]>([]);
  const [showGroupPicker, setShowGroupPicker] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [pathPrompt, setPathPrompt] = useState<{ open: boolean; oldPath: string; newPath: string }>({
    open: false,
    oldPath: '',
    newPath: '',
  });

  if (!isOpen) return null;

  const toggleSelect = (path: string, e?: React.MouseEvent) => {
    if (e?.ctrlKey || e?.metaKey) {
      setSelectedPaths((prev) =>
        prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]
      );
    } else if (e?.shiftKey && selectedPaths.length > 0) {
      const lastSelected = selectedPaths[selectedPaths.length - 1];
      const lastIndex = library.findIndex((f) => f.path === lastSelected);
      const currentIndex = library.findIndex((f) => f.path === path);
      if (lastIndex !== -1 && currentIndex !== -1) {
        const [start, end] = [Math.min(lastIndex, currentIndex), Math.max(lastIndex, currentIndex)];
        const range = library.slice(start, end + 1).map((f) => f.path);
        setSelectedPaths(Array.from(new Set([...selectedPaths, ...range])));
      }
    } else {
      setSelectedPaths((prev) =>
        prev.includes(path) && prev.length === 1 ? [] : [path]
      );
    }
  };

  const handleSelectAll = () => {
    if (selectedPaths.length === library.length) {
      setSelectedPaths([]);
    } else {
      setSelectedPaths(library.map((f) => f.path));
    }
  };

  const handleRemove = () => {
    if (selectedPaths.length === 0) return;
    if (window.confirm(`Bạn có chắc chắn muốn xoá ${selectedPaths.length} file khỏi danh sách không?`)) {
      onRemoveFiles(selectedPaths);
      setSelectedPaths([]);
    }
  };

  const handleStartUpdatePath = () => {
    if (selectedPaths.length === 0) return;
    if (selectedPaths.length === 1) {
      const old = selectedPaths[0];
      setPathPrompt({ open: true, oldPath: old, newPath: old });
    } else {
      const newFolder = prompt(
        'Nhập thư mục mới chứa các file đã chọn (giữ nguyên tên file):',
        'D:/DuAnMoi/HoSoPDF/'
      );
      if (newFolder) {
        const updates: Record<string, string> = {};
        selectedPaths.forEach((oldPath) => {
          const fileName = oldPath.split('/').pop() || '';
          updates[oldPath] = `${newFolder.replace(/\\/g, '/').replace(/\/$/, '')}/${fileName}`;
        });
        onUpdatePaths(updates);
        alert(`Đã cập nhật đường dẫn cho ${selectedPaths.length} file.`);
      }
    }
  };

  const handleSaveSinglePath = () => {
    if (!pathPrompt.newPath.trim()) return;
    onUpdatePaths({ [pathPrompt.oldPath]: pathPrompt.newPath.trim() });
    setPathPrompt({ open: false, oldPath: '', newPath: '' });
  };

  const handleConfirmAddToGroup = () => {
    const group = newGroupName.trim() || selectedGroup;
    if (!group) {
      alert('Vui lòng chọn 1 nhóm hoặc nhập tên nhóm mới!');
      return;
    }
    onAddToGroup(group, selectedPaths);
    setShowGroupPicker(false);
    setNewGroupName('');
    setSelectedGroup('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] p-4">
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-2xl border border-[#E4E7EE] overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header với dòng nhắc nhở chuẩn 1 dòng không bị ngắt */}
        <div className="px-5 py-3.5 border-b border-[#E4E7EE] flex items-start justify-between bg-[#F8FAFD]">
          <div>
            <h3 className="text-[14px] font-bold text-[#1E293B] flex items-center gap-2">
              <Folder className="w-4 h-4 text-[#2563EB]" strokeWidth={1.75} />
              Danh sách file PDF đã thêm
            </h3>
            {/* Nhắc nhở строго 1 dòng duy nhất */}
            <p className="text-[12px] text-[#64748B] mt-1 whitespace-nowrap overflow-hidden text-ellipsis">
              Có thể chọn nhiều dòng cùng lúc (giữ Ctrl hoặc Shift) để cập nhật đường dẫn hoặc thêm vào nhóm hàng loạt.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[#64748B] hover:text-[#1E293B] p-1 rounded hover:bg-[#E4E7EE]/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Table content */}
        <div className="flex-1 overflow-auto p-4">
          <div className="border border-[#E4E7EE] rounded overflow-hidden">
            <table className="w-full text-left border-collapse text-[12.5px]">
              <thead>
                <tr className="bg-[#F8FAFD] border-b border-[#E4E7EE] text-[#1E293B] font-semibold select-none">
                  <th className="py-2 px-3 w-10 text-center">
                    <input
                      type="checkbox"
                      checked={library.length > 0 && selectedPaths.length === library.length}
                      onChange={handleSelectAll}
                      className="rounded border-[#D2D7E2] text-[#2563EB] focus:ring-0 cursor-pointer"
                    />
                  </th>
                  <th className="py-2 px-3 w-64 border-r border-[#E4E7EE]">Tên file</th>
                  <th className="py-2 px-3">Đường dẫn đầy đủ trên máy</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E4E7EE]">
                {library.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="py-8 text-center text-[#64748B]">
                      Chưa có file PDF nào được thêm vào danh sách.
                    </td>
                  </tr>
                ) : (
                  library.map((item, idx) => {
                    const isSelected = selectedPaths.includes(item.path);
                    return (
                      <tr
                        key={item.path}
                        onClick={(e) => toggleSelect(item.path, e)}
                        className={`cursor-pointer transition-colors select-none ${
                          isSelected
                            ? 'bg-[#CFE4FF] text-[#0A2540] font-medium'
                            : idx % 2 === 0
                            ? 'bg-white hover:bg-[#F1F5F9]'
                            : 'bg-[#FAFCFF] hover:bg-[#F1F5F9]'
                        }`}
                      >
                        <td className="py-2 px-3 text-center" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSelect(item.path)}
                            className="rounded border-[#D2D7E2] text-[#2563EB] focus:ring-0 cursor-pointer"
                          />
                        </td>
                        <td className="py-2 px-3 font-medium border-r border-[#E4E7EE]">{item.name}</td>
                        <td className="py-2 px-3 font-mono text-[11.5px] text-[#334155] truncate max-w-lg">
                          {item.path}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
          <div className="flex justify-between items-center mt-2 text-[11.5px] text-[#64748B] px-1">
            <span>Đã chọn: <b className="text-[#1E293B]">{selectedPaths.length}</b> / {library.length} file</span>
            <span>Gợi ý: Bấm phím Shift hoặc Ctrl để chọn hàng loạt</span>
          </div>
        </div>

        {/* Action buttons footer */}
        <div className="px-5 py-3 border-t border-[#E4E7EE] bg-[#F8FAFD] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={handleStartUpdatePath}
              disabled={selectedPaths.length === 0}
              className="px-3 py-1.5 text-[12px] bg-white border border-[#D2D7E2] rounded hover:bg-[#EAF2FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] disabled:opacity-40 disabled:pointer-events-none transition-colors flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Cập nhật đường dẫn...
            </button>
            <button
              onClick={() => setShowGroupPicker(true)}
              disabled={selectedPaths.length === 0}
              className="px-3 py-1.5 text-[12px] bg-white border border-[#D2D7E2] rounded hover:bg-[#EAF2FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] disabled:opacity-40 disabled:pointer-events-none transition-colors flex items-center gap-1.5"
            >
              <FolderPlus className="w-3.5 h-3.5" />
              Thêm vào nhóm...
            </button>
            <button
              onClick={handleRemove}
              disabled={selectedPaths.length === 0}
              className="px-3 py-1.5 text-[12px] bg-white border border-[#EF4444] text-[#EF4444] rounded hover:bg-[#FEE2E2] disabled:opacity-40 disabled:pointer-events-none transition-colors flex items-center gap-1.5"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Xoá khỏi danh sách
            </button>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-[12px] bg-[#E4E7EE] hover:bg-[#D2D7E2] text-[#1E293B] rounded transition-colors"
          >
            Đóng
          </button>
        </div>

        {/* Modal con: Thêm vào nhóm */}
        {showGroupPicker && (
          <div className="absolute inset-0 bg-black/30 flex items-center justify-center p-4 z-20">
            <div className="bg-white border border-[#E4E7EE] rounded-lg shadow-xl p-5 w-full max-w-sm">
              <h4 className="text-[13px] font-bold text-[#1E293B] mb-2">Thêm file đã chọn vào nhóm</h4>
              <p className="text-[11.5px] text-[#64748B] mb-3">
                Chọn một nhóm có sẵn hoặc nhập tên nhóm mới:
              </p>

              <div className="max-h-36 overflow-y-auto border border-[#E4E7EE] rounded mb-3 divide-y divide-[#E4E7EE]">
                {groupNames.length === 0 ? (
                  <div className="p-2 text-[11.5px] text-[#64748B] text-center">Chưa có nhóm nào</div>
                ) : (
                  groupNames.map((g) => (
                    <div
                      key={g}
                      onClick={() => {
                        setSelectedGroup(g);
                        setNewGroupName('');
                      }}
                      className={`px-3 py-1.5 text-[12px] cursor-pointer flex items-center justify-between ${
                        selectedGroup === g ? 'bg-[#CFE4FF] text-[#0A2540] font-medium' : 'hover:bg-[#F1F5F9]'
                      }`}
                    >
                      <span>🏷  {g}</span>
                      {selectedGroup === g && <Check className="w-3.5 h-3.5 text-[#2563EB]" />}
                    </div>
                  ))
                )}
              </div>

              <div className="mb-4">
                <label className="block text-[11.5px] text-[#64748B] mb-1">Hoặc tạo nhóm mới:</label>
                <input
                  type="text"
                  placeholder="Nhập tên nhóm mới..."
                  value={newGroupName}
                  onChange={(e) => {
                    setNewGroupName(e.target.value);
                    if (e.target.value) setSelectedGroup('');
                  }}
                  className="w-full text-[12px] px-2.5 py-1.5 border border-[#D2D7E2] rounded focus:outline-none focus:border-[#2563EB]"
                />
              </div>

              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowGroupPicker(false)}
                  className="px-3 py-1 text-[12px] text-[#64748B] hover:text-[#1E293B]"
                >
                  Hủy
                </button>
                <button
                  onClick={handleConfirmAddToGroup}
                  className="px-3.5 py-1 text-[12px] bg-[#2563EB] text-white rounded hover:bg-[#1D4ED8]"
                >
                  Xác nhận
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Modal con: Cập nhật đường dẫn file đơn */}
        {pathPrompt.open && (
          <div className="absolute inset-0 bg-black/30 flex items-center justify-center p-4 z-20">
            <div className="bg-white border border-[#E4E7EE] rounded-lg shadow-xl p-5 w-full max-w-lg">
              <h4 className="text-[13px] font-bold text-[#1E293B] mb-2">Cập nhật đường dẫn file</h4>
              <p className="text-[11.5px] text-[#64748B] mb-2">Đường dẫn mới cho file:</p>
              <input
                type="text"
                value={pathPrompt.newPath}
                onChange={(e) => setPathPrompt({ ...pathPrompt, newPath: e.target.value })}
                className="w-full text-[12px] font-mono px-2.5 py-1.5 border border-[#D2D7E2] rounded focus:outline-none focus:border-[#2563EB] mb-4"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setPathPrompt({ open: false, oldPath: '', newPath: '' })}
                  className="px-3 py-1 text-[12px] text-[#64748B] hover:text-[#1E293B]"
                >
                  Hủy
                </button>
                <button
                  onClick={handleSaveSinglePath}
                  className="px-3.5 py-1 text-[12px] bg-[#2563EB] text-white rounded hover:bg-[#1D4ED8]"
                >
                  Lưu đường dẫn
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
