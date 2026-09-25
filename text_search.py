# -*- coding: utf-8 -*-
"""
text_search.py
================
Tiện ích tìm kiếm "linh động" kiểu Listary, có hỗ trợ tiếng Việt:

  - Không phân biệt hoa/thường.
  - Gõ KHÔNG DẤU vẫn tìm ra nội dung CÓ DẤU (vd: "mat bang" -> "Mặt bằng").
  - Không cần gõ liền một cụm đúng thứ tự: gõ nhiều từ cách nhau bằng
    khoảng trắng, mỗi từ chỉ cần khớp (đúng, khớp một phần, hoặc gần đúng)
    với MỘT từ bất kỳ trong tiêu đề / mục cha / tên file, không cần đúng
    thứ tự xuất hiện.
  - Chấp nhận sai chính tả nhẹ (khớp mờ - fuzzy) nhờ so khớp tỉ lệ tương
    đồng giữa các từ, hữu ích khi gõ nhanh hoặc nhớ không chính xác tên.

Không phụ thuộc thư viện ngoài (chỉ dùng các module chuẩn của Python) để dễ
tái sử dụng và kiểm thử độc lập.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from functools import lru_cache
from typing import List, Sequence, Tuple

_EXTRA_MAP = str.maketrans({"đ": "d", "Đ": "D"})
_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)
_FUZZY_THRESHOLD = 0.72
_GOOD_ENOUGH = 0.92


def _is_nan(value) -> bool:
    return isinstance(value, float) and value != value


def _clean(value) -> str:
    if value is None or _is_nan(value):
        return ""
    return str(value)


@lru_cache(maxsize=20000)
def strip_diacritics(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'Mặt bằng tổng thể' -> 'Mat bang tong the'."""
    if not text:
        return ""
    text = text.translate(_EXTRA_MAP)
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", without_marks)


@lru_cache(maxsize=20000)
def normalize(text: str) -> str:
    """Chuẩn hoá để so khớp: bỏ dấu, chữ thường, gộp khoảng trắng thừa."""
    if not text:
        return ""
    text = strip_diacritics(text).lower()
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=20000)
def tokenize(normalized_text: str) -> Tuple[str, ...]:
    return tuple(_WORD_RE.findall(normalized_text))


def _best_token_ratio(token: str, target_tokens: Sequence[str]) -> float:
    best = 0.0
    for t in target_tokens:
        if token == t:
            return 1.0
        if best < _GOOD_ENOUGH:
            if token in t or t in token:
                best = max(best, _GOOD_ENOUGH)
                continue
            ratio = difflib.SequenceMatcher(None, token, t).ratio()
            if ratio > best:
                best = ratio
    return best


def match_score(query: str, *fields: str) -> float:
    """
    Điểm khớp giữa từ khoá `query` và các trường văn bản `fields`.
    0.0  = không khớp (sẽ bị lọc bỏ khỏi kết quả)
    > 0  = có khớp, càng cao càng liên quan (xếp hạng Listary).
    """
    query_norm = normalize(_clean(query))
    if not query_norm:
        return 1.0

    combined_norm = normalize(" \u241F ".join(_clean(f) for f in fields if _clean(f)))
    if not combined_norm:
        return 0.0

    score = 0.0
    if query_norm in combined_norm:
        score += 100.0
        if combined_norm.startswith(query_norm):
            score += 20.0

    q_tokens = tokenize(query_norm)
    if not q_tokens:
        return score

    target_tokens = tokenize(combined_norm)
    if not target_tokens:
        return score

    per_token_scores = [_best_token_ratio(tok, target_tokens) for tok in q_tokens]
    matched = [r for r in per_token_scores if r >= _FUZZY_THRESHOLD]

    if len(matched) < len(q_tokens):
        return score

    score += sum(matched) * 10.0
    return score


def rank(query: str, rows: Sequence, field_getter) -> List[Tuple[int, float]]:
    scored = []
    for i, row in enumerate(rows):
        s = match_score(query, *field_getter(row))
        if s > 0:
            scored.append((i, s))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored
