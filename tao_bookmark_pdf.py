"""
Chương trình tạo Bookmark (Outline) cho file PDF từ dữ liệu trong file Excel.

YÊU CẦU FILE EXCEL:
- Cột 1: Nội dung bookmark (tiêu đề sẽ hiện trong mục lục PDF)
- Cột 2: Số trang tương ứng (số trang thực tế, bắt đầu từ 1)
- Dòng đầu tiên có thể là tiêu đề cột (chương trình sẽ tự bỏ qua nếu phát hiện)

CÀI ĐẶT THƯ VIỆN CẦN THIẾT (chạy trong Command Prompt / Terminal):
    pip install pandas pypdf openpyxl

CÁCH DÙNG:
    python tao_bookmark_pdf.py

Chương trình sẽ hỏi bạn đường dẫn file Excel và file PDF, sau đó tạo ra
một file PDF mới có bookmark, tên là "<ten_file_goc>_bookmark.pdf".

Bạn cũng có thể sửa phần "CẤU HÌNH NHANH" bên dưới để điền sẵn đường dẫn,
rồi chạy trực tiếp mà không cần nhập tay mỗi lần.
"""

import os
import sys

try:
    import pandas as pd
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Thiếu thư viện cần thiết. Vui lòng chạy lệnh sau rồi thử lại:")
    print("    pip install pandas pypdf openpyxl")
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    print("Không tìm thấy tkinter (thường có sẵn trong Python bản cài đặt "
          "chuẩn từ python.org). Vui lòng cài đặt lại Python và chọn đầy đủ "
          "thành phần tkinter.")
    sys.exit(1)


def chon_file_excel():
    """Mở hộp thoại cho người dùng chọn file Excel."""
    duong_dan = filedialog.askopenfilename(
        title="Chọn file Excel chứa danh sách bookmark",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("Tất cả file", "*.*")],
    )
    return duong_dan or None


def chon_file_pdf():
    """Mở hộp thoại cho người dùng chọn file PDF."""
    duong_dan = filedialog.askopenfilename(
        title="Chọn file PDF cần tạo bookmark",
        filetypes=[("PDF files", "*.pdf"), ("Tất cả file", "*.*")],
    )
    return duong_dan or None


def doc_danh_sach_bookmark(excel_path):
    """
    Đọc file Excel, trả về danh sách (nội_dung, số_trang).
    Tự động bỏ qua dòng tiêu đề nếu cột số trang không phải là số.
    """
    df = pd.read_excel(excel_path, header=None)

    # Chỉ lấy 2 cột đầu tiên
    df = df.iloc[:, :2]
    df.columns = ["noi_dung", "so_trang"]

    # Bỏ các dòng trống hoàn toàn
    df = df.dropna(how="all")

    ket_qua = []
    for idx, row in df.iterrows():
        noi_dung = row["noi_dung"]
        so_trang = row["so_trang"]

        # Bỏ qua dòng tiêu đề (ví dụ "Nội dung", "Số trang")
        if pd.isna(so_trang) or not str(so_trang).strip():
            continue
        try:
            so_trang_int = int(float(so_trang))
        except (ValueError, TypeError):
            # Không đổi được sang số -> có thể là dòng tiêu đề cột, bỏ qua
            continue

        if pd.isna(noi_dung) or not str(noi_dung).strip():
            continue

        ket_qua.append((str(noi_dung).strip(), so_trang_int))

    return ket_qua


