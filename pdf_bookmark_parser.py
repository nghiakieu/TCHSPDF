# -*- coding: utf-8 -*-
"""
pdf_bookmark_parser.py
=======================
Module đọc bookmark (outline) TRỰC TIẾP từ file PDF thật (không cần file .xcbkm
trung gian nữa).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import json

def _cache_path(pdf_path: str) -> Path:
    h = hashlib.md5(pdf_path.encode("utf-8")).hexdigest()[:12]
    cache_dir = Path(__file__).parent / ".bm_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{h}.json"

def _load_cache(pdf_path: str) -> Optional[List[Dict]]:
    cp = _cache_path(pdf_path)
    if not cp.exists():
        return None
    try:
        mtime = Path(pdf_path).stat().st_mtime
        data = json.loads(cp.read_text(encoding="utf-8"))
        if data.get("mtime") == mtime:
            return data.get("rows")
    except Exception:
        pass
    return None

def _save_cache(pdf_path: str, rows: List[Dict]):
    try:
        cp = _cache_path(pdf_path)
        mtime = Path(pdf_path).stat().st_mtime
        cp.write_text(json.dumps({"mtime": mtime, "rows": rows}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

try:
    import pikepdf
except ImportError:
    pikepdf = None


def _build_page_map(pdf: pikepdf.Pdf) -> Dict[tuple, int]:
    """Bảng tra: (object_id, generation) của mỗi trang -> số thứ tự trang (0-based)."""
    return {page.objgen: i for i, page in enumerate(pdf.pages)}


def _resolve_named_dest(pdf: pikepdf.Pdf, name: str):
    """Tra một named destination trong /Root/Names/Dests (nếu PDF có dùng)."""
    try:
        names = pdf.Root.get("/Names")
        if names is None:
            return None
        dests_root = names.get("/Dests")
        if dests_root is None:
            return None
        tree = pikepdf.NameTree(dests_root)
        if name in tree:
            obj = tree[name]
            if isinstance(obj, pikepdf.Dictionary) and "/D" in obj:
                return obj["/D"]
            return obj
    except Exception:
        return None
    return None


def _extract_dest_array(item: pikepdf.Dictionary, pdf: pikepdf.Pdf):
    """Lấy mảng destination [trang, /XYZ, left, top, zoom] từ một mục outline."""
    raw = item.get("/Dest")
    if raw is None:
        action = item.get("/A")
        if action is not None and str(action.get("/S", "")) == "/GoTo":
            raw = action.get("/D")
    if raw is None:
        return None
    if isinstance(raw, (pikepdf.Name,)):
        return _resolve_named_dest(pdf, str(raw)[1:])
    if isinstance(raw, (pikepdf.String,)) or isinstance(raw, str):
        return _resolve_named_dest(pdf, str(raw))
    return raw


def _dest_to_page_xyz(dest_array, page_map: Dict[tuple, int]):
    if dest_array is None:
        return None, None, None, None
    try:
        if len(dest_array) < 1:
            return None, None, None, None
    except TypeError:
        return None, None, None, None

    first = dest_array[0]
    page_idx = None
    objgen = getattr(first, "objgen", None)
    if objgen is not None and objgen in page_map:
        page_idx = page_map[objgen]
    else:
        try:
            page_idx = int(first)
        except (TypeError, ValueError):
            page_idx = None

    x = y = zoom = None
    if len(dest_array) >= 5 and str(dest_array[1]) == "/XYZ":
        try:
            x = float(dest_array[2]) if dest_array[2] is not None else None
            y = float(dest_array[3]) if dest_array[3] is not None else None
            zoom = float(dest_array[4]) if dest_array[4] is not None else None
        except (TypeError, ValueError):
            pass
    return page_idx, x, y, zoom


def parse_pdf_bookmarks(pdf_path: str) -> List[Dict]:
    """
    Đọc toàn bộ bookmark (outline) của một file PDF thật.
    Trả về danh sách dict: pdf_name, pdf_path, level, parent_path, title, page_0based, page (1-based), x, y, zoom
    """
    cached = _load_cache(pdf_path)
    if cached is not None:
        return cached

    if pikepdf is None:
        raise ImportError("pikepdf chưa được cài đặt.")

    rows: List[Dict] = []
    pdf_name = Path(pdf_path).name

    with pikepdf.open(pdf_path) as pdf:
        page_map = _build_page_map(pdf)
        outlines = pdf.Root.get("/Outlines")
        if outlines is None:
            return rows

        seen = set()
        stack = []
        first = outlines.get("/First")
        if first is not None:
            stack.append((first, 0, []))

        while stack:
            node, level, parent_titles = stack.pop()
            key = node.objgen
            if key in seen:
                continue
            seen.add(key)

            title = str(node.get("/Title", "")).strip()
            dest_arr = _extract_dest_array(node, pdf)
            page0, x, y, zoom = _dest_to_page_xyz(dest_arr, page_map)
            
            rows.append(
                {
                    "pdf_name": pdf_name,
                    "pdf_path": pdf_path,
                    "level": level,
                    "parent_path": " > ".join(parent_titles),
                    "title": title,
                    "page_0based": page0,
                    "page": (page0 + 1) if page0 is not None else None,
                    "x": x,
                    "y": y,
                    "zoom": zoom,
                }
            )
            
            nxt = node.get("/Next")
            if nxt is not None:
                stack.append((nxt, level, parent_titles))
                
            child = node.get("/First")
            if child is not None:
                stack.append((child, level + 1, parent_titles + [title]))

    _save_cache(pdf_path, rows)
    return rows


def parse_multiple_pdfs(pdf_paths: List[str]):
    """Đọc bookmark của nhiều file PDF, gộp thành một pandas.DataFrame."""
    import pandas as pd

    all_rows: List[Dict] = []
    errors: Dict[str, str] = {}
    for p in pdf_paths:
        try:
            rows = parse_pdf_bookmarks(p)
            if rows:
                all_rows.extend(rows)
        except Exception as e:
            errors[p] = str(e)
    df = pd.DataFrame(all_rows)
    return df, errors
