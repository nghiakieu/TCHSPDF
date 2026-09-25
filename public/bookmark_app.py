# -*- coding: utf-8 -*-
"""
bookmark_app.py
================
Ứng dụng desktop (Tkinter) - tra cứu bookmark trực tiếp từ file PDF,
lấy cảm hứng từ Listary:
  - Ẩn/hiện chuyển đổi qua lại giữa thanh tìm kiếm nhanh và bảng điều khiển chính.
  - Phím tắt gọi nhanh toàn cục (Shift 2 lần liên tiếp).
  - Sidebar nhóm cuộn mượt khi có nhiều nhóm, phần công cụ luôn ghim ở dưới.
  - Các nút công cụ căn trái đồng bộ, không màu nền nổi trội.
  - Hộp thoại danh sách file hiển thị nhắc nhở 1 dòng, highlight lựa chọn rõ nét.
  - Tinh chỉnh cỡ chữ, kích thước nút bấm hài hòa theo phong cách Listary.
  - Thanh tìm kiếm nhanh bo góc, biểu tượng thanh mảnh, không còn dòng nhắc thừa.
"""

from __future__ import annotations

import json
import math
import os
import platform
import shlex
import shutil
import subprocess
import threading
import webbrowser
from pathlib import Path
from tkinter import (
    Tk, Toplevel, Frame, Label, Entry, StringVar, Canvas, PhotoImage, filedialog,
    messagebox, simpledialog, ttk, END, BOTH, X, Y, LEFT, RIGHT, TOP, BOTTOM, E, W
)

from pdf_bookmark_parser import parse_pdf_bookmarks
from text_search import match_score

try:
    import keyboard as _keyboard_lib
except Exception:
    _keyboard_lib = None

try:
    from PIL import Image, ImageDraw, ImageTk
except Exception:
    try:
        from PIL import Image, ImageDraw
        ImageTk = None
    except Exception:
        Image = None
        ImageDraw = None
        ImageTk = None

try:
    import pystray
except Exception:
    pystray = None

CONFIG_FILE = Path(__file__).with_name("bookmark_app_config.json")

DOUBLE_SHIFT_HOTKEY = "double_shift"
DEFAULT_HOTKEY = DOUBLE_SHIFT_HOTKEY
DOUBLE_SHIFT_WINDOW = 0.35


def format_hotkey_label(hotkey: str) -> str:
    if not hotkey or hotkey == DOUBLE_SHIFT_HOTKEY:
        return "Shift Shift (bấm 2 lần)"
    return hotkey


_SYSTEM = platform.system()
FONT_FAMILY = "Segoe UI" if _SYSTEM == "Windows" else ("Helvetica Neue" if _SYSTEM == "Darwin" else "DejaVu Sans")


def F(size: float | int = 10, weight: str = "normal", bold: bool = False) -> tuple:
    w = "bold" if (bold or weight == "bold") else ("normal" if weight == "normal" else weight)
    return (FONT_FAMILY, int(round(size)), w)


class C:
    """Bảng màu chủ đạo phong cách Listary (nền sáng, điểm nhấn xanh nhạt)."""
    BG = "#F4F6F9"
    SURFACE = "#FFFFFF"
    NAVBAR_BG = "#FFFFFF"
    HEADER_BG = "#F8FAFD"
    BUTTON_BG = "#FFFFFF"
    BORDER = "#E4E7EE"
    BORDER_STRONG = "#D2D7E2"
    CARD_BORDER = "#E4E7EE"

    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    PRIMARY_LIGHT = "#EAF2FF"

    TEXT = "#1E293B"
    TEXT_MUTED = "#64748B"
    TEXT_ON_PRIMARY = "#FFFFFF"

    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    DANGER_LIGHT = "#FEE2E2"

    # Highlight rõ ràng, tương phản tốt trên nền sáng (Listary-style selection)
    SELECT_BG = "#CFE4FF"
    SELECT_FG = "#0A2540"
    ROW_ALT = "#FAFCFF"


def mk_button(parent, text, command=None, kind="secondary", width=None, anchor=None):
    style_name = f"App{kind.capitalize()}.TButton"
    btn = ttk.Button(parent, text=text, command=command, style=style_name, width=width, cursor="hand2")
    return btn


def mk_label(parent, text="", kind="body", **extra):
    presets = {
        "app_title": dict(font=F(13, "bold"), fg=C.TEXT, bg=C.NAVBAR_BG),
        "app_subtitle": dict(font=F(9), fg=C.TEXT_MUTED, bg=C.NAVBAR_BG),
        "heading": dict(font=F(11, "bold"), fg=C.TEXT, bg=C.SURFACE),
        "body": dict(font=F(9.5), fg=C.TEXT, bg=C.SURFACE),
        "muted": dict(font=F(9), fg=C.TEXT_MUTED, bg=C.SURFACE),
    }
    cfg = dict(presets.get(kind, presets["body"]))
    cfg.update(extra)
    return Label(parent, text=text, anchor="w", justify=LEFT, **cfg)


def mk_card(parent, bg=C.SURFACE, **extra):
    cfg = dict(bg=bg, highlightbackground=C.CARD_BORDER, highlightcolor=C.CARD_BORDER, highlightthickness=1, bd=0)
    cfg.update(extra)
    return Frame(parent, **cfg)


def mk_entry(parent, textvariable=None, width=None, font_size=10):
    return Entry(
        parent, textvariable=textvariable, width=width,
        font=F(font_size), bg=C.SURFACE, fg=C.TEXT,
        relief="flat", highlightthickness=1,
        highlightbackground=C.BORDER_STRONG, highlightcolor=C.PRIMARY,
        insertbackground=C.TEXT,
    )