def tao_pdf_co_bookmark(pdf_path, danh_sach_bookmark):
    """
    Thêm bookmark vào file PDF và GHI ĐÈ lên chính file gốc (giữ nguyên tên).

    Cách làm an toàn:
    1. Ghi kết quả ra một file tạm (VD: tailieu.pdf.tmp) trong cùng thư mục.
    2. Chỉ khi ghi file tạm THÀNH CÔNG mới thay thế file gốc bằng file tạm đó.
    3. Nếu có lỗi ở bước nào, file gốc vẫn giữ nguyên, không bị mất dữ liệu.
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    so_trang_pdf = len(reader.pages)

    # Copy toàn bộ nội dung PDF gốc sang file mới (chỉ copy tham chiếu trang,
    # không giải nén lại nội dung nên rất nhanh)
    for page in reader.pages:
        writer.add_page(page)

    so_luong_them = 0
    so_luong_bo_qua = 0

    for noi_dung, so_trang in danh_sach_bookmark:
        # Người dùng nhập số trang theo kiểu "trang thứ mấy" (bắt đầu từ 1)
        # pypdf cần chỉ số bắt đầu từ 0
        chi_so_trang = so_trang - 1

        if chi_so_trang < 0 or chi_so_trang >= so_trang_pdf:
            print(f'  ⚠️  Bỏ qua "{noi_dung}" vì số trang {so_trang} '
                  f'nằm ngoài phạm vi file PDF (PDF có {so_trang_pdf} trang).')
            so_luong_bo_qua += 1
            continue

        writer.add_outline_item(noi_dung, chi_so_trang)
        so_luong_them += 1

    # Ghi ra file tạm trước, chưa đụng vào file gốc
    file_tam = pdf_path + ".tmp"
    try:
        with open(file_tam, "wb") as f:
            writer.write(f)

        # Đóng reader để giải phóng file gốc trước khi thay thế (quan trọng trên Windows)
        if hasattr(reader, "stream") and reader.stream:
            reader.stream.close()

        # Thay thế file gốc bằng file tạm (chỉ chạy tới đây khi ghi file tạm đã ok)
        os.replace(file_tam, pdf_path)
    except Exception:
        # Có lỗi -> dọn file tạm, KHÔNG đụng vào file gốc
        if os.path.exists(file_tam):
            os.remove(file_tam)
        raise

    return so_luong_them, so_luong_bo_qua


def main():
    print("=" * 60)
    print("  CHƯƠNG TRÌNH TẠO BOOKMARK CHO PDF TỪ FILE EXCEL")
    print("=" * 60)

    # Tạo cửa sổ tkinter ẩn, chỉ dùng để hiện hộp thoại chọn file
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # đưa hộp thoại lên trên cùng

    print("\n👉 Vui lòng chọn file Excel chứa danh sách bookmark...")
    excel_path = chon_file_excel()
    if not excel_path:
        print("Bạn chưa chọn file Excel. Chương trình dừng lại.")
        return
    print(f"   Đã chọn: {excel_path}")

    print("\n👉 Vui lòng chọn file PDF cần tạo bookmark...")
    pdf_path = chon_file_pdf()
    if not pdf_path:
        print("Bạn chưa chọn file PDF. Chương trình dừng lại.")
        return
    print(f"   Đã chọn: {pdf_path}")

    print("\nĐang đọc dữ liệu từ Excel...")
    danh_sach = doc_danh_sach_bookmark(excel_path)

    if not danh_sach:
        thong_bao = ("Không tìm thấy dữ liệu bookmark hợp lệ trong file Excel.\n"
                     "Kiểm tra lại: cột 1 là nội dung, cột 2 là số trang (số nguyên).")
        print(thong_bao)
        messagebox.showwarning("Không có dữ liệu", thong_bao)
        return

    print(f"Tìm thấy {len(danh_sach)} bookmark trong file Excel.")

    # Xác nhận trước khi ghi đè, vì thao tác này sẽ thay đổi trực tiếp file gốc
    dong_y = messagebox.askyesno(
        "Xác nhận ghi đè",
        f"Chương trình sẽ GHI ĐÈ bookmark trực tiếp lên file:\n\n{pdf_path}\n\n"
        "Bạn có muốn tiếp tục không?"
    )
    if not dong_y:
        print("Bạn đã hủy thao tác. Không có gì bị thay đổi.")
        return

    print("Đang thêm bookmark và ghi đè lên file PDF gốc...")
    try:
        so_them, so_bo_qua = tao_pdf_co_bookmark(pdf_path, danh_sach)
    except Exception as loi:
        thong_bao_loi = (f"❌ Có lỗi xảy ra, file gốc KHÔNG bị thay đổi.\n\n"
                          f"Chi tiết lỗi: {loi}")
        print(thong_bao_loi)
        messagebox.showerror("Lỗi", thong_bao_loi)
        return

    ket_qua = f"✅ HOÀN TẤT! Đã thêm {so_them} bookmark.\n"
    if so_bo_qua:
        ket_qua += f"⚠️  Có {so_bo_qua} bookmark bị bỏ qua do số trang không hợp lệ.\n"
    ket_qua += f"📄 Đã ghi đè trực tiếp lên file:\n{pdf_path}"

    print("\n" + "=" * 60)
    print(ket_qua)
    print("=" * 60)

    messagebox.showinfo("Hoàn tất", ket_qua)
    root.destroy()


if __name__ == "__main__":
    main()
