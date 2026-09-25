import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Search,
  Plus,
  Folder,
  Tag,
  Settings,
  Keyboard,
  FileText,
  FileCode,
  Download,
  RotateCcw,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import {
  BookmarkRow,
  INITIAL_BOOKMARKS,
  INITIAL_GROUPS,
  INITIAL_LIBRARY,
  LibraryFile,
} from './data/mockData';
import { matchScore } from './utils/textSearch';
import { LibraryModal } from './components/LibraryModal';
import { GroupManagerModal } from './components/GroupManagerModal';
import { ViewerSettingsModal } from './components/ViewerSettingsModal';
import { HotkeySettingsModal } from './components/HotkeySettingsModal';
import { QuickSearchOverlay } from './components/QuickSearchOverlay';
import { DrawingViewerModal } from './components/DrawingViewerModal';
import { SourceCodeModal } from './components/SourceCodeModal';
import { InstallerModal } from './components/InstallerModal';
import { AppIcon } from './components/AppIcon';
import { Package } from 'lucide-react';

export default function App() {
  // State quản lý danh sách file, nhóm, và bookmark
  const [library, setLibrary] = useState<LibraryFile[]>(INITIAL_LIBRARY);
  const [groups, setGroups] = useState<Record<string, string[]>>(INITIAL_GROUPS);
  const [bookmarks, setBookmarks] = useState<BookmarkRow[]>(INITIAL_BOOKMARKS);

  // Bộ lọc
  const [selectedGroup, setSelectedGroup] = useState<string>('Tất cả các nhóm');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Dòng đang chọn trong bảng
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);

  // Chế độ: Khi Quick Search bật thì ẩn bảng điều khiển đầy đủ và ngược lại
  const [isQuickSearchOpen, setIsQuickSearchOpen] = useState<boolean>(false);

  // Modals
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [isGroupManagerOpen, setIsGroupManagerOpen] = useState(false);
  const [isViewerSettingsOpen, setIsViewerSettingsOpen] = useState(false);
  const [isHotkeySettingsOpen, setIsHotkeySettingsOpen] = useState(false);
  const [isSourceCodeOpen, setIsSourceCodeOpen] = useState(false);
  const [isInstallerOpen, setIsInstallerOpen] = useState(false);
  const [activeDrawing, setActiveDrawing] = useState<BookmarkRow | null>(null);

  // Cấu hình phần mềm mở PDF & phím tắt
  const [viewerExe, setViewerExe] = useState('C:/Program Files/SumatraPDF/SumatraPDF.exe');
  const [viewerTemplate, setViewerTemplate] = useState('"{exe}" -page {page} "{file}"');
  const [hotkey, setHotkey] = useState('double_shift');

  // Xử lý phím tắt toàn cục Double Shift (bấm Shift 2 lần liên tiếp để bật/tắt ô tìm kiếm nổi)
  const lastShiftTime = useRef<number>(0);
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Shift') {
        const now = Date.now();
        if (now - lastShiftTime.current < 350) {
          lastShiftTime.current = 0;
          setIsQuickSearchOpen((prev) => !prev);
        } else {
          lastShiftTime.current = now;
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Lọc danh sách bookmark theo nhóm và từ khóa
  const filteredBookmarks = useMemo(() => {
    let result = bookmarks;

    // Lọc theo nhóm
    if (selectedGroup !== 'Tất cả các nhóm') {
      const allowedPaths = new Set(groups[selectedGroup] || []);
      result = result.filter((b) => allowedPaths.has(b.pdf_path));
    }

    // Lọc theo từ khóa tìm kiếm (thuật toán Listary)
    const trimmed = searchQuery.trim();
    if (trimmed) {
      const scored = result
        .map((b) => ({
          item: b,
          score: matchScore(trimmed, b.title, b.parent_path, b.pdf_name),
        }))
        .filter((entry) => entry.score > 0);

      scored.sort((a, b) => b.score - a.score);
      result = scored.map((s) => s.item);
    }

    return result;
  }, [bookmarks, groups, selectedGroup, searchQuery]);

  // Thêm file PDF mới
  const handleAddPdfFiles = () => {
    const fileName = prompt(
      'Nhập tên file PDF cần thêm vào hồ sơ:',
      `BV-HangMucMoi-${Date.now().toString().slice(-4)}.pdf`
    );
    if (!fileName || !fileName.trim()) return;

    const trimmed = fileName.trim();
    const filePath = `C:/HoSoBanVe/DuAn/${trimmed}`;

    if (library.some((f) => f.path === filePath)) {
      alert('File PDF này đã có trong danh sách!');
      return;
    }

    const newFile: LibraryFile = { name: trimmed, path: filePath };
    setLibrary((prev) => [...prev, newFile]);

    // Tạo các bookmark mẫu cho file mới
    const newItems: BookmarkRow[] = [
      {
        id: `bm-${Date.now()}-1`,
        pdf_name: trimmed,
        pdf_path: filePath,
        level: 0,
        parent_path: '',
        title: `Mặt bằng tổng thể - ${trimmed.replace('.pdf', '')}`,
        page: 1,
        groups: selectedGroup !== 'Tất cả các nhóm' ? [selectedGroup] : [],
      },
      {
        id: `bm-${Date.now()}-2`,
        pdf_name: trimmed,
        pdf_path: filePath,
        level: 1,
        parent_path: `Mặt bằng tổng thể - ${trimmed.replace('.pdf', '')}`,
        title: `Chi tiết kỹ thuật cấu kiện chính`,
        page: 2,
        groups: selectedGroup !== 'Tất cả các nhóm' ? [selectedGroup] : [],
      },
    ];

    setBookmarks((prev) => [...prev, ...newItems]);

    // Nếu đang chọn 1 nhóm thì tự động thêm file mới vào nhóm đó
    if (selectedGroup !== 'Tất cả các nhóm') {
      setGroups((prev) => ({
        ...prev,
        [selectedGroup]: [...(prev[selectedGroup] || []), filePath],
      }));
    }

    alert(`Đã thêm thành công file "${trimmed}" và nạp ${newItems.length} bookmark!`);
  };

  // Xoá file khỏi thư viện
  const handleRemoveFiles = (paths: string[]) => {
    const pathSet = new Set(paths);
    setLibrary((prev) => prev.filter((f) => !pathSet.has(f.path)));
    setBookmarks((prev) => prev.filter((b) => !pathSet.has(b.pdf_path)));

    const updatedGroups = { ...groups };
    for (const g of Object.keys(updatedGroups)) {
      updatedGroups[g] = updatedGroups[g].filter((p) => !pathSet.has(p));
    }
    setGroups(updatedGroups);
  };

  // Cập nhật đường dẫn file
  const handleUpdatePaths = (updates: Record<string, string>) => {
    setLibrary((prev) =>
      prev.map((f) => {
        if (updates[f.path]) {
          const newPath = updates[f.path];
          return { name: newPath.split('/').pop() || f.name, path: newPath };
        }
        return f;
      })
    );

    setBookmarks((prev) =>
      prev.map((b) => {
        if (updates[b.pdf_path]) {
          const newPath = updates[b.pdf_path];
          return {
            ...b,
            pdf_path: newPath,
            pdf_name: newPath.split('/').pop() || b.pdf_name,
          };
        }
        return b;
      })
    );

    const updatedGroups = { ...groups };
    for (const g of Object.keys(updatedGroups)) {
      updatedGroups[g] = updatedGroups[g].map((p) => updates[p] || p);
    }
    setGroups(updatedGroups);
  };

  // Thêm file vào nhóm
  const handleAddToGroup = (groupName: string, paths: string[]) => {
    setGroups((prev) => {
      const existing = prev[groupName] || [];
      const merged = Array.from(new Set([...existing, ...paths]));
      return { ...prev, [groupName]: merged };
    });

    setBookmarks((prev) =>
      prev.map((b) => {
        if (paths.includes(b.pdf_path) && !b.groups.includes(groupName)) {
          return { ...b, groups: [...b.groups, groupName] };
        }
        return b;
      })
    );

    alert(`Đã thêm ${paths.length} file vào nhóm "${groupName}"!`);
  };

  // Mở bản vẽ PDF
  const handleOpenBookmark = (bm: BookmarkRow) => {
    setActiveDrawing(bm);
  };

  // Danh sách các nhóm (kể cả nhóm số 1, 2, 3..10 như ảnh chụp của user)
  const groupNames = useMemo(() => {
    return Object.keys(groups);
  }, [groups]);

  // Đếm số file và bookmark theo phạm vi đang xem
  const currentFilesCount = useMemo(() => {
    const unique = new Set(filteredBookmarks.map((b) => b.pdf_path));
    return unique.size;
  }, [filteredBookmarks]);

  return (
    <div className="h-screen w-screen flex flex-col bg-[#F4F6F9] text-[#1E293B] select-none font-sans overflow-hidden">
      {/* ------------------------------------------------------------- */}
      {/* 1. THANH TÌM KIẾM NHANH NỔI (QUICK SEARCH OVERLAY)            */}
      {/* Khi bật: Ẩn bảng điều khiển đầy đủ; Khi tắt: Hiện lại đầy đủ  */}
      {/* ------------------------------------------------------------- */}
      <QuickSearchOverlay
        isOpen={isQuickSearchOpen}
        onClose={() => setIsQuickSearchOpen(false)}
        onExpandToFull={(query) => {
          setIsQuickSearchOpen(false);
          setSearchQuery(query);
        }}
        bookmarks={bookmarks}
        onOpenBookmark={handleOpenBookmark}
      />

      {/* Khi Quick Search đang mở, ẩn bảng điều khiển đầy đủ theo yêu cầu */}
      {!isQuickSearchOpen && (
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {/* ----------------------------------------------------------- */}
          {/* CỬA SỔ CHÍNH: Tiêu đề cửa sổ chuẩn hệ thống (Title Bar)     */}
          {/* ----------------------------------------------------------- */}
          <div className="h-10 bg-[#FFFFFF] border-b border-[#E2E8F0] px-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              {/* Logo ứng dụng rõ ràng, màu sắc nổi bật */}
              <AppIcon size={22} />
              <span className="text-[13px] font-bold text-[#0F172A] tracking-tight">
                Tra cứu hồ sơ PDF
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#EBF3FF] text-[#1D4ED8] font-bold border border-[#BFDBFE]">
                Listary Edition
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsInstallerOpen(true)}
                className="px-3 py-1.5 text-[12px] text-white bg-[#059669] hover:bg-[#047857] rounded-lg font-semibold flex items-center gap-2 shadow-xs transition-colors cursor-pointer"
                title="Đóng gói và tải file cài đặt Windows (.exe)"
              >
                <Package className="w-4 h-4" />
                <span>Đóng gói cài đặt (.exe)</span>
              </button>

              <button
                type="button"
                onClick={() => setIsSourceCodeOpen(true)}
                className="px-3 py-1.5 text-[12px] text-[#2563EB] bg-[#EFF6FF] hover:bg-[#DBEAFE] rounded-lg font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Xem và tải mã nguồn Python (bookmark_app.py)"
              >
                <FileCode className="w-4 h-4" />
                <span>Mã nguồn (.py)</span>
              </button>

              <div className="h-4 w-[1px] bg-[#D2D7E2] mx-1"></div>

              <div className="flex items-center gap-1.5 text-[11.5px] text-[#64748B]">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#10B981]"></span>
                <span>Chạy ngầm (Shift Shift)</span>
              </div>
            </div>
          </div>

          {/* ----------------------------------------------------------- */}
          {/* THANH CÔNG CỤ TÌM KIẾM TRÊN CÙNG: CHIẾM FULL 100% BỀ RỘNG   */}
          {/* Bo tròn 4 góc hiện đại chuẩn mực (12px), viền mượt mà       */}
          {/* ----------------------------------------------------------- */}
          <div className="bg-white border-b border-[#E2E8F0] px-4 py-2.5 shrink-0 flex items-center">
            {/* Ô tìm kiếm bo tròn 4 góc hiện đại (Rounded-xl), chiếm full 100% chiều rộng */}
            <div className="w-full flex items-center bg-[#F8FAFC] border-2 border-[#CBD5E1] hover:border-[#94A3B8] focus-within:border-[#2563EB] focus-within:bg-white rounded-xl px-4 py-2 transition-all shadow-xs focus-within:shadow-md focus-within:ring-2 focus-within:ring-[#2563EB]/20">
              {/* Biểu tượng tìm kiếm to rõ ràng, cân đối */}
              <Search className="w-5 h-5 text-[#64748B] shrink-0 mr-3" strokeWidth={1.75} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm kiếm bookmark theo tiêu đề, mục cha, tên file PDF..."
                className="w-full text-[13.5px] bg-transparent text-[#0F172A] placeholder-[#94A3B8] focus:outline-none"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="w-5 h-5 flex items-center justify-center rounded-full bg-[#E2E8F0] hover:bg-[#CBD5E1] text-[#64748B] text-[11px] font-bold mr-1 transition-colors"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* ----------------------------------------------------------- */}
          {/* NỘI DUNG CHÍNH: SIDEBAR (LỌC THEO NHÓM + CÔNG CỤ) & BẢNG    */}
          {/* ----------------------------------------------------------- */}
          <div className="flex-1 flex overflow-hidden p-3.5 gap-3.5">
            {/* SIDEBAR TRÁI: Width 240px                                   */}
            {/* Lọc theo nhóm có cuộn mượt; CÔNG CỤ GHIM CỐ ĐỊNH Ở DƯỚI     */}
            <div className="w-[240px] bg-white border border-[#E2E8F0] rounded-xl flex flex-col shrink-0 shadow-xs overflow-hidden">
              {/* Vùng Lọc theo nhóm: cuộn được khi có nhiều nhóm (1,2..10)  */}
              <div className="p-3.5 pb-2 border-b border-[#E2E8F0] flex items-center justify-between shrink-0">
                <span className="text-[11px] font-bold text-[#64748B] tracking-wider uppercase">
                  Lọc theo nhóm
                </span>
                <span className="text-[10.5px] font-medium text-[#64748B] px-1.5 py-0.2 rounded bg-[#F1F5F9]">
                  {groupNames.length} nhóm
                </span>
              </div>

              {/* Danh sách nhóm cuộn tự do không làm ảnh hưởng phần công cụ */}
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {/* Tất cả các nhóm */}
                <div
                  onClick={() => setSelectedGroup('Tất cả các nhóm')}
                  className={`px-3 py-2 text-[12.5px] rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                    selectedGroup === 'Tất cả các nhóm'
                      ? 'bg-[#CFE4FF] text-[#0A2540] font-bold shadow-xs'
                      : 'hover:bg-[#F1F5F9] text-[#334155]'
                  }`}
                >
                  <span className="flex items-center gap-2 truncate">
                    <span className="text-[14px]">🗂</span>
                    <span>Tất cả các nhóm</span>
                  </span>
                  <span className="text-[10.5px] font-semibold text-[#64748B] px-1.5 py-0.5 rounded bg-white/70">
                    {bookmarks.length}
                  </span>
                </div>

                {/* Các nhóm người dùng tạo (bao gồm 1, 2, 3... 10) */}
                {groupNames.map((g) => {
                  const isSelected = selectedGroup === g;
                  const countInGroup = (groups[g] || []).length;
                  return (
                    <div
                      key={g}
                      onClick={() => setSelectedGroup(g)}
                      className={`px-3 py-2 text-[12.5px] rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                        isSelected
                          ? 'bg-[#CFE4FF] text-[#0A2540] font-bold shadow-xs'
                          : 'hover:bg-[#F1F5F9] text-[#334155]'
                      }`}
                    >
                      <span className="flex items-center gap-2 truncate">
                        <span className="text-[13px]">🏷</span>
                        <span>{g}</span>
                      </span>
                      <span className="text-[10.5px] font-semibold text-[#64748B] px-1.5 py-0.5 rounded bg-white/70">
                        {countInGroup}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* --------------------------------------------------------- */}
              {/* PHẦN CÔNG CỤ: GHIM CHẶT Ở DƯỚI (BOTTOM)                   */}
              {/* Căn lề trái, biểu tượng to rõ ràng, cân đối               */}
              {/* --------------------------------------------------------- */}
              <div className="border-t border-[#E2E8F0] p-3 bg-[#F8FAFD] shrink-0">
                <span className="block text-[10.5px] font-bold text-[#64748B] tracking-wider uppercase mb-2 px-1">
                  CÔNG CỤ
                </span>
                <div className="flex flex-col gap-1.5">
                  {/* Nút thêm file PDF: biểu tượng to w-5 h-5, căn lề trái đều đẹp */}
                  <button
                    type="button"
                    onClick={handleAddPdfFiles}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-white border border-[#CBD5E1] rounded-lg hover:bg-[#EFF6FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] font-medium transition-colors flex items-center gap-2.5 cursor-pointer shadow-xs"
                  >
                    <Plus className="w-5 h-5 text-[#2563EB] shrink-0" strokeWidth={2} />
                    <span>Thêm file PDF...</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsLibraryOpen(true)}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-white border border-[#CBD5E1] rounded-lg hover:bg-[#EFF6FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] font-medium transition-colors flex items-center gap-2.5 cursor-pointer shadow-xs"
                  >
                    <Folder className="w-5 h-5 text-[#475569] shrink-0" strokeWidth={1.75} />
                    <span>Danh sách file đã thêm</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsGroupManagerOpen(true)}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-white border border-[#CBD5E1] rounded-lg hover:bg-[#EFF6FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] font-medium transition-colors flex items-center gap-2.5 cursor-pointer shadow-xs"
                  >
                    <Tag className="w-5 h-5 text-[#475569] shrink-0" strokeWidth={1.75} />
                    <span>Quản lý nhóm...</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsViewerSettingsOpen(true)}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-white border border-[#CBD5E1] rounded-lg hover:bg-[#EFF6FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] font-medium transition-colors flex items-center gap-2.5 cursor-pointer shadow-xs"
                  >
                    <Settings className="w-5 h-5 text-[#475569] shrink-0" strokeWidth={1.75} />
                    <span>Phần mềm mở PDF...</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsHotkeySettingsOpen(true)}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-white border border-[#CBD5E1] rounded-lg hover:bg-[#EFF6FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] font-medium transition-colors flex items-center gap-2.5 cursor-pointer shadow-xs"
                  >
                    <Keyboard className="w-5 h-5 text-[#475569] shrink-0" strokeWidth={1.75} />
                    <span>Phím tắt tìm nhanh</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsQuickSearchOpen(true)}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-white border border-[#CBD5E1] rounded-lg hover:bg-[#EFF6FF] hover:text-[#2563EB] hover:border-[#2563EB] text-[#1E293B] font-medium transition-colors flex items-center justify-between cursor-pointer shadow-xs"
                  >
                    <div className="flex items-center gap-2.5">
                      <Search className="w-5 h-5 text-[#2563EB] shrink-0" strokeWidth={1.75} />
                      <span>Tìm nhanh nổi</span>
                    </div>
                    <kbd className="text-[10px] font-bold bg-[#F1F5F9] px-1.5 py-0.5 rounded text-[#64748B] border border-[#CBD5E1]">
                      Shift Shift
                    </kbd>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsInstallerOpen(true)}
                    className="w-full text-left px-3 py-2 text-[12.5px] bg-[#ECFDF5] border border-[#A7F3D0] rounded-lg hover:bg-[#D1FAE5] text-[#065F46] font-semibold transition-colors flex items-center gap-2.5 cursor-pointer shadow-xs"
                  >
                    <Package className="w-5 h-5 text-[#059669] shrink-0" strokeWidth={1.75} />
                    <span>Đóng gói cài đặt (.exe)</span>
                  </button>
                </div>
              </div>
            </div>

            {/* BẢNG KẾT QUẢ TRA CỨU BOOKMARK (BÊN PHẢI)                  */}
            <div className="flex-1 bg-white border border-[#E4E7EE] rounded-lg shadow-xs flex flex-col overflow-hidden">
              <div className="flex-1 overflow-auto">
                <table className="w-full text-left border-collapse text-[12px]">
                  <thead className="sticky top-0 bg-[#F8FAFD] border-b border-[#E4E7EE] text-[#1E293B] font-semibold z-10 select-none">
                    <tr>
                      <th className="py-2.5 px-3 w-56 border-r border-[#E4E7EE]">📄 File PDF</th>
                      <th className="py-2.5 px-3 w-52 border-r border-[#E4E7EE]">Thuộc mục (cha)</th>
                      <th className="py-2.5 px-3">Tiêu đề bookmark</th>
                      <th className="py-2.5 px-3 w-20 text-center border-l border-[#E4E7EE]">Trang</th>
                      <th className="py-2.5 px-3 w-36 border-l border-[#E4E7EE]">🏷 Nhóm</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E4E7EE]">
                    {filteredBookmarks.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-14 text-center text-[#64748B]">
                          <p className="text-[13px] font-medium">Không tìm thấy bookmark nào</p>
                          <p className="text-[11.5px] mt-1 text-[#94A3B8]">
                            Thử tìm với từ khoá khác hoặc bấm &quot;Thêm file PDF...&quot; để nạp thêm bản vẽ.
                          </p>
                        </td>
                      </tr>
                    ) : (
                      filteredBookmarks.map((row, idx) => {
                        const isSelected = selectedRowId === row.id;
                        return (
                          <tr
                            key={row.id}
                            onClick={() => setSelectedRowId(row.id)}
                            onDoubleClick={() => handleOpenBookmark(row)}
                            className={`cursor-pointer transition-colors select-none ${
                              isSelected
                                ? 'bg-[#CFE4FF] text-[#0A2540] font-medium'
                                : idx % 2 === 0
                                ? 'bg-white hover:bg-[#F1F5F9]'
                                : 'bg-[#FAFCFF] hover:bg-[#F1F5F9]'
                            }`}
                          >
                            <td className="py-2 px-3 border-r border-[#E4E7EE] font-medium truncate max-w-[220px]">
                              {row.pdf_name}
                            </td>
                            <td className="py-2 px-3 border-r border-[#E4E7EE] text-[#64748B] truncate max-w-[200px]">
                              {row.parent_path || '—'}
                            </td>
                            <td className="py-2 px-3">
                              <span style={{ paddingLeft: `${row.level * 16}px` }} className="inline-block truncate">
                                {row.level > 0 && <span className="text-[#94A3B8] mr-1">↳</span>}
                                {row.title}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-center border-l border-[#E4E7EE] font-mono text-[11.5px]">
                              <span className="inline-block px-1.5 py-0.2 rounded bg-[#EAF2FF] text-[#2563EB] font-bold">
                                {row.page}
                              </span>
                            </td>
                            <td className="py-2 px-3 border-l border-[#E4E7EE] text-[11px] text-[#64748B] truncate max-w-[140px]">
                              {row.groups.length > 0 ? row.groups.join(', ') : '—'}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* ----------------------------------------------------------- */}
          {/* THANH TRẠNG THÁI MỎNG Ở CUỐI CỬA SỔ (Listary Footer)         */}
          {/* ----------------------------------------------------------- */}
          <div className="h-8 bg-[#F8FAFD] border-t border-[#E4E7EE] px-4 flex items-center justify-between text-[11.5px] text-[#64748B] shrink-0">
            <div className="flex items-center gap-2">
              <span className="text-[#2563EB] font-medium">ℹ</span>
              <span>
                {selectedGroup === 'Tất cả các nhóm'
                  ? 'Tất cả'
                  : `Nhóm '${selectedGroup}'`}
                : đã có <b className="text-[#1E293B]">{filteredBookmarks.length}</b> bookmark từ{' '}
                <b className="text-[#1E293B]">{currentFilesCount}</b> file PDF.
              </span>
            </div>

            <div className="flex items-center gap-4 text-[11px]">
              <span>💡 Nhấp đúp vào dòng để mở bản vẽ</span>
              <span>Phím tắt: <b>Shift Shift</b></span>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* THANH TASKBAR & KHAY HỆ THỐNG (SYSTEM TRAY)                   */}
      {/* Hiển thị logo phần mềm trên Taskbar và Khay thu nhỏ           */}
      {/* ------------------------------------------------------------- */}
      <div className="h-10 bg-[#F1F5F9]/95 backdrop-blur-md border-t border-[#D2D7E2] px-3 flex items-center justify-between shrink-0 z-40 select-none shadow-xs">
        {/* Nút Start & Các ứng dụng trên Taskbar */}
        <div className="flex items-center gap-1.5 h-full">
          {/* Windows Start Icon */}
          <button
            type="button"
            className="w-8 h-8 rounded-md hover:bg-black/5 flex items-center justify-center transition-colors text-[#2563EB]"
            title="Start"
          >
            <svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor">
              <path d="M0 0h7v7H0V0zm9 0h7v7H9V0zM0 9h7v7H0V9zm9 0h7v7H9V9z" />
            </svg>
          </button>

          {/* Biểu tượng phần mềm trên thanh Taskbar */}
          <button
            type="button"
            onClick={() => setIsQuickSearchOpen((prev) => !prev)}
            className={`h-8 px-2.5 rounded-md flex items-center gap-2 transition-all cursor-pointer relative group ${
              !isQuickSearchOpen
                ? 'bg-white shadow-xs border border-[#CBD5E1]'
                : 'hover:bg-white/60 bg-transparent'
            }`}
            title="Tra cứu hồ sơ PDF (Đang chạy)"
          >
            <AppIcon size={19} />
            <span className="text-[12px] font-medium text-[#1E293B] hidden sm:inline max-w-[170px] truncate">
              Tra cứu hồ sơ PDF
            </span>
            {/* Thanh gạch chân active đặc trưng Windows */}
            <span
              className={`absolute bottom-0 left-2 right-2 h-[2.5px] rounded-full transition-all ${
                !isQuickSearchOpen ? 'bg-[#2563EB]' : 'bg-[#94A3B8]/60 group-hover:bg-[#2563EB]'
              }`}
            />
          </button>
        </div>

        {/* Khay hệ thống thu nhỏ (System Tray) bên phải */}
        <div className="flex items-center gap-2 text-[#475569] text-[11px]">
          {/* Logo phần mềm chạy ngầm trên Khay thu nhỏ */}
          <div className="relative group">
            <button
              type="button"
              onClick={() => setIsQuickSearchOpen((prev) => !prev)}
              className="w-7 h-7 rounded hover:bg-white flex items-center justify-center p-1 transition-colors border border-transparent hover:border-[#CBD5E1]"
              title="Tra cứu hồ sơ Bản vẽ PDF (Đang chạy ngầm ở khay hệ thống)"
            >
              <AppIcon size={17} />
            </button>
            <span className="absolute -top-7 right-0 hidden group-hover:block bg-[#1E293B] text-white text-[10px] px-2 py-0.5 rounded whitespace-nowrap shadow-md pointer-events-none">
              Khay hệ thống: Tra cứu PDF (Shift Shift)
            </span>
          </div>

          <div className="h-4 w-[1px] bg-[#CBD5E1] mx-0.5"></div>

          {/* Tray system indicators: Audio, Network, Language, Clock */}
          <span className="px-1 font-semibold text-[10.5px] text-[#64748B]">VIE</span>

          <div className="text-right leading-tight pr-1">
            <div className="font-semibold text-[11.5px] text-[#1E293B]">
              {new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
            </div>
            <div className="text-[9.5px] text-[#64748B]">
              {new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })}
            </div>
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* CÁC HỘP THOẠI MODAL                                           */}
      {/* ------------------------------------------------------------- */}
      <LibraryModal
        isOpen={isLibraryOpen}
        onClose={() => setIsLibraryOpen(false)}
        library={library}
        onRemoveFiles={handleRemoveFiles}
        onUpdatePaths={handleUpdatePaths}
        onAddToGroup={handleAddToGroup}
        groupNames={groupNames}
      />

      <GroupManagerModal
        isOpen={isGroupManagerOpen}
        onClose={() => setIsGroupManagerOpen(false)}
        groups={groups}
        library={library}
        onSaveGroups={(newGroups) => setGroups(newGroups)}
      />

      <ViewerSettingsModal
        isOpen={isViewerSettingsOpen}
        onClose={() => setIsViewerSettingsOpen(false)}
        viewerExe={viewerExe}
        viewerTemplate={viewerTemplate}
        onSave={(exe, tmpl) => {
          setViewerExe(exe);
          setViewerTemplate(tmpl);
        }}
      />

      <HotkeySettingsModal
        isOpen={isHotkeySettingsOpen}
        onClose={() => setIsHotkeySettingsOpen(false)}
        currentHotkey={hotkey}
        onSave={(hk) => setHotkey(hk)}
      />

      <DrawingViewerModal
        bookmark={activeDrawing}
        onClose={() => setActiveDrawing(null)}
      />

      <SourceCodeModal
        isOpen={isSourceCodeOpen}
        onClose={() => setIsSourceCodeOpen(false)}
      />

      <InstallerModal
        isOpen={isInstallerOpen}
        onClose={() => setIsInstallerOpen(false)}
      />
    </div>
  );
}