def setup_style(root: Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Kích thước nút bấm hài hòa, biểu tượng to rõ ràng
    base_btn = dict(padding=(12, 7), relief="flat", borderwidth=1, focuscolor="")

    def _cfg_button(style_name, **overrides):
        merged = {**base_btn, "font": F(10), "anchor": "w"}
        merged.update(overrides)
        style.configure(style_name, **merged)

    _cfg_button(
        "AppPrimary.TButton",
        background=C.PRIMARY, foreground=C.TEXT_ON_PRIMARY,
        bordercolor=C.PRIMARY, lightcolor=C.PRIMARY, darkcolor=C.PRIMARY,
        font=F(9.5, "bold"),
    )
    style.map(
        "AppPrimary.TButton",
        background=[("pressed", C.PRIMARY_HOVER), ("active", C.PRIMARY_HOVER)],
        bordercolor=[("pressed", C.PRIMARY_HOVER), ("active", C.PRIMARY_HOVER)],
    )

    _cfg_button(
        "AppSecondary.TButton",
        background=C.BUTTON_BG, foreground=C.TEXT,
        bordercolor=C.BORDER_STRONG, lightcolor=C.BUTTON_BG, darkcolor=C.BUTTON_BG,
    )
    style.map(
        "AppSecondary.TButton",
        background=[("pressed", C.PRIMARY_LIGHT), ("active", C.PRIMARY_LIGHT)],
        foreground=[("pressed", C.PRIMARY), ("active", C.PRIMARY)],
        bordercolor=[("pressed", C.PRIMARY), ("active", C.PRIMARY)],
    )

    _cfg_button(
        "AppGhost.TButton",
        background=C.BG, foreground=C.TEXT_MUTED,
        bordercolor=C.BG, lightcolor=C.BG, darkcolor=C.BG, borderwidth=0,
    )
    style.map(
        "AppGhost.TButton",
        background=[("pressed", C.HEADER_BG), ("active", C.HEADER_BG)],
        foreground=[("pressed", C.PRIMARY), ("active", C.PRIMARY)],
    )

    _cfg_button(
        "AppDanger.TButton",
        background=C.BUTTON_BG, foreground=C.DANGER,
        bordercolor=C.DANGER, lightcolor=C.BUTTON_BG, darkcolor=C.BUTTON_BG,
    )
    style.map(
        "AppDanger.TButton",
        background=[("pressed", C.DANGER_LIGHT), ("active", C.DANGER_LIGHT)],
        foreground=[("pressed", C.DANGER), ("active", C.DANGER)],
    )

    # Highlight danh sách rõ nét, tương phản tốt cho nền sáng
    style.configure(
        "Treeview",
        background=C.SURFACE, fieldbackground=C.SURFACE, foreground=C.TEXT,
        rowheight=26, font=F(9.5), borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=C.HEADER_BG, foreground=C.TEXT, font=F(9.5, "bold"),
        relief="flat", borderwidth=0, padding=(8, 7),
    )
    style.map("Treeview.Heading", background=[("active", C.HEADER_BG)])
    style.map(
        "Treeview",
        background=[("selected", C.SELECT_BG)],
        foreground=[("selected", C.SELECT_FG)],
    )

    style.configure(
        "TCombobox",
        fieldbackground=C.SURFACE, background=C.SURFACE, foreground=C.TEXT,
        arrowcolor=C.TEXT_MUTED, bordercolor=C.BORDER_STRONG, padding=5,
        relief="flat",
    )
    for orient in ("Vertical", "Horizontal"):
        style.configure(
            f"{orient}.TScrollbar",
            background=C.HEADER_BG, troughcolor=C.BG, bordercolor=C.BG,
            arrowcolor=C.TEXT_MUTED, gripcount=0, relief="flat",
        )
    style.configure("TSeparator", background=C.BORDER)


def style_treeview_stripes(tree: ttk.Treeview) -> None:
    tree.tag_configure("odd", background=C.SURFACE)
    tree.tag_configure("even", background=C.ROW_ALT)


def dialog_header(parent, title: str, subtitle: str = "") -> Frame:
    head = Frame(parent, bg=C.SURFACE)
    head.pack(fill=X, padx=18, pady=(14, 6))
    mk_label(head, title, kind="heading").pack(anchor=W)
    if subtitle:
        # Giữ dòng nhắc nhở 1 dòng, không bị xuống dòng vụn
        mk_label(head, subtitle, kind="muted").pack(anchor=W, pady=(3, 0))
    ttk.Separator(parent, orient="horizontal").pack(fill=X, padx=18, pady=(0, 4))
    return head


VIEWER_PRESETS = {
    "SumatraPDF (Windows)": '"{exe}" -page {page} "{file}"',
    "Foxit PhantomPDF / Foxit Reader (Windows)": '"{exe}" "{file}" /A page={page}',
    "Adobe Acrobat / Reader (Windows)": '"{exe}" /A "page={page}" "{file}"',
    "Evince (Linux)": '"{exe}" --page-index {page} "{file}"',
    "Okular (Linux)": '"{exe}" -p {page} "{file}"',
    "Xreader (Linux)": '"{exe}" --page-index {page} "{file}"',
    "Tuỳ chỉnh khác...": '"{exe}" "{file}"',
}

_FOXIT_DEFAULT_PATHS = [
    r"C:\Program Files\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe",
    r"C:\Program Files (x86)\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe",
    r"C:\Program Files\Foxit Software\Foxit PhantomPDF\FoxitPhantomPDF.exe",
    r"C:\Program Files (x86)\Foxit Software\Foxit PhantomPDF\FoxitPhantomPDF.exe",
    r"C:\Program Files\Foxit Software\Foxit Reader\FoxitReader.exe",
    r"C:\Program Files (x86)\Foxit Software\Foxit Reader\FoxitReader.exe",
]


def _find_foxit_exe():
    found = shutil.which("FoxitPhantomPDF") or shutil.which("FoxitPhantomPDF.exe") \
        or shutil.which("FoxitReader") or shutil.which("FoxitReader.exe") \
        or shutil.which("FoxitPDFEditor") or shutil.which("FoxitPDFEditor.exe")
    if found:
        return found
    for p in _FOXIT_DEFAULT_PATHS:
        if Path(p).is_file():
            return p
    return None


def open_pdf_at_page(pdf_path: str, page_1based: int, viewer_exe: str = "", viewer_template: str = "") -> None:
    pdf_path = str(Path(pdf_path).resolve())
    page = max(1, int(page_1based))

    if viewer_exe and viewer_template:
        cmd_str = viewer_template.format(exe=viewer_exe, file=pdf_path, page=page)
        try:
            args = shlex.split(cmd_str, posix=(platform.system() != "Windows"))
            subprocess.Popen(args)
            return
        except Exception as e:
            raise RuntimeError(f"Không chạy được lệnh mở PDF: {e}")

    system = platform.system()
    sumatra = shutil.which("SumatraPDF") or shutil.which("SumatraPDF.exe")
    if sumatra:
        subprocess.Popen([sumatra, "-page", str(page), pdf_path])
        return

    if system == "Windows":
        foxit = _find_foxit_exe()
        if foxit:
            subprocess.Popen([foxit, pdf_path, "/A", f"page={page}"])
            return
        for exe in ("Acrobat.exe", "AcroRd32.exe"):
            found = shutil.which(exe)
            if found:
                subprocess.Popen([found, "/A", f"page={page}", pdf_path])
                return
        try:
            os.startfile(pdf_path)
            return
        except Exception:
            pass
    elif system == "Darwin":
        subprocess.Popen(["open", pdf_path])
        return
    else:
        for exe, args in (
            ("evince", ["--page-index", str(page)]),
            ("okular", ["-p", str(page)]),
            ("xreader", ["--page-index", str(page)]),
        ):
            found = shutil.which(exe)
            if found:
                subprocess.Popen([found, *args, pdf_path])
                return
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", pdf_path])
            return

    webbrowser.open(f"file:///{pdf_path}#page={page}")


class ViewerSettingsDialog(Toplevel):
    def __init__(self, parent, current_exe: str, current_template: str, on_save):
        super().__init__(parent)
        self.title("Chọn phần mềm mở PDF")
        self.configure(bg=C.BG)
        self.resizable(False, False)
        self.on_save = on_save

        dialog_header(self, "⚙  Phần mềm đọc PDF", "Cấu hình chương trình dùng để mở PDF và nhảy đúng trang bookmark.")

        body = Frame(self, bg=C.BG)
        body.pack(fill=BOTH, expand=True, padx=18, pady=(6, 4))

        mk_label(body, "Đường dẫn phần mềm đọc PDF (.exe):", kind="muted", bg=C.BG).grid(
            row=0, column=0, columnspan=2, sticky=W, pady=(4, 4)
        )
        self.exe_var = StringVar(value=current_exe)
        mk_entry(body, textvariable=self.exe_var, width=50).grid(row=1, column=0, sticky="we", pady=(0, 10))
        mk_button(body, "Duyệt...", command=self.browse_exe, kind="secondary").grid(
            row=1, column=1, padx=(8, 0), pady=(0, 10)
        )

        mk_label(body, "Mẫu có sẵn:", kind="muted", bg=C.BG).grid(row=2, column=0, sticky=W)
        self.preset_var = StringVar()
        preset_box = ttk.Combobox(
            body, textvariable=self.preset_var, values=list(VIEWER_PRESETS.keys()), state="readonly", width=40
        )
        preset_box.grid(row=3, column=0, columnspan=2, sticky="we", pady=(4, 10))
        preset_box.bind("<<ComboboxSelected>>", self.apply_preset)

        mk_label(body, "Mẫu dòng lệnh ({exe}, {file}, {page}):", kind="muted", bg=C.BG).grid(
            row=4, column=0, columnspan=2, sticky=W
        )
        self.template_var = StringVar(value=current_template)
        mk_entry(body, textvariable=self.template_var, width=50).grid(
            row=5, column=0, columnspan=2, sticky="we", pady=(4, 10)
        )

        mk_label(
            body, "💡 Để trống cả 2 ô trên nếu muốn chương trình TỰ ĐỘNG dò phần mềm đọc PDF có sẵn trên máy.",
            kind="muted", bg=C.BG, wraplength=440,
        ).grid(row=6, column=0, columnspan=2, sticky=W, pady=(0, 6))

        body.grid_columnconfigure(0, weight=1)

        btns = Frame(self, bg=C.BG)
        btns.pack(fill=X, padx=18, pady=(8, 16))
        mk_button(btns, "Lưu", command=self.save, kind="primary").pack(side=LEFT)
        mk_button(btns, "Xoá cấu hình", command=self.clear, kind="danger").pack(side=LEFT, padx=8)
        mk_button(btns, "Đóng", command=self.destroy, kind="ghost").pack(side=RIGHT)

    def browse_exe(self):
        filetypes = [("Chương trình", "*.exe")] if platform.system() == "Windows" else [("Tất cả", "*")]
        path = filedialog.askopenfilename(title="Chọn phần mềm đọc PDF", filetypes=filetypes)
        if path:
            self.exe_var.set(path)

    def apply_preset(self, event=None):
        name = self.preset_var.get()
        if name in VIEWER_PRESETS:
            self.template_var.set(VIEWER_PRESETS[name])

    def save(self):
        self.on_save(self.exe_var.get().strip(), self.template_var.get().strip())
        messagebox.showinfo("Đã lưu", "Đã lưu cấu hình phần mềm mở PDF.")
        self.destroy()

    def clear(self):
        self.exe_var.set("")
        self.template_var.set("")
        self.on_save("", "")
        messagebox.showinfo("Đã xoá", "Chương trình sẽ tự động dò phần mềm đọc PDF.")
        self.destroy()


class GroupPickerDialog(Toplevel):
    def __init__(self, parent, group_names, on_pick):
        super().__init__(parent)
        self.title("Thêm vào nhóm")
        self.configure(bg=C.BG)
        self.resizable(False, False)
        self.on_pick = on_pick

        dialog_header(self, "🏷  Thêm vào nhóm", "Chọn một nhóm có sẵn, hoặc tạo nhóm mới ngay tại đây.")

        body = Frame(self, bg=C.BG)
        body.pack(fill=BOTH, expand=True, padx=18, pady=(6, 4))

        mk_label(body, "Nhóm có sẵn:", kind="muted", bg=C.BG).pack(anchor=W)
        list_card = mk_card(body)
        list_card.pack(fill=BOTH, expand=True, pady=(4, 10))
        self.group_list = ttk.Treeview(list_card, columns=("name",), show="headings", height=6)
        self.group_list.heading("name", text="Tên nhóm")
        self.group_list.column("name", width=280)
        style_treeview_stripes(self.group_list)
        for i, g in enumerate(group_names):
            self.group_list.insert("", END, values=(g,), tags=("even" if i % 2 else "odd",))
        self.group_list.pack(fill=BOTH, expand=True, padx=1, pady=1)

        mk_label(body, "Hoặc nhập tên để tạo nhóm mới:", kind="muted", bg=C.BG).pack(anchor=W)
        self.new_group_var = StringVar()
        mk_entry(body, textvariable=self.new_group_var, width=40).pack(fill=X, pady=(4, 8))

        mk_button(self, "Thêm vào nhóm này", command=self.confirm, kind="primary").pack(
            anchor=W, padx=18, pady=(6, 16)
        )

    def confirm(self):
        new_name = self.new_group_var.get().strip()
        if new_name:
            self.on_pick(new_name)
            self.destroy()
            return
        sel = self.group_list.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn", "Hãy chọn 1 nhóm có sẵn hoặc nhập tên nhóm mới.")
            return
        gname = self.group_list.item(sel[0], "values")[0]
        self.on_pick(gname)
        self.destroy()


class LibraryDialog(Toplevel):
    def __init__(self, parent, library, on_remove, on_update_paths, on_add_to_group, get_group_names):
        super().__init__(parent)
        self.title("Danh sách file PDF đã thêm")
        self.configure(bg=C.BG)
        self.geometry("860x520")
        self.minsize(720, 420)
        self.on_remove = on_remove
        self.on_update_paths = on_update_paths
        self.on_add_to_group = on_add_to_group
        self.get_group_names = get_group_names

        # Dòng nhắc nhở giữ trên 1 dòng duy nhất, không bị ngắt quãng
        dialog_header(
            self, "📁  Danh sách file PDF đã thêm",
            "Có thể chọn nhiều dòng cùng lúc (giữ Ctrl hoặc Shift) để cập nhật đường dẫn hoặc thêm vào nhóm hàng loạt.",
        )

        table_card = mk_card(self)
        table_card.pack(fill=BOTH, expand=True, padx=18, pady=(8, 10))

        self.listbox = ttk.Treeview(
            table_card, columns=("name", "path"), show="headings", selectmode="extended", height=8
        )
        self.listbox.heading("name", text="Tên file")
        self.listbox.heading("path", text="Đường dẫn")
        self.listbox.column("name", width=250)
        self.listbox.column("path", width=540)
        style_treeview_stripes(self.listbox)
        for i, item in enumerate(library):
            self.listbox.insert("", END, values=(item["name"], item["path"]), tags=("even" if i % 2 else "odd",))

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=vsb.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=(1, 0), pady=1)
        vsb.pack(side=LEFT, fill=Y, pady=1, padx=(0, 1))

        btns = Frame(self, bg=C.BG)
        btns.pack(fill=X, padx=18, pady=(0, 16))
        mk_button(btns, "Cập nhật đường dẫn...", command=self.update_paths, kind="secondary").pack(
            side=LEFT, padx=(0, 8)
        )
        mk_button(btns, "Thêm vào nhóm...", command=self.add_to_group, kind="secondary").pack(
            side=LEFT, padx=(0, 8)
        )
        mk_button(btns, "Xoá khỏi danh sách", command=self.remove_selected, kind="danger").pack(side=LEFT)

    def _selected_items(self):
        sel = self.listbox.selection()
        return [(s, self.listbox.item(s, "values")) for s in sel]

    def remove_selected(self):
        items = self._selected_items()
        if not items:
            messagebox.showinfo("Chưa chọn", "Hãy chọn 1 hoặc nhiều file trước.")
            return
        names = ", ".join(v[0] for _, v in items)
        if not messagebox.askyesno("Xác nhận", f"Xoá khỏi danh sách:\n{names} ?"):
            return
        for iid, values in items:
            self.listbox.delete(iid)
            self.on_remove(values[1])

    def update_paths(self):
        items = self._selected_items()
        if not items:
            messagebox.showinfo("Chưa chọn", "Hãy chọn 1 hoặc nhiều file trước.")
            return

        if len(items) == 1:
            iid, (name, old_path) = items[0]
            new_path = filedialog.askopenfilename(
                title=f"Chọn vị trí mới cho: {name}",
                filetypes=[("PDF files", "*.pdf")],
            )
            if not new_path:
                return
            updates = {old_path: new_path}
        else:
            folder = filedialog.askdirectory(title="Chọn thư mục mới chứa các file đã chọn (giữ nguyên tên file)")
            if not folder:
                return
            updates = {}
            missing = []
            for iid, (name, old_path) in items:
                candidate = Path(folder) / name
                if candidate.is_file():
                    updates[old_path] = str(candidate)
                else:
                    missing.append(name)
            if missing:
                messagebox.showwarning(
                    "Không tìm thấy một số file",
                    "Không tìm thấy các file sau trong thư mục đã chọn:\n\n" + "\n".join(missing),
                )

        if not updates:
            return

        for iid, (name, old_path) in items:
            if old_path in updates:
                self.listbox.item(iid, values=(name, updates[old_path]))

        self.on_update_paths(updates)
        messagebox.showinfo("Hoàn tất", f"Đã cập nhật đường dẫn cho {len(updates)} file.")

    def add_to_group(self):
        items = self._selected_items()
        if not items:
            messagebox.showinfo("Chưa chọn", "Hãy chọn 1 hoặc nhiều file trước.")
            return
        paths = [values[1] for _, values in items]

        def _pick(group_name):
            self.on_add_to_group(group_name, paths)

        GroupPickerDialog(self, self.get_group_names(), _pick)


