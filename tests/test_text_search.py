import pytest
from text_search import match_score, normalize, strip_diacritics

@pytest.mark.parametrize("inp,expected", [
    ("Mặt bằng tổng thể", "Mat bang tong the"),
    ("đường dẫn", "duong dan"),
    ("Hồ sơ bản vẽ", "Ho so ban ve"),
    ("TẦNG HẦM", "TANG HAM"),
])
def test_strip_diacritics(inp, expected):
    assert strip_diacritics(inp) == expected

def test_match_no_diacritic():
    # Gõ không dấu tìm nội dung có dấu
    assert match_score("mat bang", "Mặt bằng tổng thể") > 0

def test_match_fuzzy_typo():
    # Gõ sai chính tả một chút vẫn khớp (mặt bng -> mặt bằng)
    assert match_score("mat bng", "Mặt bằng tổng thể") > 0

def test_no_match():
    # Từ khóa hoàn toàn không liên quan
    assert match_score("xyz999zzz", "Mặt bằng tổng thể") == 0.0

def test_empty_query_returns_1():
    # Từ khóa trống trả về 1.0 (pass filter)
    assert match_score("", "anything") == 1.0
