import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import os
def main():
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