class GroupManagerDialog(Toplevel):
    def __init__(self, parent, groups: dict, library: list, on_change):
        super().__init__(parent)
        self.title("Quản lý nhóm")
        self.configure(bg=C.BG)
        self.geometry("820x560")
        self.minsize(700, 480)
        self.groups = groups
        self.library_by_path = {item["path"]: item["name"] for item in library}
        self.on_change = on_change

        dialog_header(self, "🏷  Quản lý nhóm", "Tạo, đổi tên, xoá nhóm và quản lý file PDF thuộc mỗi nhóm.")

        body = Frame(self, bg=C.BG)
        body.pack(fill=BOTH, expand=True, padx=18, pady=(6, 16))

        left = Frame(body, bg=C.BG)
        left.pack(side=LEFT, fill=Y, padx=(0, 12))
        mk_label(left, "Danh sách nhóm", kind="muted", bg=C.BG).pack(anchor=W, pady=(0, 4))

        left_card = mk_card(left)
        left_card.pack(fill=Y)
        self.group_list = ttk.Treeview(left_card, columns=("name",), show="headings", height=10)
        self.group_list.heading("name", text="Tên nhóm")
        self.group_list.column("name", width=190)
        style_treeview_stripes(self.group_list)
        self.group_list.pack(fill=Y, padx=1, pady=1)
        self.group_list.bind("<<TreeviewSelect>>", lambda e: self.refresh_members())

        gbtns = Frame(left, bg=C.BG)
        gbtns.pack(fill=X, pady=8)
        mk_button(gbtns, "+ Tạo nhóm mới", command=self.create_group, kind="primary").pack(fill=X, pady=(0, 5))
        mk_button(gbtns, "Đổi tên nhóm", command=self.rename_group, kind="secondary").pack(fill=X, pady=(0, 5))
        mk_button(gbtns, "Xoá nhóm", command=self.delete_group, kind="danger").pack(fill=X)

        right = Frame(body, bg=C.BG)
        right.pack(side=LEFT, fill=BOTH, expand=True)
        mk_label(
            right, "File PDF trong nhóm đã chọn (chọn dòng để bớt khỏi nhóm):",
            kind="muted", bg=C.BG,
        ).pack(anchor=W, pady=(0, 4))

        member_card = mk_card(right)
        member_card.pack(fill=BOTH, expand=True, pady=(0, 8))
        self.member_list = ttk.Treeview(
            member_card, columns=("name", "path"), show="headings", selectmode="extended", height=8
        )
        self.member_list.heading("name", text="Tên file")
        self.member_list.heading("path", text="Đường dẫn")
        self.member_list.column("name", width=220)
        self.member_list.column("path", width=380)
        style_treeview_stripes(self.member_list)
        self.member_list.pack(fill=BOTH, expand=True, padx=1, pady=1)

        mk_button(right, "Bớt file đã chọn khỏi nhóm", command=self.remove_members, kind="secondary").pack(anchor=W)

        self._reload_group_list()

    def _reload_group_list(self):
        self.group_list.delete(*self.group_list.get_children())
        for i, g in enumerate(self.groups.keys()):
            self.group_list.insert("", END, iid=g, values=(g,), tags=("even" if i % 2 else "odd",))

    def refresh_members(self):
        self.member_list.delete(*self.member_list.get_children())
        sel = self.group_list.selection()
        if not sel:
            return
        gname = sel[0]
        for i, p in enumerate(self.groups.get(gname, [])):
            name = self.library_by_path.get(p, Path(p).name)
            self.member_list.insert("", END, values=(name, p), tags=("even" if i % 2 else "odd",))

    def create_group(self):
        name = simpledialog.askstring("Nhóm mới", "Nhập tên nhóm mới:", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.groups:
            messagebox.showwarning("Trùng tên", "Nhóm này đã tồn tại.")
            return
        self.groups[name] = []
        self._reload_group_list()
        self.on_change()

    def rename_group(self):
        sel = self.group_list.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn", "Hãy chọn 1 nhóm trước.")
            return
        old = sel[0]
        new = simpledialog.askstring("Đổi tên nhóm", "Tên nhóm mới:", initialvalue=old, parent=self)
        if not new or not new.strip() or new.strip() == old:
            return
        new = new.strip()
        if new in self.groups:
            messagebox.showwarning("Trùng tên", "Đã có nhóm với tên này.")
            return
        self.groups[new] = self.groups.pop(old)
        self._reload_group_list()
        self.on_change()

    def delete_group(self):
        sel = self.group_list.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn", "Hãy chọn 1 nhóm trước.")
            return
        gname = sel[0]
        if messagebox.askyesno(
            "Xác nhận", f"Xoá nhóm '{gname}'?\n(Các file PDF vẫn giữ nguyên trong danh sách chính.)"
        ):
            self.groups.pop(gname, None)
            self._reload_group_list()
            self.member_list.delete(*self.member_list.get_children())
            self.on_change()

    def remove_members(self):
        sel_g = self.group_list.selection()
        if not sel_g:
            return
        gname = sel_g[0]
        sel_m = self.member_list.selection()
        if not sel_m:
            messagebox.showinfo("Chưa chọn", "Hãy chọn file cần bớt khỏi nhóm.")
            return
        paths_to_remove = {self.member_list.item(s, "values")[1] for s in sel_m}
        self.groups[gname] = [p for p in self.groups.get(gname, []) if p not in paths_to_remove]
        self.refresh_members()
        self.on_change()


class HotkeySettingsDialog(Toplevel):
    _KEYSYM_MAP = {
        "prior": "page up", "next": "page down",
        "return": "enter", "escape": "esc",
        "period": ".", "comma": ",", "minus": "-", "plus": "+", "equal": "=",
    }
    _PURE_MODIFIERS = {
        "control_l", "control_r", "alt_l", "alt_r", "shift_l", "shift_r",
        "super_l", "super_r", "caps_lock",
    }

    def __init__(self, parent, current_hotkey: str, on_save):
        super().__init__(parent)
        self.title("Đặt phím tắt gọi nhanh")
        self.configure(bg=C.BG)
        self.resizable(False, False)
        self.on_save = on_save

        dialog_header(
            self, "⌨  Phím tắt gọi ô tìm kiếm nhanh",
            "Mặc định: bấm Shift 2 LẦN LIÊN TIẾP để bật ô tìm kiếm nổi. Có thể đặt tổ hợp khác tùy chọn.",
        )

        body = Frame(self, bg=C.BG)
        body.pack(fill=BOTH, expand=True, padx=18, pady=(6, 4))

        mk_label(body, "Phím tắt hiện tại:", kind="muted", bg=C.BG).pack(anchor=W)
        self.hotkey_var = StringVar(value=current_hotkey or DEFAULT_HOTKEY)
        self.display_var = StringVar(value=format_hotkey_label(self.hotkey_var.get()))
        self.capture_entry = Entry(
            body, textvariable=self.display_var, font=F(12, "bold"), justify="center",
            bg=C.SURFACE, fg=C.PRIMARY, relief="flat", highlightthickness=1,
            highlightbackground=C.BORDER_STRONG, highlightcolor=C.PRIMARY,
        )
        self.capture_entry.pack(fill=X, pady=(4, 10), ipady=8)
        self.capture_entry.bind("<KeyPress>", self._on_key_press)
        self.capture_entry.bind("<KeyRelease>", lambda e: "break")
        self.capture_entry.bind("<Key>", lambda e: "break")
        self.capture_entry.focus_set()
        self._last_shift_time = 0.0

        mk_label(
            body, "💡 Bấm nhanh phím Shift 2 lần trong ô này để khôi phục mặc định Listary.",
            kind="muted", bg=C.BG,
        ).pack(anchor=W, pady=(0, 6))

        btns = Frame(self, bg=C.BG)
        btns.pack(fill=X, padx=18, pady=(8, 16))
        mk_button(btns, "Lưu", command=self.save, kind="primary").pack(side=LEFT)
        mk_button(btns, "Dùng mặc định (Shift Shift)", command=self.reset_default, kind="secondary").pack(
            side=LEFT, padx=8
        )
        mk_button(btns, "Đóng", command=self.destroy, kind="ghost").pack(side=RIGHT)

    def _set_hotkey(self, value: str):
        self.hotkey_var.set(value)
        self.display_var.set(format_hotkey_label(value))

    def _on_key_press(self, event):
        keysym = (event.keysym or "").lower()
        if keysym in ("shift_l", "shift_r"):
            import time as _t
            now = _t.time()
            if now - self._last_shift_time <= DOUBLE_SHIFT_WINDOW:
                self._last_shift_time = 0.0
                self._set_hotkey(DOUBLE_SHIFT_HOTKEY)
            else:
                self._last_shift_time = now
            return "break"

        if keysym in self._PURE_MODIFIERS:
            return "break"

        mods = []
        state = event.state
        if state & 0x0004:
            mods.append("ctrl")
        if state & 0x0008 or state & 0x20000:
            mods.append("alt")
        if state & 0x0001:
            mods.append("shift")

        key = self._KEYSYM_MAP.get(keysym, keysym)
        combo = "+".join(mods + [key]) if mods else key
        self._set_hotkey(combo)
        return "break"

    def save(self):
        hk = self.hotkey_var.get().strip()
        if not hk:
            messagebox.showwarning("Thiếu phím tắt", "Hãy bấm 1 tổ hợp phím trước khi lưu.")
            return
        self.on_save(hk)
        messagebox.showinfo("Đã lưu", f"Đã đặt phím tắt gọi nhanh: {format_hotkey_label(hk)}")
        self.destroy()

    def reset_default(self):
        self._set_hotkey(DEFAULT_HOTKEY)


# ---------------------------------------------------------------------------
# Khung tìm kiếm bo tròn 4 góc cao cấp phong cách Hiện đại (Modern Rounded Search Box)
# Sử dụng thuật toán đa giác cung tròn lượng giác (Trigonometric Arc Polygon)
# Giúp 4 góc cong liền mạch tuyệt đối, không có vết nứt, khe hở hay răng cưa,
# tự co giãn chiếm 100% bề rộng và hỗ trợ hiệu ứng hover/focus sang trọng.
# ---------------------------------------------------------------------------
class RoundedSearchBox(Frame):
    def __init__(
        self, parent, textvariable=None, placeholder="",
        font=None, radius=12, bg_parent="#FFFFFF", fill_bg="#F8FAFC",
        border_color="#CBD5E1", focus_color="#2563EB",
        extra_btn_text="", extra_btn_cmd=None, extra_btn_tooltip="",
        **kwargs
    ):
        super().__init__(parent, bg=bg_parent, **kwargs)

        self.radius = radius
        self.bg_parent = bg_parent
        self.fill_bg = fill_bg
        self.border_color = border_color
        self.focus_color = focus_color
        self.is_focused = False
        self.is_hovered = False
        self.placeholder = placeholder
        self.textvariable = textvariable if textvariable is not None else StringVar()
        self.font = font or F(11.5)
        self.extra_btn_cmd = extra_btn_cmd

        self.box_height = 42

        # Canvas chuyên vẽ viền và nền bo tròn
        self.canvas = Canvas(
            self, bg=self.bg_parent, bd=0, highlightthickness=0,
            height=self.box_height
        )
        self.canvas.pack(fill=X, expand=True)

        # Biểu tượng kính lúp thanh lịch
        self.icon_label = Label(
            self.canvas, text="⌕", font=F(15), bg=self.fill_bg, fg="#64748B",
            cursor="xterm"
        )
        self.icon_win = self.canvas.create_window(24, self.box_height // 2, window=self.icon_label, anchor="center")

        # Ô nhập Entry không viền (độ rộng tự động tính toán theo toàn bộ chiều rộng)
        self.entry = Entry(
            self.canvas, textvariable=self.textvariable, font=self.font,
            bg=self.fill_bg, fg=getattr(C, "TEXT", "#1E293B"),
            relief="flat", bd=0, insertbackground=getattr(C, "TEXT", "#1E293B"),
        )
        self.entry_win = self.canvas.create_window(48, self.box_height // 2, window=self.entry, anchor="w")

        # Nút xóa nhanh ✕ khi có nội dung
        self.clear_btn = Label(
            self.canvas, text="✕", font=F(9, "bold"), bg=self.fill_bg, fg="#94A3B8",
            cursor="hand2", padx=2
        )
        self.clear_btn.bind("<Button-1>", lambda e: self.clear_text())
        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.configure(fg="#1E293B"))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.configure(fg="#94A3B8"))
        self.clear_win = self.canvas.create_window(0, 0, window=self.clear_btn, state="hidden")

        # Nút phụ tùy chọn (ví dụ: nút ⤢ mở rộng ra cửa sổ chính)
        self.extra_btn = None
        self.extra_win = None
        if extra_btn_text:
            self.extra_btn = Label(
                self.canvas, text=extra_btn_text, font=F(13), bg=self.fill_bg, fg="#64748B",
                cursor="hand2", padx=4
            )
            if extra_btn_cmd:
                self.extra_btn.bind("<Button-1>", lambda e: extra_btn_cmd())
            self.extra_btn.bind("<Enter>", lambda e: self.extra_btn.configure(fg=self.focus_color))
            self.extra_btn.bind("<Leave>", lambda e: self.extra_btn.configure(fg="#64748B"))
            self.extra_win = self.canvas.create_window(0, 0, window=self.extra_btn)

        # Placeholder dạng nhãn mờ phủ bên trên (không chèn vào textvariable để tránh làm lệch bộ lọc tìm kiếm)
        self.placeholder_win = None
        if self.placeholder:
            self.placeholder_label = Label(
                self.canvas, text=self.placeholder, font=self.font,
                bg=self.fill_bg, fg=getattr(C, "TEXT_MUTED", "#94A3B8"),
                cursor="xterm"
            )
            self.placeholder_win = self.canvas.create_window(
                48, self.box_height // 2, window=self.placeholder_label, anchor="w"
            )
            self.placeholder_label.bind("<Button-1>", lambda e: self.entry.focus_set())

        # Xử lý sự kiện chuột & tiêu điểm
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.icon_label.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        # Hiệu ứng hover viền chuột
        self.canvas.bind("<Enter>", self._on_mouse_enter)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.entry.bind("<Enter>", self._on_mouse_enter)
        self.entry.bind("<Leave>", self._on_mouse_leave)

        self.textvariable.trace_add("write", lambda *a: self._on_text_changed())
        self._update_placeholder_visibility()

    def _on_mouse_enter(self, event=None):
        self.is_hovered = True
        self._redraw()

    def _on_mouse_leave(self, event=None):
        self.is_hovered = False
        self._redraw()

    def _update_placeholder_visibility(self):
        if self.placeholder_win is not None:
            txt = self.textvariable.get()
            if txt:
                self.canvas.itemconfigure(self.placeholder_win, state="hidden")
            else:
                self.canvas.itemconfigure(self.placeholder_win, state="normal")

    def _on_focus_in(self, event=None):
        self.is_focused = True
        self._redraw()

    def _on_focus_out(self, event=None):
        self.is_focused = False
        self._update_placeholder_visibility()
        self._redraw()

    def clear_text(self):
        self.textvariable.set("")
        self._update_placeholder_visibility()
        self.entry.focus_set()

    def _on_text_changed(self):
        self._update_placeholder_visibility()
        self._update_buttons_pos()

    def _update_buttons_pos(self):
        w = self.canvas.winfo_width()
        h = self.box_height
        if w < 60:
            return

        right_offset = 20
        if self.extra_win is not None:
            self.canvas.coords(self.extra_win, w - right_offset, h // 2)
            right_offset += 24

        txt = self.textvariable.get()
        if txt:
            self.canvas.coords(self.clear_win, w - right_offset, h // 2)
            self.canvas.itemconfigure(self.clear_win, state="normal")
            right_offset += 22
        else:
            self.canvas.itemconfigure(self.clear_win, state="hidden")

        # Cung cấp không gian tối đa cho Entry hiển thị văn bản dài
        entry_w = max(40, w - 54 - right_offset)
        self.entry.configure(width=max(8, int(entry_w / 8.2)))

    def _on_resize(self, event):
        self._update_buttons_pos()
        self._redraw()

    @staticmethod
    def _create_rounded_polygon_points(x1, y1, x2, y2, r, steps=16):
        """Tạo danh sách tọa độ đa giác cung tròn lượng giác siêu mượt cho 4 góc bo."""
        r = max(2, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        points = []
        corners = [
            (x2 - r, y1 + r, -math.pi / 2, 0),             # Góc trên phải
            (x2 - r, y2 - r, 0, math.pi / 2),              # Góc dưới phải
            (x1 + r, y2 - r, math.pi / 2, math.pi),        # Góc dưới trái
            (x1 + r, y1 + r, math.pi, 3 * math.pi / 2),    # Góc trên trái
        ]
        for cx, cy, start_angle, end_angle in corners:
            for i in range(steps + 1):
                theta = start_angle + (end_angle - start_angle) * (i / steps)
                points.extend([cx + r * math.cos(theta), cy + r * math.sin(theta)])
        return points

    def _redraw(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 40 or h < 16:
            return

        # Căn lề 1.5px để viền hiển thị trọn vẹn, không bị cắt mép
        pad = 2
        x1, y1 = pad, pad
        x2, y2 = w - pad - 1, h - pad - 1

        if self.is_focused:
            border_color = self.focus_color
            stroke_w = 2.0
            fill_color = "#FFFFFF"
        elif self.is_hovered:
            border_color = getattr(C, "BORDER_STRONG", "#94A3B8")
            stroke_w = 1.5
            fill_color = self.fill_bg
        else:
            border_color = self.border_color
            stroke_w = 1.5
            fill_color = self.fill_bg

        # Đồng bộ màu nền các thành phần con liền mạch tuyệt đối
        self.icon_label.configure(bg=fill_color)
        self.entry.configure(bg=fill_color)
        self.clear_btn.configure(bg=fill_color)
        if self.extra_btn is not None:
            self.extra_btn.configure(bg=fill_color)
        if self.placeholder_win is not None and hasattr(self, "placeholder_label"):
            self.placeholder_label.configure(bg=fill_color)

        # 1. Thử vẽ bằng thư viện Pillow với kỹ thuật 3x Supersampling + Lanczos
        # Giúp 4 góc cong hoàn toàn trơn mịn, khử răng cưa tuyệt đối và viền liền mạch không bị đứt đoạn
        drawn_with_pil = False
        if Image is not None and ImageDraw is not None and ImageTk is not None:
            try:
                scale = 3  # 3x supersampling
                cache_key = (w, h, fill_color, border_color, stroke_w, self.radius, self.bg_parent)
                if getattr(self, "_cached_key", None) != cache_key or getattr(self, "_cached_photo", None) is None:
                    img_w = int(w * scale)
                    img_h = int(h * scale)

                    # Lấy màu RGB nền ngoài (hỗ trợ màu khóa trong suốt)
                    try:
                        bg_rgb = self.canvas.winfo_rgb(self.bg_parent)
                        canvas_bg_rgba = (bg_rgb[0] >> 8, bg_rgb[1] >> 8, bg_rgb[2] >> 8, 255)
                    except Exception:
                        canvas_bg_rgba = (255, 255, 255, 255)

                    try:
                        fill_rgb = self.canvas.winfo_rgb(fill_color)
                        fill_rgba = (fill_rgb[0] >> 8, fill_rgb[1] >> 8, fill_rgb[2] >> 8, 255)
                    except Exception:
                        fill_rgba = (255, 255, 255, 255)

                    try:
                        border_rgb = self.canvas.winfo_rgb(border_color)
                        border_rgba = (border_rgb[0] >> 8, border_rgb[1] >> 8, border_rgb[2] >> 8, 255)
                    except Exception:
                        border_rgba = (37, 99, 235, 255)

                    img = Image.new("RGBA", (img_w, img_h), canvas_bg_rgba)
                    draw = ImageDraw.Draw(img)

                    pad_s = int(pad * scale)
                    max_r = (img_h - 2 * pad_s) / 2
                    r_s = min(self.radius * scale, max_r)
                    bw_s = int(round(stroke_w * scale))

                    draw.rounded_rectangle(
                        [pad_s, pad_s, img_w - pad_s, img_h - pad_s],
                        radius=r_s,
                        fill=fill_rgba,
                        outline=border_rgba,
                        width=bw_s
                    )

                    smooth_img = img.resize((w, h), Image.Resampling.LANCZOS)
                    self._cached_photo = ImageTk.PhotoImage(smooth_img)
                    self._cached_key = cache_key

                self.canvas.delete("round_bg")
                self.canvas.create_image(0, 0, image=self._cached_photo, anchor="nw", tags="round_bg")
                self.canvas.tag_lower("round_bg")
                drawn_with_pil = True
            except Exception:
                drawn_with_pil = False

        # 2. Phương án dự phòng thuần Tkinter (dùng 4 cung tròn + 4 đoạn thẳng nối chuẩn hình học khép kín)
        if not drawn_with_pil:
            self.canvas.delete("round_bg")
            r = max(2, min(self.radius, (h - 2 * pad) // 2))
            d = 2 * r
            # Đổ màu nền thân hình chữ nhật bo tròn
            self.canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill_color, outline="", tags="round_bg")
            self.canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill_color, outline="", tags="round_bg")
            self.canvas.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, fill=fill_color, outline="", tags="round_bg")
            self.canvas.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, fill=fill_color, outline="", tags="round_bg")
            self.canvas.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, fill=fill_color, outline="", tags="round_bg")
            self.canvas.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, fill=fill_color, outline="", tags="round_bg")
            # Vẽ 4 đoạn thẳng viền nối liền
            self.canvas.create_line(x1 + r, y1, x2 - r, y1, fill=border_color, width=stroke_w, tags="round_bg")
            self.canvas.create_line(x2, y1 + r, x2, y2 - r, fill=border_color, width=stroke_w, tags="round_bg")
            self.canvas.create_line(x1 + r, y2, x2 - r, y2, fill=border_color, width=stroke_w, tags="round_bg")
            self.canvas.create_line(x1, y1 + r, x1, y2 - r, fill=border_color, width=stroke_w, tags="round_bg")
            # Vẽ 4 góc cong bo viền
            self.canvas.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, style="arc", outline=border_color, width=stroke_w, tags="round_bg")
            self.canvas.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, style="arc", outline=border_color, width=stroke_w, tags="round_bg")
            self.canvas.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, style="arc", outline=border_color, width=stroke_w, tags="round_bg")
            self.canvas.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, style="arc", outline=border_color, width=stroke_w, tags="round_bg")
            self.canvas.tag_lower("round_bg")

    def focus_set(self):
        self.entry.focus_set()

    def get(self):
        return self.textvariable.get()

    def set(self, val):
        self.textvariable.set(val)
        self._update_placeholder_visibility()


