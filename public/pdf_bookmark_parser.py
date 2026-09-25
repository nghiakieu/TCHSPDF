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
    if pikepdf is None:
        raise ImportError("pikepdf chưa được cài đặt.")

    rows: List[Dict] = []
    pdf_name = Path(pdf_path).name

    with pikepdf.open(pdf_path) as pdf:
        page_map = _build_page_map(pdf)
        outlines = pdf.Root.get("/Outlines")
        if outlines is None:
            return rows

        def walk(node, level, parent_titles, seen):
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
            child = node.get("/First")
            while child is not None:
                key = child.objgen
                if key in seen:
                    break
                seen.add(key)
                walk(child, level + 1, parent_titles + [title], seen)
                child = child.get("/Next")

        seen_top = set()
        child = outlines.get("/First")
        while child is not None:
            key = child.objgen
            if key in seen_top:
                break
            seen_top.add(key)
            walk(child, 0, [], seen_top)
            child = child.get("/Next")

    return rows


def parse_multiple_pdfs(pdf_paths: List[str]):
    """Đọc bookmark của nhiều file PDF, gộp thành một pandas.DataFrame."""
    import pandas as pd

    all_rows: List[Dict] = []
    errors: Dict[str, str] = {}
    for p in pdf_paths:
        try:
            rows = parse_pdf_bookmarks(p)
            if not rows:
                errors[p] = "Không tìm thấy bookmark nào trong file này."
            all_rows.extend(rows)
        except Exception as e:
            errors[p] = str(e)
    df = pd.DataFrame(all_rows)
    return df, errors
