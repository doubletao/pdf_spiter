import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
from PIL import Image


def split_pdf_to_images(pdf_path, direction, dpi=200):
    """把 PDF 每页按方向平均一分为二，输出 1.png, 2.png..."""
    doc = fitz.open(pdf_path)
    out_dir = os.path.splitext(pdf_path)[0] + "_split"
    os.makedirs(out_dir, exist_ok=True)

    counter = 0
    for page in doc:
        # 按指定 DPI 渲染整页为图片
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        w, h = img.size
        if direction == "horizontal":
            # 横向拆分：沿竖直中线切成左右两半
            left = img.crop((0, 0, w // 2, h))
            right = img.crop((w // 2, 0, w, h))
            parts = [left, right]
        else:
            # 纵向拆分：沿水平中线切成上下两半
            top = img.crop((0, 0, w, h // 2))
            bottom = img.crop((0, h // 2, w, h))
            parts = [top, bottom]

        for part in parts:
            counter += 1
            part.save(os.path.join(out_dir, f"{counter}.png"))

    doc.close()
    return out_dir, counter


def run():
    pdf_path = filedialog.askopenfilename(
        title="选择 PDF 文件", filetypes=[("PDF 文件", "*.pdf")]
    )
    if not pdf_path:
        return

    direction = direction_var.get()
    try:
        out_dir, count = split_pdf_to_images(pdf_path, direction)
    except Exception as e:
        messagebox.showerror("出错了", str(e))
        return

    messagebox.showinfo(
        "完成",
        f"已生成 {count} 张图片\n输出目录：\n{out_dir}"
    )


root = tk.Tk()
root.title("PDF 试卷拆分工具")
root.geometry("360x180")
root.resizable(False, False)

tk.Label(root, text="拆分方向：", font=("Microsoft YaHei", 11)).pack(pady=(20, 5))

direction_var = tk.StringVar(value="horizontal")
frame = tk.Frame(root)
frame.pack()
tk.Radiobutton(frame, text="横向（左右一分为二）", variable=direction_var,
               value="horizontal", font=("Microsoft YaHei", 10)).pack(anchor="w")
tk.Radiobutton(frame, text="纵向（上下一分为二）", variable=direction_var,
               value="vertical", font=("Microsoft YaHei", 10)).pack(anchor="w")

tk.Button(root, text="选择 PDF 并开始拆分", command=run,
          font=("Microsoft YaHei", 11), width=24, height=1).pack(pady=18)

root.mainloop()