# ---------------------------------------------------------------------------
# Ô tìm kiếm nhanh nổi kiểu Listary
# Bo 4 góc hoàn toàn, trơn mịn, viền ngoài trong suốt 100%
# Khi mở -> ẩn bảng điều khiển chính, khi đóng -> hiện lại bảng điều khiển chính.
# ---------------------------------------------------------------------------
class QuickSearchOverlay(Toplevel):
    MAX_RESULTS = 8
    WIDTH = 640
    TRANS_KEY = "#010203"  # Mã màu khóa trong suốt cho Windows (DWM ColorKey)

    def __init__(self, app: "BookmarkApp"):
        super().__init__(app.root)
        self.app = app
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Hỗ trợ độ trong suốt hoàn hảo trên Windows:
        # Biến vùng khung chữ nhật bên ngoài thành trong suốt 100%,
        # giúp người dùng chỉ nhìn thấy thanh tìm kiếm bo tròn nổi trơn mịn giữa màn hình
        self.is_trans_supported = False
        if platform.system() == "Windows":
            try:
                self.attributes("-transparentcolor", self.TRANS_KEY)
                self.is_trans_supported = True
            except Exception:
                self.is_trans_supported = False

        self.window_bg = self.TRANS_KEY if self.is_trans_supported else C.BG
        self.configure(bg=self.window_bg)

        # Khung chứa chính (trong suốt ngoài lề)
        self.container = Frame(self, bg=self.window_bg)
        self.container.pack(fill=BOTH, expand=True, padx=4, pady=4)

        # Ép độ rộng chuẩn 640px
        Frame(self.container, width=self.WIDTH, height=1, bg=self.window_bg).pack()

        self.query_var = StringVar()
        # Khung tìm kiếm nhanh bo tròn viên thuốc mềm mại (Pill Shape) chuẩn Listary
        # bg_parent được đặt bằng self.window_bg để 4 góc bo hoàn toàn trong suốt không có khung chữ nhật bao ngoài!
        self.search_box = RoundedSearchBox(
            self.container,
            textvariable=self.query_var,
            placeholder="Tìm kiếm hồ sơ bản vẽ, mục cha, số trang...",
            radius=20,
            bg_parent=self.window_bg,
            fill_bg="#FFFFFF",
            border_color=C.PRIMARY,
            focus_color=C.PRIMARY,
            extra_btn_text="⤢",
            extra_btn_cmd=self._expand_to_main_window,
            extra_btn_tooltip="Mở rộng ra bảng điều khiển chính",
        )
        self.search_box.pack(fill=X, expand=True)
        self.entry = self.search_box.entry

        # Khung kết quả (chỉ hiện khi người dùng gõ từ khóa tìm kiếm)
        self.results_container = Frame(self.container, bg=self.window_bg)
        self.results_card = Frame(
            self.results_container,
            bg=C.SURFACE,
            bd=0,
            highlightthickness=1,
            highlightbackground="#CBD5E1",
            highlightcolor=C.PRIMARY
        )
        self.results_card.pack(fill=X, expand=True, pady=(6, 0))

        self.results_frame = Frame(self.results_card, bg=C.SURFACE)
        self.results_frame.pack(fill=BOTH, expand=True, padx=2, pady=(4, 2))

        self.footer_hint = mk_label(
            self.results_card, "↑↓ chọn · Enter mở · ⤢ mở rộng · Esc đóng",
            kind="muted", bg=C.SURFACE, font=F(8.5)
        )
        self.footer_hint.pack(anchor=E, padx=12, pady=(2, 6))

        self._row_widgets = []
        self._results = []
        self._selected = -1
        self._after_id = None
        self._closing = False

        self.query_var.trace_add("write", lambda *a: self._schedule_search())
        self.entry.bind("<Down>", self._move_down)
        self.entry.bind("<Up>", self._move_up)
        self.entry.bind("<Return>", self._open_selected)
        self.entry.bind("<Escape>", lambda e: self.hide())
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<FocusOut>", self._on_focus_out)

        self._place_on_screen()
        self.lift()
        self.entry.focus_force()

    def _place_on_screen(self):
        self.update_idletasks()
        w = max(self.WIDTH, self.winfo_reqwidth())
        h = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, int(sh * 0.18))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_focus_out(self, event):
        if self._closing:
            return
        self.after(90, self._check_focus_still_inside)

    def _check_focus_still_inside(self):
        if self._closing or not self.winfo_exists():
            return
        try:
            focused = self.focus_get()
        except Exception:
            focused = None
        if focused is None:
            self.hide()

    def _expand_to_main_window(self):
        query = self.query_var.get()
        self._closing = True
        try:
            self.destroy()
        except Exception:
            pass
        self.app._quick_search = None
        # Hiện lại bảng điều khiển đầy đủ kèm từ khóa
        self.app.restore_window()
        self.app.search_var.set(query)
        self.app.apply_filter()

    def hide(self):
        if self._closing:
            return
        self._closing = True
        try:
            self.destroy()
        except Exception:
            pass
        self.app._quick_search = None
        # Khi tắt thanh tìm kiếm nhanh thì HIỆN LẠI bảng điều khiển đầy đủ
        self.app.restore_window()

    def _schedule_search(self, delay_ms: int = 80):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(delay_ms, self._run_search)

    def _run_search(self):
        query = self.query_var.get().strip()
        df = self.app.df
        results = []
        if query and df is not None and not df.empty:
            for idx, row in df.iterrows():
                score = match_score(query, row["title"], row["parent_path"], row["pdf_name"])
                if score > 0:
                    results.append((idx, row, score))
            results.sort(key=lambda t: t[2], reverse=True)
            results = results[: self.MAX_RESULTS]
        self._results = results
        self._render_results()

    def _render_results(self):
        for w in self._row_widgets:
            w.destroy()
        self._row_widgets = []

        query = self.query_var.get().strip()

        # Bỏ dòng thông tin "Gõ để tìm..." đi cho gọn; chỉ hiển thị khi có tìm kiếm
        if not query:
            # Ẩn phần kết quả khi chưa gõ gì (chỉ còn thanh tìm kiếm nổi trôi lơ lửng)
            self.results_container.pack_forget()
            self._selected = -1
            self._place_on_screen()
            return

        # Khi đã gõ từ khóa: hiển thị khung kết quả bên dưới
        self.results_container.pack(fill=X, expand=True)

        if not self._results:
            msg = "Không tìm thấy bookmark phù hợp."
            lbl = mk_label(self.results_frame, msg, kind="muted", bg=C.SURFACE)
            lbl.pack(fill=X, padx=10, pady=8)
            self._row_widgets.append(lbl)
            self._selected = -1
            self._place_on_screen()
            return

        for i, (idx, row, score) in enumerate(self._results):
            row_frame = Frame(self.results_frame, bg=C.SURFACE, cursor="hand2")
            row_frame.pack(fill=X, pady=1)

            title_txt = ("    " * int(row.get("level", 0) or 0)) + str(row["title"])
            main = mk_label(row_frame, title_txt, bg=C.SURFACE, fg=C.TEXT, font=F(10.5, "bold"))
            main.pack(anchor=W, padx=10, pady=(4, 0), fill=X)

            sub = f"📄 {row['pdf_name']}"
            if row.get("parent_path"):
                sub += f"   ›  {row['parent_path']}"
            if row.get("page") is not None:
                sub += f"    ·  Trang {row['page']}"
            subl = mk_label(row_frame, sub, kind="muted", bg=C.SURFACE, font=F(8.5))
            subl.pack(anchor=W, padx=10, pady=(0, 4), fill=X)

            for widget in (row_frame, main, subl):
                widget.bind("<Button-1>", lambda e, i=i: self._open_index(i))
                widget.bind("<Enter>", lambda e, i=i: self._highlight(i))
            self._row_widgets.append(row_frame)

        self._highlight(0)
        self._place_on_screen()

    def _highlight(self, i: int):
        self._selected = i
        for j, w in enumerate(self._row_widgets):
            bg = C.SELECT_BG if j == i else C.SURFACE
            w.configure(bg=bg)
            for child in w.winfo_children():
                child.configure(bg=bg)

    def _move_down(self, event=None):
        if self._results:
            self._highlight((self._selected + 1) % len(self._results))
        return "break"

    def _move_up(self, event=None):
        if self._results:
            self._highlight((self._selected - 1) % len(self._results))
        return "break"

    def _open_index(self, i: int):
        if 0 <= i < len(self._results):
            _idx, row, _score = self._results[i]
            self.app.open_bookmark_row(row)
            self.hide()

    def _open_selected(self, event=None):
        if self._results:
            i = self._selected if self._selected >= 0 else 0
            self._open_index(i)
        return "break"


