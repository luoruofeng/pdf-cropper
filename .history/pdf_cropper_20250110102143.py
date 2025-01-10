import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import os

def extract_and_save_pdf_without_headers_footers(pdf_path, output_pdf_path, header_height=50, footer_height=50, left_margin=0, right_margin=0, dpi=300, progress_callback=None):
    """
    提取 PDF 的正文内容，去掉页眉、页脚，并将裁剪后的内容保存为新的 PDF，同时支持裁剪左边和右边。
    :param pdf_path: PDF 文件路径
    :param output_pdf_path: 输出的新 PDF 文件路径
    :param header_height: 页眉区域高度
    :param footer_height: 页脚区域高度
    :param left_margin: 左边裁剪区域宽度
    :param right_margin: 右边裁剪区域宽度
    :param dpi: 分辨率（每英寸的点数），默认值为 300
    :param progress_callback: 进度回调函数
    """
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()  # 创建一个新的空 PDF

    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc[page_num]
        page_rect = page.rect  # 页面尺寸
        # 定义正文区域：去掉页眉、页脚以及左边和右边的区域
        crop_rect = fitz.Rect(
            page_rect.x0 + left_margin,  # 左边裁剪
            page_rect.y0 + header_height,  # 上边裁剪（页眉）
            page_rect.x1 - right_margin,  # 右边裁剪
            page_rect.y1 - footer_height  # 下边裁剪（页脚）
        )
        
        # 获取裁剪后的页面图像，并设置高分辨率
        pixmap = page.get_pixmap(clip=crop_rect, dpi=dpi)
        
        # 创建新页面并插入裁剪后的图像
        new_page = new_doc.new_page(width=pixmap.width, height=pixmap.height)
        new_page.insert_image(new_page.rect, pixmap=pixmap)

        # 更新进度
        if progress_callback:
            progress_callback(page_num + 1, total_pages)

    # 保存裁剪后的 PDF
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()

def load_pdf():
    """
    加载选定的 PDF 文件并显示第一页的缩略图。
    """
    global pdf_path
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if pdf_path:
        display_pdf_page(0)

def display_pdf_page(page_num):
    """
    显示指定页码的 PDF 内容。
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap(dpi=150)  # 获取页面图像
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    img_tk = ImageTk.PhotoImage(img)
    
    # 在 Canvas 中显示图像
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk
    doc.close()

def crop_and_save():
    """
    获取用户输入的裁剪参数，执行裁剪并保存新的 PDF。
    """
    try:
        # 获取裁剪参数
        header_height = float(header_entry.get()) * 28.35  # 转换为pt (1 cm = 28.35 pt)
        footer_height = float(footer_entry.get()) * 28.35
        left_margin = float(left_entry.get()) * 28.35
        right_margin = float(right_entry.get()) * 28.35
        
        output_pdf_path = "cropped_output.pdf"

        # 显示进度条
        progress_bar.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        progress_bar["value"] = 0
        progress_bar["maximum"] = len(fitz.open(pdf_path))

        def update_progress(current, total):
            progress_bar["value"] = (current / total) * 100
            root.update_idletasks()

        extract_and_save_pdf_without_headers_footers(pdf_path, output_pdf_path, header_height, footer_height, left_margin, right_margin, progress_callback=update_progress)
        
        messagebox.showinfo("Success", f"PDF saved as: {output_pdf_path}")
        progress_bar.grid_forget()  # 隐藏进度条

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for the crop distances.")

# 创建主窗口
root = tk.Tk()
root.title("PDF Cropper")

# 创建布局框架
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# 创建按钮和输入框
load_button = tk.Button(frame, text="Select PDF", command=load_pdf)
load_button.grid(row=0, column=0, padx=5, pady=5)

header_label = tk.Label(frame, text="Header Height (cm):")
header_label.grid(row=1, column=0, padx=5, pady=5)
header_entry = tk.Entry(frame)
header_entry.grid(row=1, column=1, padx=5, pady=5)

footer_label = tk.Label(frame, text="Footer Height (cm):")
footer_label.grid(row=2, column=0, padx=5, pady=5)
footer_entry = tk.Entry(frame)
footer_entry.grid(row=2, column=1, padx=5, pady=5)

left_label = tk.Label(frame, text="Left Margin (cm):")
left_label.grid(row=3, column=0, padx=5, pady=5)
left_entry = tk.Entry(frame)
left_entry.grid(row=3, column=1, padx=5, pady=5)

right_label = tk.Label(frame, text="Right Margin (cm):")
right_label.grid(row=4, column=0, padx=5, pady=5)
right_entry = tk.Entry(frame)
right_entry.grid(row=4, column=1, padx=5, pady=5)

crop_button = tk.Button(frame, text="Crop and Save PDF", command=crop_and_save)
crop_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# 创建进度条
progress_bar = Progressbar(frame, length=200, orient="horizontal", mode="determinate")

# 创建 Canvas 来显示 PDF 页面
canvas = tk.Canvas(root, width=600, height=800)
canvas.pack(padx=10, pady=10)

# 启动主循环
root.mainloop()
