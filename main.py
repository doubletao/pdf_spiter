import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageTk

PREVIEW_MAX_W = 500
PREVIEW_MAX_H = 440

doc = None
pdf_path = None
page_index = 0
preview_photo = None


def split_pdf_to_images(pdf_path, direction, ratio, dpi=200):
    """把 PDF 每页按方向和比例一分为二，输出 1.png, 2.png..."""
    out_dir = os.path.splitext(pdf_path)[0] + "_split"
    os.makedirs(out_dir, exist_ok=True)

    counter = 0
    with fitz.open(pdf_path) as pdf:
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        for page in pdf:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            w, h = img.size
            if direction == "horizontal":
                cut = int(w * ratio)
                parts = [img.crop((0, 0, cut, h)), img.crop((cut, 0, w, h))]
            else:
                cut = int(h * ratio)
                parts = [img.crop((0, 0, w, cut)), img.crop((0, cut, w, h))]

            for part in parts:
                counter += 1
                part.save(os.path.join(out_dir, f"{counter}.png"))

    return out_dir, counter


def render_preview():
    """渲染当前页预览，并画出红色切割线"""
    global preview_photo
    canvas.delete("all")

    if doc is None:
        canvas.create_text(
            PREVIEW_MAX_W // 2, PREVIEW_MAX_H // 2,
            text="请点击右侧「选择 PDF 文件」\n即可预览页面并调整切割线",
            fill="gray", font=("Microsoft YaHei", 12), justify="center",
        )
        page_label.config(text="第 - / - 页")
        return

    page = doc[page_index]
    rect = page.rect
    if rect.width <= 0 or rect.height <= 0:
        canvas.create_text(
            PREVIEW_MAX_W // 2, PREVIEW_MAX_H // 2,
            text="该页无法预览", fill="gray", font=("Microsoft YaHei", 12),
        )
        return

    zoom = min(PREVIEW_MAX_W / rect.width, PREVIEW_MAX_H / rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    draw = ImageDraw.Draw(img)
    ratio = ratio_var.get() / 100.0
    w, h = img.size
    if direction_var.get() == "horizontal":
        x = round(w * ratio)
        draw.line([(x, 0), (x, h)], fill=(255, 0, 0), width=3)
    else:
        y = round(h * ratio)
        draw.line([(0, y), (w, y)], fill=(255, 0, 0), width=3)

    preview_photo = ImageTk.PhotoImage(img)
    canvas.create_image(PREVIEW_MAX_W // 2, PREVIEW_MAX_H // 2, image=preview_photo)
    page_label.config(text=f"第 {page_index + 1} / {len(doc)} 页")


def refresh():
    """方向/比例变化后刷新标签与预览"""
    side = "左侧" if direction_var.get() == "horizontal" else "上侧"
    ratio_label.config(text=f"{side}占比：{ratio_var.get()}%")
    render_preview()


def open_pdf():
    global doc, pdf_path, page_index
    path = filedialog.askopenfilename(
        title="选择 PDF 文件", filetypes=[("PDF 文件", "*.pdf")]
    )
    if not path:
        return

    try:
        new_doc = fitz.open(path)
    except Exception as e:
        messagebox.showerror("出错了", f"无法打开 PDF：\n{e}")
        return
    if len(new_doc) == 0:
        new_doc.close()
        messagebox.showerror("出错了", "该 PDF 没有任何页面")
        return

    if doc is not None:
        doc.close()
    doc = new_doc
    pdf_path = path
    page_index = 0
    render_preview()


def prev_page():
    global page_index
    if doc is not None and page_index > 0:
        page_index -= 1
        render_preview()


def next_page():
    global page_index
    if doc is not None and page_index < len(doc) - 1:
        page_index += 1
        render_preview()


def run():
    if doc is None:
        messagebox.showwarning("提示", "请先选择 PDF 文件")
        return

    direction = direction_var.get()
    ratio = ratio_var.get() / 100.0
    try:
        out_dir, count = split_pdf_to_images(pdf_path, direction, ratio)
    except Exception as e:
        messagebox.showerror("出错了", str(e))
        return

    messagebox.showinfo(
        "完成",
        f"已生成 {count} 张图片\n输出目录：\n{out_dir}"
    )


def on_close():
    if doc is not None:
        doc.close()
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF 试卷拆分工具")
    root.geometry("748x500")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    direction_var = tk.StringVar(value="horizontal")
    ratio_var = tk.IntVar(value=50)

    left = tk.Frame(root)
    left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(left, width=PREVIEW_MAX_W, height=PREVIEW_MAX_H,
                       bg="#f0f0f0", highlightthickness=0)
    canvas.pack()

    right = tk.Frame(root)
    right.pack(side="right", fill="y", padx=(0, 14), pady=12)

    tk.Label(right, text="拆分方向：", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(0, 2))
    tk.Radiobutton(right, text="横向（左右一分为二）", variable=direction_var,
                   value="horizontal", command=refresh,
                   font=("Microsoft YaHei", 10)).pack(anchor="w")
    tk.Radiobutton(right, text="纵向（上下一分为二）", variable=direction_var,
                   value="vertical", command=refresh,
                   font=("Microsoft YaHei", 10)).pack(anchor="w", pady=(0, 14))

    ratio_label = tk.Label(right, text="左侧占比：50%", font=("Microsoft YaHei", 10))
    ratio_label.pack(anchor="w")
    ttk.Scale(right, from_=10, to=90, variable=ratio_var, orient="horizontal",
              command=lambda _v: refresh()).pack(fill="x", pady=(2, 14))

    tk.Label(right, text="页面导航：", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(0, 4))
    nav = tk.Frame(right)
    nav.pack(anchor="w")
    tk.Button(nav, text="< 上一页", width=9, command=prev_page,
              font=("Microsoft YaHei", 9)).pack(side="left")
    tk.Button(nav, text="下一页 >", width=9, command=next_page,
              font=("Microsoft YaHei", 9)).pack(side="left", padx=(6, 0))
    page_label = tk.Label(right, text="第 - / - 页", font=("Microsoft YaHei", 10))
    page_label.pack(anchor="w", pady=(6, 0))

    tk.Button(right, text="选择 PDF 文件", command=open_pdf, width=18,
              font=("Microsoft YaHei", 11)).pack(pady=(22, 8))
    tk.Button(right, text="开始拆分", command=run, width=18,
              font=("Microsoft YaHei", 11)).pack()

    refresh()
    root.mainloop()
