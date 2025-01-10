import fitz  # PyMuPDF
from tkinter import Tk, Label, Entry, Button, Canvas, filedialog, messagebox, ttk
import os
import fitz
import traceback
import time


def extract_and_save_pdf_without_headers_footers(pdf_path, output_pdf_path, header_height=50, footer_height=50, left_margin=0, right_margin=0, progress_callback=None):
    """
    提取 PDF 的正文内容，去掉页眉、页脚，并将裁剪后的内容保存为新的 PDF，同时支持裁剪左边和右边。
    """
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()  # 创建一个新的空 PDF

    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        page_rect = page.rect  # 获取页面的尺寸
        
        # 设置裁剪区域（去除页眉、页脚以及左右边距）
        crop_rect = fitz.Rect(
            page_rect.x0 + left_margin, 
            page_rect.y0 + header_height,
            page_rect.x1 - right_margin, 
            page_rect.y1 - footer_height
        )
        
        # 设置裁剪框
        page.set_cropbox(crop_rect)

        # 将裁剪后的页面内容添加到新 PDF
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # 更新进度条
        if progress_callback:
            progress_callback(page_num + 1, total_pages)

    # 保存裁剪后的 PDF 文件，并启用压缩
    new_doc.save(output_pdf_path, deflate=True)
    new_doc.close()
    doc.close()

    # 添加延时，确保文件被完全释放
    time.sleep(15)

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

        # 调用提取并保存函数，裁剪并保存到临时文件
        extract_and_save_pdf_without_headers_footers(pdf_path, temp_pdf_path, header_height, footer_height, left_margin, right_margin, progress_callback=update_progress)
        
        # 替换原 PDF 文件
        if os.path.exists(pdf_path) and os.path.exists(temp_pdf_path):
            os.remove(pdf_path)
            os.rename(temp_pdf_path, pdf_path)
        
        
        messagebox.showinfo("Success", f"PDF saved as: {pdf_path}")
        progress_bar.grid_forget()

        # 延时1秒后自动关闭窗口
        root.after(1000, root.quit)  # 1000毫秒 = 1秒
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for the crop distances.")
    except PermissionError:
        messagebox.showerror("Error", "Permission denied. Please check if the file is in use or if you have the necessary permissions.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        # 打印堆栈信息到终端
        print("Error details:")
        traceback.print_exc()
    finally:
        # 在处理完毕后重新启用按钮
        crop_button.config(state="normal")

def main():
    # 初始化 Tkinter 界面
    global root, pdf_path, header_entry, footer_entry, left_entry, right_entry, progress_bar, canvas, crop_button
    
    root = Tk()
    root.title("PDF Crop Tool")

    # 创建 UI 元素
    Label(root, text="Header Height (cm):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    header_entry = Entry(root)
    header_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(root, text="Footer Height (cm):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    footer_entry = Entry(root)
    footer_entry.grid(row=1, column=1, padx=5, pady=5)

    Label(root, text="Left Margin (cm):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    left_entry = Entry(root)
    left_entry.grid(row=2, column=1, padx=5, pady=5)

    Label(root, text="Right Margin (cm):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    right_entry = Entry(root)
    right_entry.grid(row=3, column=1, padx=5, pady=5)

    Button(root, text="Load PDF", command=load_pdf).grid(row=4, column=0, padx=5, pady=5)
    
    # 给按钮命名，并配置
    crop_button = Button(root, text="Crop and Save PDF", command=crop_and_save)
    crop_button.grid(row=4, column=1, padx=5, pady=5)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    canvas = Canvas(root, width=600, height=800)
    canvas.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    # 启动主循环
    root.mainloop()