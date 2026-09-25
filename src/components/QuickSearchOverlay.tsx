import React, { useState, useEffect, useRef } from 'react';
import { Search, Maximize2, FileText, ChevronRight } from 'lucide-react';
import { BookmarkRow } from '../data/mockData';
import { matchScore } from '../utils/textSearch';
import { AppIcon } from './AppIcon';

interface QuickSearchOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  onExpandToFull: (query: string) => void;
  bookmarks: BookmarkRow[];
  onOpenBookmark: (bookmark: BookmarkRow) => void;
}

export const QuickSearchOverlay: React.FC<QuickSearchOverlayProps> = ({
  isOpen,
  onClose,
  onExpandToFull,
  bookmarks,
  onOpenBookmark,
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      }, 50);
    } else {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Lọc bookmark theo thuật toán Listary
  const filteredResults = React.useMemo(() => {
    const trimmed = query.trim();
    if (!trimmed) return [];

    const scored = bookmarks
      .map((b) => ({
        bookmark: b,
        score: matchScore(trimmed, b.title, b.parent_path, b.pdf_name),
      }))
      .filter((item) => item.score > 0);

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, 8).map((s) => s.bookmark);
  }, [query, bookmarks]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  if (!isOpen) return null;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (filteredResults.length > 0) {
        setSelectedIndex((prev) => (prev + 1) % filteredResults.length);
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (filteredResults.length > 0) {
        setSelectedIndex((prev) => (prev - 1 + filteredResults.length) % filteredResults.length);
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredResults.length > 0) {
        onOpenBookmark(filteredResults[selectedIndex] || filteredResults[0]);
        onClose();
      }
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center pt-[15vh] bg-black/25 backdrop-blur-[2px]"
      onClick={onClose}
    >
      {/* Khung tìm kiếm Listary trôi nổi chuẩn phong cách tim kiem nhanh listary.png */}
      <div
        className="w-full max-w-[580px] bg-white shadow-2xl overflow-hidden flex flex-col rounded-xl border border-[#CBD5E1] ring-1 ring-black/5 animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        {/* Thanh tìm kiếm nhanh phong cách Listary: nền trắng, biểu tượng kính lúp, nút ↗ góc phải */}
        <div className="flex items-center px-4 py-2.5 bg-white">
          {/* Biểu tượng kính lúp Listary thanh mảnh */}
          <Search className="w-5 h-5 text-[#94A3B8] shrink-0 mr-3" strokeWidth={1.75} />

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm kiếm ứng dụng và tập tin (hồ sơ bản vẽ, số trang...)"
            className="flex-1 bg-transparent text-[#1E293B] text-[15px] placeholder-[#94A3B8] focus:outline-none"
          />

          {query.trim().length > 0 && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="p-1 text-[#94A3B8] hover:text-[#1E293B] rounded-full mr-2 cursor-pointer transition-colors"
              title="Xoá tìm kiếm"
            >
              <span className="text-[13px] font-bold px-1">✕</span>
            </button>
          )}

          {/* Biểu tượng ống kính Listary ◎ */}
          <span className="text-[#94A3B8] text-[15px] select-none mr-2 font-medium">◎</span>

          {/* Nút phóng to / mở rộng sang bảng điều khiển đầy đủ ↗ */}
          <button
            type="button"
            onClick={() => onExpandToFull(query)}
            title="Mở rộng ra bảng điều khiển chính"
            className="p-1 px-1.5 text-[#64748B] hover:text-[#2563EB] hover:bg-[#EFF6FF] border border-[#E2E8F0] bg-[#F8FAFC] rounded-md transition-colors cursor-pointer text-xs font-bold"
          >
            ↗
          </button>
        </div>

        {/* Danh sách kết quả: CHỈ hiện khi người dùng đã gõ từ khóa, đã bỏ dòng "Gõ để tìm..." */}
        {query.trim().length > 0 && (
          <div className="border-t border-[#E4E7EE] bg-white">
            {filteredResults.length === 0 ? (
              <div className="px-5 py-6 text-center text-[#64748B] text-[13px]">
                Không tìm thấy bookmark phù hợp với từ khoá &ldquo;{query}&rdquo;
              </div>
            ) : (
              <div className="p-2 space-y-1 max-h-[380px] overflow-y-auto">
                {filteredResults.map((item, idx) => {
                  const isSelected = idx === selectedIndex;
                  return (
                    <div
                      key={item.id}
                      onClick={() => {
                        onOpenBookmark(item);
                        onClose();
                      }}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`px-3.5 py-2.5 rounded-xl cursor-pointer transition-colors flex items-start justify-between ${
                        isSelected
                          ? 'bg-[#CFE4FF] text-[#0A2540]'
                          : 'hover:bg-[#F1F5F9] text-[#1E293B]'
                      }`}
                    >
                      <div className="flex-1 min-w-0 pr-3">
                        <div className="font-semibold text-[13px] truncate flex items-center gap-1.5">
                          {item.level > 0 && (
                            <span className="text-[#94A3B8] font-normal text-[11px]">
                              {'—'.repeat(item.level)}
                            </span>
                          )}
                          <span>{item.title}</span>
                        </div>
                        <div className="text-[11px] text-[#64748B] mt-0.5 flex items-center gap-2 truncate">
                          <span className="flex items-center gap-1 text-[#475569]">
                            <FileText className="w-3 h-3 text-[#2563EB]" strokeWidth={1.5} />
                            {item.pdf_name}
                          </span>
                          {item.parent_path && (
                            <>
                              <ChevronRight className="w-3 h-3 text-[#94A3B8]" />
                              <span className="truncate">{item.parent_path}</span>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="shrink-0 text-right">
                        <span className="inline-block px-2 py-0.5 rounded-md bg-white/80 border border-[#D2D7E2] text-[11px] font-semibold text-[#2563EB]">
                          Trang {item.page}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Dòng phím tắt footer mỏng gọn */}
            <div className="px-4 py-2 bg-[#F8FAFD] border-t border-[#E4E7EE] flex items-center justify-between text-[11px] text-[#64748B]">
              <span className="flex items-center gap-3">
                <span>↑↓ Di chuyển</span>
                <span>↵ Mở bản vẽ</span>
                <span>⤢ Mở rộng</span>
              </span>
              <span>Bấm Esc hoặc nhấp ra ngoài để đóng</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
