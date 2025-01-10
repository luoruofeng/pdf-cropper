import fitz  # PyMuPDF
from tkinter import Tk, Label, Entry, Button, Canvas, filedialog, messagebox, ttk
from PIL import Image, ImageTk

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
        header_height = float(header_entry.get()) * 28.35
        footer_height = float(footer_entry.get()) * 28.35
        left_margin = float(left_entry.get()) * 28.35
        right_margin = float(right_entry.get()) * 28.35
        
        output_pdf_path = "cropped_output.pdf"
        progress_bar["value"] = 0
        progress_bar["maximum"] = len(fitz.open(pdf_path))

        def update_progress(current, total):
            progress_bar["value"] = (current / total) * 100
            root.update_idletasks()

        extract_and_save_pdf_without_headers_footers(pdf_path, output_pdf_path, header_height, footer_height, left_margin, right_margin, progress_callback=update_progress)
        
        messagebox.showinfo("Success", f"PDF saved as: {output_pdf_path}")
        progress_bar.grid_forget()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for the crop distances.")

def main():
    # 初始化 Tkinter 界面
    global root, pdf_path, header_entry, footer_entry, left_entry, right_entry, progress_bar, canvas
    
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
    Button(root, text="Crop and Save PDF", command=crop_and_save).grid(row=4, column=1, padx=5, pady=5)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    canvas = Canvas(root, width=600, height=800)
    canvas.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    # 启动主循环
    root.mainloop()

# 调用 main 函数启动应用程序
if __name__ == "__main__":
    main()
