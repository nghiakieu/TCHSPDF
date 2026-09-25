import pytest
from pathlib import Path
from pdf_bookmark_parser import parse_pdf_bookmarks

def test_missing_file_raises():
    with pytest.raises(Exception):
        parse_pdf_bookmarks("nonexistent_file.pdf")
