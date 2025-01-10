import fitz  # PyMuPDF
from tkinter import Tk, Label, Entry, Button, Canvas, filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import fitz

def extract_and_save_pdf_without_headers_footers(pdf_path, output_pdf_path, header_height=50, footer_height=50, left_margin=0, right_margin=0, dpi=300, progress_callback=None):
    """
    提取 PDF 的正文内容，去掉页眉、页脚，并将裁剪后的内容保存为新的 PDF，同时支持裁剪左边和右边。
    """
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()  # 创建一个新的空 PDF

    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc[page_num]
        page_rect = page.rect  # 页面尺寸
        crop_rect = fitz.Rect(
            page_rect.x0 + left_margin, 
            page_rect.y0 + header_height,
            page_rect.x1 - right_margin, 
            page_rect.y1 - footer_height
        )
        pixmap = page.get_pixmap(clip=crop_rect, dpi=dpi)
        new_page = new_doc.new_page(width=pixmap.width, height=pixmap.height)
        new_page.insert_image(new_page.rect, pixmap=pixmap)

        if progress_callback:
            progress_callback(page_num + 1, total_pages)

    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()

def process_pdf_or_folder(pdf_path, output_folder, header_height=50, footer_height=50, left_margin=0, right_margin=0, dpi=300, progress_callback=None):
    """
    如果 pdf_path 是文件夹路径，则递归该文件夹下的所有 PDF 文件；如果是 PDF 文件，则直接处理该文件。
    """
    if os.path.isdir(pdf_path):
        # 如果是文件夹路径，递归处理该文件夹下的所有 PDF 文件
        for root, _, files in os.walk(pdf_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_pdf_path = os.path.join(root, file)
                    output_pdf_path = os.path.join(output_folder, os.path.relpath(full_pdf_path, pdf_path))
                    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
                    extract_and_save_pdf_without_headers_footers(full_pdf_path, output_pdf_path, header_height, footer_height, left_margin, right_margin, dpi, progress_callback)
    elif os.path.isfile(pdf_path) and pdf_path.lower().endswith('.pdf'):
        # 如果是单个 PDF 文件，直接处理
        output_pdf_path = os.path.join(output_folder, os.path.basename(pdf_path))
        extract_and_save_pdf_without_headers_footers(pdf_path, output_pdf_path, header_height, footer_height, left_margin, right_margin, dpi, progress_callback)


def load_pdf():
    global pdf_path
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if pdf_path:
        display_pdf_page(0)

def display_pdf_page(page_num):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk
    doc.close()


def crop_and_save():
    try:
        # 禁用按钮以防止重复点击
        crop_button.config(state="disabled")
        
        # 获取用户输入的裁剪参数，单位为毫米，转换为点数（1毫米=2.835点）
        header_height = float(header_entry.get()) * 28.35
        footer_height = float(footer_entry.get()) * 28.35
        left_margin = float(left_entry.get()) * 28.35
        right_margin = float(right_entry.get()) * 28.35
        
        # 设置临时输出文件路径
        temp_pdf_name = "temp_cropped_output.pdf"
        progress_bar["value"] = 0
        doc = fitz.open(pdf_path)
        progress_bar["maximum"] = len(doc)

        def update_progress(current, total):
            progress_bar["value"] = (current / total) * 100
            root.update_idletasks()

        temp_pdf_path = os.path.join(os.path.dirname(pdf_path), temp_pdf_name)
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

        # 调用提取并保存函数，裁剪并保存到临时文件
        extract_and_save_pdf_without_headers_footers(pdf_path, temp_pdf_path, header_height, footer_height, left_margin, right_margin, progress_callback=update_progress)
        
        # 替换原 PDF 文件
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        os.rename(temp_pdf_path, pdf_path)
        
        messagebox.showinfo("Success", f"PDF saved as: {pdf_path}")
        progress_bar.grid_forget()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for the crop distances.")
    except PermissionError:
        messagebox.showerror("Error", "Permission denied. Please check if the file is in use or if you have the necessary permissions.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    finally:
        # 在处理完毕后重新启用按钮
        crop_button.config(state="normal")


# 调用 main 函数启动应用程序
if __name__ == "__main__":
    main()