# ---------------------------------------------------------------------------
# Cửa sổ chính
# ---------------------------------------------------------------------------
class BookmarkApp:
    ALL_GROUPS_LABEL = "Tất cả các nhóm"
    SIDEBAR_WIDTH = 230

    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Tra cứu hồ sơ PDF")
        self.root.geometry("1160x660")
        self.root.minsize(900, 500)
        self.root.configure(bg=C.BG)

        # Cài đặt logo phần mềm trên thanh Taskbar và Titlebar
        self._setup_app_icons()

        setup_style(self.root)

        self.config = self._load_config()
        self.df = None

        self._tray_icon = None
        self._hotkey_handle = None
        self._double_shift_handle = None
        self._last_shift_press = 0.0
        self._quick_search = None
        self._shown_tray_hint = False

        self._build_ui()
        self._load_library_on_startup()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close_button)
        self._init_tray()
        self._register_hotkey()

    def _load_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                cfg.setdefault("library", [])
                cfg.setdefault("viewer_exe", "")
                cfg.setdefault("viewer_template", "")
                cfg.setdefault("groups", {})
                cfg.setdefault("hotkey", DEFAULT_HOTKEY)
                return cfg
            except Exception:
                pass
        return {
            "library": [], "viewer_exe": "", "viewer_template": "", "groups": {},
            "hotkey": DEFAULT_HOTKEY,
        }

    def _save_config(self) -> None:
        CONFIG_FILE.write_text(json.dumps(self.config, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_library_on_startup(self):
        library = self.config.get("library", [])
        if not library:
            return
        valid_paths = []
        missing = []
        for item in library:
            if Path(item["path"]).is_file():
                valid_paths.append(item["path"])
            else:
                missing.append(item["path"])
        if valid_paths:
            self._parse_and_merge(valid_paths)
        if missing:
            messagebox.showwarning(
                "Không tìm thấy file",
                "Các file PDF sau đã lưu nhưng hiện không tìm thấy trên máy:\n\n" + "\n".join(missing),
            )

    # -----------------------------------------------------------------------
    # Giao diện chính: đã bỏ dòng tiêu đề trùng lặp bên dưới title bar,
    # chỉnh cỡ chữ, kích thước nút nhấn hài hòa phong cách Listary.
    # -----------------------------------------------------------------------
    def _build_ui(self):
        topbar = Frame(self.root, bg=C.NAVBAR_BG)
        topbar.pack(side=TOP, fill=X)
        Frame(self.root, bg=C.BORDER, height=1).pack(side=TOP, fill=X)

        top_inner = Frame(topbar, bg=C.NAVBAR_BG)
        top_inner.pack(fill=X, padx=16, pady=8)

        # Thanh tìm kiếm trên cùng chiếm FULL 100% bề rộng với 4 góc bo cong mượt mà
        search_row = Frame(top_inner, bg=C.NAVBAR_BG)
        search_row.pack(fill=X, expand=True)

        self.search_var = StringVar()
        self._search_after_id = None
        self.search_var.trace_add("write", lambda *a: self._schedule_filter())

        self.search_box = RoundedSearchBox(
            search_row,
            textvariable=self.search_var,
            placeholder="Tìm kiếm bookmark theo tiêu đề, mục cha, tên file PDF...",
            radius=12,
            bg_parent=C.NAVBAR_BG,
            fill_bg="#F8FAFC",
            border_color=C.BORDER_STRONG,
            focus_color=C.PRIMARY,
        )
        self.search_box.pack(fill=X, expand=True)
        self.search_entry = self.search_box.entry
        self.search_box.focus_set()

        content = Frame(self.root, bg=C.BG)
        content.pack(side=TOP, fill=BOTH, expand=True)

        # Sidebar Lọc theo nhóm & Công cụ
        sidebar_outer = Frame(content, bg=C.BG, width=self.SIDEBAR_WIDTH)
        sidebar_outer.pack(side=LEFT, fill=Y, padx=(12, 6), pady=(8, 8))
        sidebar_outer.pack_propagate(False)
        self._build_sidebar(sidebar_outer)

        right = Frame(content, bg=C.BG)
        right.pack(side=LEFT, fill=BOTH, expand=True, padx=(6, 12), pady=(8, 8))

        table_card = mk_card(right)
        table_card.pack(side=TOP, fill=BOTH, expand=True)
        table_frame = Frame(table_card, bg=C.SURFACE)
        table_frame.pack(fill=BOTH, expand=True, padx=1, pady=1)

        columns = ("file", "muc", "tieu_de", "trang", "nhom")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {
            "file": "📄 File PDF",
            "muc": "Thuộc mục (cha)",
            "tieu_de": "Tiêu đề bookmark",
            "trang": "Trang",
            "nhom": "🏷 Nhóm",
        }
        widths = {"file": 210, "muc": 200, "tieu_de": 320, "trang": 55, "nhom": 140}
        anchors = {"trang": "center"}
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor=anchors.get(c, "w"))
        style_treeview_stripes(self.tree)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=LEFT, fill=Y)

        self.tree.bind("<Double-1>", lambda e: self.open_selected())

        footer = Frame(self.root, bg=C.HEADER_BG)
        footer.pack(side=BOTTOM, fill=X)
        Frame(self.root, bg=C.BORDER, height=1).pack(side=BOTTOM, fill=X)
        self.status_var = StringVar(value="Chưa có dữ liệu. Hãy bấm 'Thêm file PDF' để bắt đầu.")
        Label(
            footer, textvariable=self.status_var, anchor="w",
            bg=C.HEADER_BG, fg=C.TEXT_MUTED, font=F(9), padx=14, pady=6,
        ).pack(side=LEFT, fill=X, expand=True)

    def _install_placeholder(self, entry: Entry, var: StringVar, placeholder: str):
        def _show():
            if not var.get():
                entry.configure(fg=C.TEXT_MUTED)
                entry._placeholder_active = True
                entry.insert(0, placeholder)

        def _clear(event=None):
            if getattr(entry, "_placeholder_active", False):
                entry.delete(0, END)
                entry.configure(fg=C.TEXT)
                entry._placeholder_active = False

        def _restore(event=None):
            if not entry.get():
                _show()

        entry._placeholder_active = False
        entry.bind("<FocusIn>", _clear)
        entry.bind("<FocusOut>", _restore)
        _show()

    # -----------------------------------------------------------------------
    # Sidebar: Phần CÔNG CỤ ghim ở BOTTOM (không bao giờ bị che khuất).
    # Nút thêm file bỏ màu nền nổi trội, căn lề trái đồng bộ các nút khác.
    # Phần danh sách nhóm có Canvas cuộn mượt khi có nhiều nhóm.
    # -----------------------------------------------------------------------
    def _build_sidebar(self, parent):
        card = mk_card(parent)
        card.pack(fill=BOTH, expand=True)
        inner = Frame(card, bg=C.SURFACE)
        inner.pack(fill=BOTH, expand=True, padx=2, pady=2)

        # 1. CÔNG CỤ: pack ở BOTTOM để luôn nhìn thấy và bấm được
        tools_box = Frame(inner, bg=C.SURFACE)
        tools_box.pack(side=BOTTOM, fill=X, padx=8, pady=(0, 8))

        ttk.Separator(tools_box, orient="horizontal").pack(fill=X, pady=(2, 8))
        mk_label(tools_box, "CÔNG CỤ", kind="muted", bg=C.SURFACE, font=F(8.5, "bold")).pack(
            anchor=W, padx=4, pady=(0, 4)
        )

        tools = Frame(tools_box, bg=C.SURFACE)
        tools.pack(fill=X)

        # Căn lề trái, nút thêm file dùng kiểu secondary đồng bộ nền trắng với các nút khác
        mk_button(tools, "＋  Thêm file PDF", command=self.add_pdfs, kind="secondary").pack(
            fill=X, pady=(0, 4)
        )
        mk_button(tools, "📁  Danh sách file đã thêm", command=self.show_library, kind="secondary").pack(
            fill=X, pady=(0, 4)
        )
        mk_button(tools, "🏷  Quản lý nhóm", command=self.show_group_manager, kind="secondary").pack(
            fill=X, pady=(0, 4)
        )
        mk_button(tools, "⚙  Phần mềm mở PDF", command=self.show_viewer_settings, kind="secondary").pack(
            fill=X, pady=(0, 4)
        )
        mk_button(tools, "⌨  Phím tắt tìm nhanh", command=self.show_hotkey_settings, kind="secondary").pack(
            fill=X, pady=(0, 4)
        )
        mk_button(tools, "⌕  Tìm nhanh nổi (Shift Shift)", command=self.show_quick_search, kind="secondary").pack(
            fill=X, pady=(0, 4)
        )
        mk_button(tools, "📦  Xuất bản cài đặt (.exe)", command=self.show_installer_export, kind="secondary").pack(
            fill=X
        )

        # 2. LỌC THEO NHÓM: đặt ở phần trên, có cuộn khi thêm nhiều nhóm
        mk_label(inner, "LỌC THEO NHÓM", kind="muted", bg=C.SURFACE, font=F(8.5, "bold")).pack(
            anchor=W, padx=12, pady=(10, 4)
        )

        group_scroll_wrap = Frame(inner, bg=C.SURFACE)
        group_scroll_wrap.pack(side=TOP, fill=BOTH, expand=True, padx=(4, 2), pady=(0, 4))

        self._group_canvas = Canvas(group_scroll_wrap, bg=C.SURFACE, highlightthickness=0, bd=0)
        self._group_vsb = ttk.Scrollbar(group_scroll_wrap, orient="vertical", command=self._group_canvas.yview)
        self._group_items_frame = Frame(self._group_canvas, bg=C.SURFACE)

        self._group_canvas_window = self._group_canvas.create_window(
            (0, 0), window=self._group_items_frame, anchor="nw"
        )
        self._group_canvas.configure(yscrollcommand=self._group_vsb.set)

        self._group_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self._group_vsb.pack(side=RIGHT, fill=Y)

        def _on_frame_cfg(e):
            self._group_canvas.configure(scrollregion=self._group_canvas.bbox("all"))

        def _on_canvas_cfg(e):
            self._group_canvas.itemconfig(self._group_canvas_window, width=e.width)

        self._group_items_frame.bind("<Configure>", _on_frame_cfg)
        self._group_canvas.bind("<Configure>", _on_canvas_cfg)

        self._group_item_widgets = {}
        self.group_filter_var = StringVar(value=self.ALL_GROUPS_LABEL)
        self._refresh_group_filter_values()

    def _select_group(self, name: str):
        self.group_filter_var.set(name)
        self._highlight_group_items()
        self.apply_filter()

    def _highlight_group_items(self):
        selected = self.group_filter_var.get()
        for name, (row, label) in self._group_item_widgets.items():
            is_sel = name == selected
            bg = C.PRIMARY_LIGHT if is_sel else C.SURFACE
            fg = C.PRIMARY if is_sel else C.TEXT
            row.configure(bg=bg)
            label.configure(bg=bg, fg=fg, font=F(9.5, "bold" if is_sel else "normal"))

    def _refresh_group_filter_values(self):
        for row, _label in self._group_item_widgets.values():
            row.destroy()
        self._group_item_widgets = {}

        names = [self.ALL_GROUPS_LABEL] + list(self.config.get("groups", {}).keys())
        if self.group_filter_var.get() not in names:
            self.group_filter_var.set(self.ALL_GROUPS_LABEL)

        for name in names:
            icon = "🗂" if name == self.ALL_GROUPS_LABEL else "🏷"
            row = Frame(self._group_items_frame, bg=C.SURFACE, cursor="hand2")
            row.pack(fill=X, pady=1)
            label = Label(
                row, text=f"{icon}  {name}", anchor="w", justify=LEFT,
                bg=C.SURFACE, fg=C.TEXT, font=F(9.5), padx=8, pady=5,
            )
            label.pack(fill=X)
            for w in (row, label):
                w.bind("<Button-1>", lambda e, n=name: self._select_group(n))
            self._group_item_widgets[name] = (row, label)

        self._highlight_group_items()

    def add_pdfs(self):
        paths = filedialog.askopenfilenames(title="Chọn file PDF", filetypes=[("PDF files", "*.pdf")])
        if not paths:
            return

        norm_paths = [str(Path(p).resolve()) for p in paths]
        existing_paths = {str(Path(item["path"]).resolve()) for item in self.config.get("library", [])}
        for p in norm_paths:
            if p not in existing_paths:
                self.config.setdefault("library", []).append({"name": Path(p).name, "path": p})
        self._save_config()

        # Đặt lại bộ lọc nhóm về Tất cả các nhóm để file mới thêm hiển thị ngay
        self.group_filter_var.set(self.ALL_GROUPS_LABEL)
        self._refresh_group_filter_values()

        # Nạp dữ liệu bookmark và đồng bộ lên giao diện ngay lập tức
        self._parse_and_merge(norm_paths)
        self.apply_filter()
        self.root.update_idletasks()
        self.root.update()

    def _parse_and_merge(self, pdf_paths):
        import pandas as pd

        self.status_var.set("Đang đọc bookmark từ file PDF...")
        self.root.update_idletasks()

        new_rows = []
        errors = {}
        for p in pdf_paths:
            try:
                rows = parse_pdf_bookmarks(p)
                if not rows:
                    errors[p] = "Không có bookmark trong file này."
                new_rows.extend(rows)
            except Exception as e:
                errors[p] = str(e)

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            if self.df is None or self.df.empty:
                self.df = new_df
            else:
                self.df = self.df[~self.df["pdf_path"].isin(pdf_paths)]
                self.df = pd.concat([self.df, new_df], ignore_index=True)

        self.apply_filter()
        self.root.update_idletasks()
        self.root.update()

        if errors:
            msg = "\n".join(f"- {Path(p).name}: {m}" for p, m in errors.items())
            messagebox.showwarning("Một số file có vấn đề", msg)

    def show_library(self):
        library = self.config.get("library", [])
        if not library:
            messagebox.showinfo("Trống", "Chưa có file PDF nào được thêm.")
            return
        LibraryDialog(
            self.root,
            library,
            on_remove=self.remove_from_library,
            on_update_paths=self.update_library_paths,
            on_add_to_group=self.add_paths_to_group,
            get_group_names=lambda: list(self.config.get("groups", {}).keys()),
        )

    def remove_from_library(self, path):
        self.config["library"] = [i for i in self.config.get("library", []) if i["path"] != path]
        groups = self.config.get("groups", {})
        for gname in list(groups.keys()):
            groups[gname] = [p for p in groups[gname] if p != path]
        self._save_config()
        self._refresh_group_filter_values()
        if self.df is not None and not self.df.empty:
            self.df = self.df[self.df["pdf_path"] != path]
        self.apply_filter()

    def update_library_paths(self, updates: dict) -> None:
        if not updates:
            return
        for item in self.config.get("library", []):
            if item["path"] in updates:
                new_path = updates[item["path"]]
                item["path"] = new_path
                item["name"] = Path(new_path).name

        groups = self.config.get("groups", {})
        for gname, paths in groups.items():
            groups[gname] = [updates.get(p, p) for p in paths]

        self._save_config()

        if self.df is not None and not self.df.empty:
            self.df["pdf_path"] = self.df["pdf_path"].apply(lambda p: updates.get(p, p))
            self.df["pdf_name"] = self.df["pdf_path"].apply(lambda p: Path(p).name)
            self.apply_filter()

    def show_group_manager(self):
        groups = self.config.setdefault("groups", {})
        library = self.config.get("library", [])
        if not library:
            messagebox.showinfo("Trống", "Chưa có file PDF nào để đưa vào nhóm.")
            return
        GroupManagerDialog(self.root, groups, library, on_change=self._on_groups_changed)

    def _on_groups_changed(self):
        self._save_config()
        self._refresh_group_filter_values()
        self.apply_filter()

    def add_paths_to_group(self, group_name, paths):
        groups = self.config.setdefault("groups", {})
        lst = groups.setdefault(group_name, [])
        added = 0
        for p in paths:
            if p not in lst:
                lst.append(p)
                added += 1
        self._save_config()
        self._refresh_group_filter_values()
        messagebox.showinfo("Hoàn tất", f"Đã thêm {added} file vào nhóm '{group_name}'.")

    def _groups_for_path(self, path: str) -> str:
        groups = self.config.get("groups", {})
        return ", ".join(g for g, paths in groups.items() if path in paths)

    def show_viewer_settings(self):
        def save_cb(exe, template):
            self.config["viewer_exe"] = exe
            self.config["viewer_template"] = template
            self._save_config()

        ViewerSettingsDialog(
            self.root, self.config.get("viewer_exe", ""), self.config.get("viewer_template", ""), save_cb
        )

    # -----------------------------------------------------------------------
    # Khi bật thanh tìm kiếm nhanh thì ẩn bảng điều khiển đầy đủ và ngược lại
    # -----------------------------------------------------------------------
    def show_quick_search(self):
        if self._quick_search is not None and self._quick_search.winfo_exists():
            self._quick_search.hide()
            return
        # Ẩn cửa sổ chính khi mở tìm kiếm nhanh
        self.root.withdraw()
        self._quick_search = QuickSearchOverlay(self)

    def show_hotkey_settings(self):
        def save_cb(hotkey: str):
            self.config["hotkey"] = hotkey
            self._save_config()
            self._register_hotkey()

        HotkeySettingsDialog(self.root, self.config.get("hotkey", DEFAULT_HOTKEY), save_cb)

    def _register_hotkey(self):
        if _keyboard_lib is None:
            return
        if self._hotkey_handle is not None:
            try:
                _keyboard_lib.remove_hotkey(self._hotkey_handle)
            except Exception:
                pass
            self._hotkey_handle = None
        if self._double_shift_handle is not None:
            try:
                _keyboard_lib.unhook_key(self._double_shift_handle)
            except Exception:
                pass
            self._double_shift_handle = None

        hk = self.config.get("hotkey", DEFAULT_HOTKEY)
        if hk == DOUBLE_SHIFT_HOTKEY:
            self._last_shift_press = 0.0

            def _on_shift(event):
                if event.event_type != "up":
                    return
                import time as _t
                now = _t.time()
                if now - self._last_shift_press <= DOUBLE_SHIFT_WINDOW:
                    self._last_shift_press = 0.0
                    self.root.after(0, self.show_quick_search)
                else:
                    self._last_shift_press = now

            try:
                self._double_shift_handle = _keyboard_lib.hook_key("shift", _on_shift)
            except Exception as e:
                self._double_shift_handle = None
                print(f"[Cảnh báo] Lỗi phím tắt Shift Shift: {e}")
            return

        try:
            self._hotkey_handle = _keyboard_lib.add_hotkey(
                hk, lambda: self.root.after(0, self.show_quick_search)
            )
        except Exception as e:
            self._hotkey_handle = None
            print(f"[Cảnh báo] Lỗi phím tắt {hk}: {e}")

    def show_installer_export(self):
        """Mở hộp thoại hướng dẫn và khởi chạy công cụ đóng gói bộ cài đặt Windows (.exe)."""
        msg = (
            "HƯỚNG DẪN XUẤT BẢN BỘ CÀI ĐẶT WINDOWS (.EXE):\n\n"
            "Thư mục ứng dụng đã được tích hợp sẵn 2 công cụ đóng gói độc lập:\n"
            "1. 'build_installer.bat': Nhấp đúp chuột để tự động đóng gói ứng dụng\n"
            "   thành file độc lập 'TraCuuBanVePDF.exe' (không cần cài Python).\n\n"
            "2. 'installer_script.iss': Dùng với phần mềm Inno Setup (miễn phí) để\n"
            "   tạo file cài đặt 'Setup_TraCuuBanVePDF_v1.0.exe' có biểu tượng ngoài\n"
            "   màn hình Desktop và khởi động cùng Windows.\n\n"
            "Bạn có muốn mở thư mục chứa công cụ đóng gói ngay bây giờ không?"
        )
        if messagebox.askyesno("Xuất bản bộ cài đặt Windows (.exe)", msg):
            try:
                base_dir = str(Path(__file__).parent.resolve())
                if platform.system() == "Windows":
                    os.startfile(base_dir)
                elif platform.system() == "Darwin":
                    import subprocess
                    subprocess.Popen(["open", base_dir])
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", base_dir])
            except Exception as e:
                messagebox.showinfo("Đường dẫn thư mục", str(Path(__file__).parent.resolve()))

    def _setup_app_icons(self):
        """Thiết lập biểu tượng phần mềm trên thanh Taskbar và Titlebar."""
        if platform.system() == "Windows":
            try:
                import ctypes
                myappid = "pdf.bookmark.listary.app.v1"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass

        try:
            from tkinter import PhotoImage
            icon_file = Path(__file__).with_name("app_icon.png")
            if icon_file.is_file():
                self._app_icon_photo = PhotoImage(file=str(icon_file))
                self.root.iconphoto(True, self._app_icon_photo)
            elif Image is not None:
                from PIL import ImageTk
                img = self._build_tray_image()
                if img is not None:
                    self._app_icon_photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, self._app_icon_photo)
        except Exception as e:
            print(f"[Cảnh báo] Không nạp được biểu tượng cửa sổ: {e}")

    def _build_tray_image(self):
        """Vẽ hoặc nạp biểu tượng logo phần mềm (Hồ sơ PDF đỏ + Kính lúp xanh cán cam) cho khay hệ thống."""
        icon_file = Path(__file__).with_name("app_icon.png")
        if icon_file.is_file() and Image is not None:
            try:
                return Image.open(str(icon_file)).convert("RGBA")
            except Exception:
                pass

        if Image is None or ImageDraw is None:
            return None

        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 1. Lớp giấy trắng nền đáy
        draw.rounded_rectangle([9, 8, 55, 59], radius=5, fill=(255, 255, 255, 255))

        # 2. Khung tài liệu PDF màu đỏ với góc gập trên phải
        draw.polygon([(11, 8), (43, 8), (54, 19), (54, 57), (11, 57)], fill=(234, 67, 53, 255))

        # 3. Góc gập trên phải màu hồng nhạt
        draw.polygon([(43, 8), (54, 19), (43, 19)], fill=(252, 165, 165, 255))

        # 4. Các vạch tài liệu màu hồng
        draw.rounded_rectangle([16, 33, 34, 36], radius=2, fill=(252, 165, 165, 255))
        draw.rounded_rectangle([16, 40, 34, 43], radius=2, fill=(252, 165, 165, 255))
        draw.rounded_rectangle([16, 47, 28, 50], radius=2, fill=(252, 165, 165, 255))

        # 5. Cán kính lúp màu cam vàng hướng chéo xuống phải
        draw.line([46, 46, 60, 60], fill=(245, 158, 11, 255), width=5)

        # 6. Khung kính lúp tròn màu xanh dương
        draw.ellipse([25, 25, 52, 52], fill=(224, 242, 254, 230), outline=(37, 99, 235, 255), width=4)
        # Điểm sáng phản chiếu trên kính
        draw.arc([27, 27, 50, 50], start=160, end=250, fill=(255, 255, 255, 255), width=2)
        return img

    def _init_tray(self):
        if pystray is None or Image is None or ImageDraw is None:
            return
        try:
            image = self._build_tray_image()
            menu = pystray.Menu(
                pystray.MenuItem(
                    "⌕ Tìm kiếm nhanh", lambda icon, item: self.root.after(0, self.show_quick_search),
                    default=True,
                ),
                pystray.MenuItem("🗂 Mở cửa sổ chính", lambda icon, item: self.root.after(0, self.restore_window)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("⌨ Đổi phím tắt...", lambda icon, item: self.root.after(0, self.show_hotkey_settings)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Thoát hẳn", lambda icon, item: self.root.after(0, self.quit_app)),
            )
            self._tray_icon = pystray.Icon(
                "bookmark_pdf_app", image, "Tra cứu hồ sơ Bản vẽ PDF", menu
            )

            def _run():
                try:
                    self._tray_icon.run()
                except Exception as e:
                    print(f"[Cảnh báo] Khay hệ thống: {e}")

            threading.Thread(target=_run, daemon=True).start()
        except Exception as e:
            self._tray_icon = None

    def _on_close_button(self):
        if self._tray_icon is not None:
            if not self._shown_tray_hint:
                self._shown_tray_hint = True
                messagebox.showinfo(
                    "Vẫn chạy ngầm",
                    "Cửa sổ đã ẩn, chương trình vẫn chạy ngầm.\n\n"
                    f"• Bấm '{format_hotkey_label(self.config.get('hotkey', DEFAULT_HOTKEY))}' "
                    "để mở ô tìm kiếm nhanh.\n"
                    "• Chuột phải vào biểu tượng khay hệ thống để mở lại hoặc thoát hẳn.",
                )
            self.root.withdraw()
        else:
            if messagebox.askyesno("Thoát", "Thoát chương trình ngay bây giờ?"):
                self.quit_app()

    def restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        try:
            if self._tray_icon is not None:
                self._tray_icon.stop()
        except Exception:
            pass
        try:
            if _keyboard_lib is not None and self._hotkey_handle is not None:
                _keyboard_lib.remove_hotkey(self._hotkey_handle)
        except Exception:
            pass
        try:
            if _keyboard_lib is not None and self._double_shift_handle is not None:
                _keyboard_lib.unhook_key(self._double_shift_handle)
        except Exception:
            pass
        self.root.destroy()
        os._exit(0)

    def _schedule_filter(self, delay_ms: int = 120):
        if self._search_after_id is not None:
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(delay_ms, self.apply_filter)

    def apply_filter(self):
        self.tree.delete(*self.tree.get_children())
        if self.df is None or self.df.empty:
            self.status_var.set("Chưa có dữ liệu. Hãy bấm 'Thêm file PDF...' để bắt đầu.")
            return
        df = self.df

        group_name = self.group_filter_var.get()
        in_group = bool(group_name) and group_name != self.ALL_GROUPS_LABEL
        if in_group:
            group_paths = set(self.config.get("groups", {}).get(group_name, []))
            df = df[df["pdf_path"].isin(group_paths)]

        keyword = self.search_var.get().strip()
        if keyword:
            scores = df.apply(
                lambda r: match_score(keyword, r["title"], r["parent_path"], r["pdf_name"]),
                axis=1,
            )
            df = df[scores > 0]
            if not df.empty:
                df = df.assign(_score=scores[scores > 0]).sort_values(
                    "_score", ascending=False, kind="mergesort"
                )

        for i, (idx, row) in enumerate(df.iterrows()):
            self.tree.insert(
                "",
                END,
                iid=str(idx),
                values=(
                    row["pdf_name"],
                    row["parent_path"],
                    ("    " * int(row["level"])) + row["title"],
                    row["page"],
                    self._groups_for_path(row["pdf_path"]),
                ),
                tags=("even" if i % 2 else "odd",),
            )

        n_files = df["pdf_path"].nunique() if not df.empty else 0
        n_rows = len(df)
        scope = f"Nhóm '{group_name}'" if in_group else "Tất cả"
        self.status_var.set(f"ℹ  {scope}: đã có {n_rows} bookmark từ {n_files} file PDF.")

    def _selected_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một dòng bookmark trước.")
            return None
        idx = int(sel[0])
        return self.df.loc[idx]

    def open_selected(self):
        row = self._selected_row()
        if row is None:
            return
        self.open_bookmark_row(row)

    def open_bookmark_row(self, row) -> bool:
        pdf_path = row["pdf_path"]
        if not pdf_path or not Path(pdf_path).is_file():
            messagebox.showwarning("Không tìm thấy file", f"Không tìm thấy file PDF:\n{pdf_path}")
            return False
        if row["page"] is None:
            messagebox.showwarning("Thiếu số trang", "Bookmark này không có thông tin số trang hợp lệ.")
            return False
        try:
            open_pdf_at_page(
                pdf_path,
                int(row["page"]),
                viewer_exe=self.config.get("viewer_exe", ""),
                viewer_template=self.config.get("viewer_template", ""),
            )
            return True
        except Exception as e:
            messagebox.showerror("Lỗi mở PDF", str(e))
            return False


def main():
    try:
        root = Tk()
        BookmarkApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print("\n" + "=" * 60)
        print("LỖI KHỞI ĐỘNG ỨNG DỤNG:")
        print("=" * 60)
        print(err_msg)
        print("=" * 60)
        try:
            messagebox.showerror(
                "Lỗi khởi động Tra cứu hồ sơ PDF",
                f"Không thể khởi động chương trình:\n\n{e}\n\nChi tiết:\n{err_msg}"
            )
        except Exception:
            pass
        try:
            input("\nBấm Enter để đóng cửa sổ...")
        except Exception:
            pass


if __name__ == "__main__":
    main()
