import React, { useState } from 'react';
import { Tag, Plus, Edit2, Trash2, X, UserMinus, FileText } from 'lucide-react';
import { LibraryFile } from '../data/mockData';

interface GroupManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  groups: Record<string, string[]>;
  library: LibraryFile[];
  onSaveGroups: (newGroups: Record<string, string[]>) => void;
}

export const GroupManagerModal: React.FC<GroupManagerModalProps> = ({
  isOpen,
  onClose,
  groups,
  library,
  onSaveGroups,
}) => {
  const [selectedGroup, setSelectedGroup] = useState<string>(Object.keys(groups)[0] || '');
  const [selectedMembers, setSelectedMembers] = useState<string[]>([]);

  if (!isOpen) return null;

  const groupKeys = Object.keys(groups);
  const currentMembers = groups[selectedGroup] || [];

  const handleCreateGroup = () => {
    const name = prompt('Nhập tên nhóm mới:');
    if (!name || !name.trim()) return;
    const trimmed = name.trim();
    if (groups[trimmed]) {
      alert('Nhóm này đã tồn tại!');
      return;
    }
    const updated = { ...groups, [trimmed]: [] };
    onSaveGroups(updated);
    setSelectedGroup(trimmed);
  };

  const handleRenameGroup = () => {
    if (!selectedGroup) return;
    const newName = prompt('Nhập tên nhóm mới:', selectedGroup);
    if (!newName || !newName.trim() || newName.trim() === selectedGroup) return;
    const trimmed = newName.trim();
    if (groups[trimmed]) {
      alert('Đã có nhóm với tên này!');
      return;
    }
    const updated: Record<string, string[]> = {};
    for (const [k, v] of Object.entries(groups)) {
      if (k === selectedGroup) {
        updated[trimmed] = v;
      } else {
        updated[k] = v;
      }
    }
    onSaveGroups(updated);
    setSelectedGroup(trimmed);
  };

  const handleDeleteGroup = () => {
    if (!selectedGroup) return;
    if (window.confirm(`Xoá nhóm '${selectedGroup}'?\n(Các file PDF vẫn giữ nguyên trong danh sách chính)`)) {
      const updated = { ...groups };
      delete updated[selectedGroup];
      onSaveGroups(updated);
      setSelectedGroup(Object.keys(updated)[0] || '');
      setSelectedMembers([]);
    }
  };

  const handleRemoveMembers = () => {
    if (!selectedGroup || selectedMembers.length === 0) return;
    const updatedMembers = currentMembers.filter((path) => !selectedMembers.includes(path));
    const updated = { ...groups, [selectedGroup]: updatedMembers };
    onSaveGroups(updated);
    setSelectedMembers([]);
  };

  const toggleMemberSelect = (path: string) => {
    setSelectedMembers((prev) =>
      prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] p-4">
      <div className="w-full max-w-3xl bg-white rounded-lg shadow-2xl border border-[#E4E7EE] overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-[#E4E7EE] flex items-start justify-between bg-[#F8FAFD]">
          <div>
            <h3 className="text-[14px] font-bold text-[#1E293B] flex items-center gap-2">
              <Tag className="w-4 h-4 text-[#2563EB]" strokeWidth={1.75} />
              Quản lý nhóm
            </h3>
            <p className="text-[12px] text-[#64748B] mt-0.5">
              Tạo, đổi tên, xoá nhóm và quản lý file PDF thuộc mỗi nhóm.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[#64748B] hover:text-[#1E293B] p-1 rounded hover:bg-[#E4E7EE]/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* 2-column layout */}
        <div className="flex-1 p-5 flex gap-4 overflow-hidden">
          {/* Left: Groups list + buttons */}
          <div className="w-56 flex flex-col">
            <span className="text-[12px] font-semibold text-[#64748B] mb-2">Danh sách nhóm:</span>
            <div className="flex-1 border border-[#E4E7EE] rounded overflow-y-auto divide-y divide-[#E4E7EE] mb-3 bg-[#FAFCFF]">
              {groupKeys.length === 0 ? (
                <div className="p-3 text-center text-[12px] text-[#64748B]">Chưa có nhóm nào</div>
              ) : (
                groupKeys.map((g) => (
                  <div
                    key={g}
                    onClick={() => {
                      setSelectedGroup(g);
                      setSelectedMembers([]);
                    }}
                    className={`px-3 py-2 text-[12.5px] cursor-pointer flex items-center justify-between transition-colors ${
                      selectedGroup === g
                        ? 'bg-[#CFE4FF] text-[#0A2540] font-bold border-l-3 border-[#2563EB]'
                        : 'hover:bg-[#F1F5F9] text-[#1E293B]'
                    }`}
                  >
                    <span className="truncate">🏷  {g}</span>
                    <span className="text-[11px] px-1.5 py-0.5 rounded bg-white/70 text-[#64748B] border border-[#E4E7EE]">
                      {(groups[g] || []).length}
                    </span>
                  </div>
                ))
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <button
                onClick={handleCreateGroup}
                className="w-full py-1.5 text-[12px] bg-white border border-[#D2D7E2] rounded hover:bg-[#EAF2FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] transition-colors flex items-center justify-center gap-1.5 font-medium"
              >
                <Plus className="w-3.5 h-3.5" />
                Tạo nhóm mới
              </button>
              <button
                onClick={handleRenameGroup}
                disabled={!selectedGroup}
                className="w-full py-1.5 text-[12px] bg-white border border-[#D2D7E2] rounded hover:bg-[#EAF2FF] hover:text-[#2563EB] text-[#1E293B] disabled:opacity-40 transition-colors flex items-center justify-center gap-1.5"
              >
                <Edit2 className="w-3.5 h-3.5" />
                Đổi tên nhóm
              </button>
              <button
                onClick={handleDeleteGroup}
                disabled={!selectedGroup}
                className="w-full py-1.5 text-[12px] bg-white border border-[#EF4444] text-[#EF4444] rounded hover:bg-[#FEE2E2] disabled:opacity-40 transition-colors flex items-center justify-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Xoá nhóm
              </button>
            </div>
          </div>

          {/* Right: Members of selected group */}
          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[12px] font-semibold text-[#64748B]">
                File trong nhóm &ldquo;<b className="text-[#1E293B]">{selectedGroup || 'Chưa chọn'}</b>&rdquo;:
              </span>
              <span className="text-[11.5px] text-[#64748B]">
                {currentMembers.length} file
              </span>
            </div>

            <div className="flex-1 border border-[#E4E7EE] rounded overflow-y-auto bg-white mb-3">
              {currentMembers.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center p-6 text-center text-[#64748B]">
                  <FileText className="w-8 h-8 text-[#CBD5E1] mb-2" />
                  <p className="text-[12px]">Nhóm này chưa có file PDF nào.</p>
                  <p className="text-[11px] text-[#94A3B8] mt-1">
                    Mở &quot;Danh sách file đã thêm&quot; &gt; &quot;Thêm vào nhóm...&quot; để đưa file vào nhóm này.
                  </p>
                </div>
              ) : (
                <table className="w-full text-left text-[12px]">
                  <thead>
                    <tr className="bg-[#F8FAFD] border-b border-[#E4E7EE] text-[#64748B]">
                      <th className="py-2 px-3 w-10 text-center">Chọn</th>
                      <th className="py-2 px-3">Tên file & Đường dẫn</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E4E7EE]">
                    {currentMembers.map((path) => {
                      const isSelected = selectedMembers.includes(path);
                      const fileItem = library.find((f) => f.path === path);
                      const fileName = fileItem ? fileItem.name : path.split('/').pop();
                      return (
                        <tr
                          key={path}
                          onClick={() => toggleMemberSelect(path)}
                          className={`cursor-pointer transition-colors ${
                            isSelected ? 'bg-[#CFE4FF] text-[#0A2540] font-medium' : 'hover:bg-[#F1F5F9]'
                          }`}
                        >
                          <td className="py-2 px-3 text-center" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => toggleMemberSelect(path)}
                              className="rounded border-[#D2D7E2] text-[#2563EB] focus:ring-0 cursor-pointer"
                            />
                          </td>
                          <td className="py-2 px-3">
                            <div className="font-medium text-[#1E293B]">{fileName}</div>
                            <div className="text-[11px] text-[#64748B] font-mono truncate max-w-md">{path}</div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>

            <div>
              <button
                onClick={handleRemoveMembers}
                disabled={selectedMembers.length === 0}
                className="px-3.5 py-1.5 text-[12px] bg-white border border-[#D2D7E2] rounded hover:bg-[#FEE2E2] hover:text-[#EF4444] hover:border-[#EF4444] text-[#1E293B] disabled:opacity-40 transition-colors flex items-center gap-1.5"
              >
                <UserMinus className="w-3.5 h-3.5" />
                Bớt {selectedMembers.length > 0 ? `(${selectedMembers.length})` : ''} file đã chọn khỏi nhóm
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#E4E7EE] bg-[#F8FAFD] flex justify-end">
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
