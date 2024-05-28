import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from threading import Thread

# 函数：执行文件操作
def perform_operation():
    source_folder = source_entry.get()
    destination_folder = destination_entry.get()
    operation = operation_choice.get()
    recursive = recursive_var.get()
    move_images_only = move_images_only_var.get()
    keep_structure = keep_structure_var.get()

    if not os.path.exists(source_folder) or not os.path.exists(destination_folder):
        messagebox.showerror("错误", "请选择有效的源文件夹和目标文件夹")
        return

    confirmation = messagebox.askokcancel("确认操作", f"确定要{operation}文件吗？")
    if not confirmation:
        return

    file_list = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            source_file = os.path.join(root, file)
            relative_path = os.path.relpath(source_file, source_folder)
            if keep_structure:
                destination_file = os.path.join(destination_folder, relative_path)
            else:
                destination_file = os.path.join(destination_folder, file)
            if not move_images_only or (move_images_only and is_image_file(source_file)):
                file_list.append((source_file, destination_file))

    operation_thread = Thread(target=move_or_copy, args=(file_list, operation, source_folder, destination_folder))
    operation_thread.start()

# 函数：移动或复制文件
def move_or_copy(file_list, operation, source_folder, destination_folder):
    total_files = len(file_list)
    progress_bar["maximum"] = total_files
    success_count = 0
    failed_files = []

    for source_file, destination_file in file_list:
        os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        try:
            if operation == "移动":
                shutil.move(source_file, destination_file)
            elif operation == "复制":
                shutil.copy2(source_file, destination_file)
            success_count += 1
        except Exception as e:
            failed_files.append((source_file, destination_file))
            print(f"操作失败：{str(e)}")
        finally:
            progress_bar["value"] = success_count
            root.update_idletasks()

    if failed_files:
        handle_failed_operations(failed_files, operation)

    messagebox.showinfo("成功", f"所有文件已成功{operation}到目标文件夹。")

# 函数：处理失败的文件操作
def handle_failed_operations(failed_files, operation):
    verify_dir = os.path.join(destination_folder.get(), "校验文件夹")
    os.makedirs(verify_dir, exist_ok=True)

    for source_file, destination_file in failed_files:
        rel_path = os.path.relpath(destination_file, destination_folder.get())
        verify_file_path = os.path.join(verify_dir, rel_path)
        os.makedirs(os.path.dirname(verify_file_path), exist_ok=True)
        try:
            if operation == "移动":
                shutil.move(source_file, verify_file_path)
            elif operation == "复制":
                shutil.copy2(source_file, verify_file_path)
            print(f"校验操作：文件 {source_file} 已被{operation}到 {verify_file_path}")
        except Exception as e:
            print(f"校验操作失败：{str(e)}")

# 函数：判断是否为图片文件
def is_image_file(file_path):
    image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"]
    file_extension = os.path.splitext(file_path)[1].lower()
    return file_extension in image_extensions

# 设置GUI界面
root = tk.Tk()
root.title("Photooo")
root.geometry("520x590")


# 设置页面边距
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(10, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(3, weight=1)

# 标题文字
title_label = tk.Label(root, text="Photooo", font=("Helvetica", 40))
title_label.grid(row=1, column=1, padx=20, pady=20, sticky="n")

# 源文件夹选择
source_label = tk.Label(root, text="选择源文件夹:")
source_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
source_entry = tk.Entry(root, width=40)
source_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
source_button = tk.Button(root, text="选择文件夹", command=lambda: [clear_source_folder(), source_entry.insert(0, filedialog.askdirectory())])
source_button.grid(row=3, column=2, padx=10, pady=5)

# 目标文件夹选择
destination_label = tk.Label(root, text="选择目标文件夹:")
destination_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")
destination_entry = tk.Entry(root, width=40)
destination_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
destination_button = tk.Button(root, text="选择文件夹", command=lambda: [clear_destination_folder(), destination_entry.insert(0, filedialog.askdirectory())])
destination_button.grid(row=5, column=2, padx=10, pady=5)

# 是否递归复制
recursive_var = tk.BooleanVar()
recursive_checkbutton = tk.Checkbutton(root, text="递归复制", variable=recursive_var)
recursive_checkbutton.grid(row=6, column=1, padx=10, pady=5, sticky="w")

# 是否仅移动图片文件
move_images_only_var = tk.BooleanVar()
move_images_only_checkbutton = tk.Checkbutton(root, text="仅移动图片文件", variable=move_images_only_var)
move_images_only_checkbutton.grid(row=7, column=1, padx=10, pady=5, sticky="w")

# 是否保留目录结构
keep_structure_var = tk.BooleanVar()
keep_structure_checkbutton = tk.Checkbutton(root, text="保留目录结构", variable=keep_structure_var)
keep_structure_checkbutton.grid(row=8, column=1, padx=10, pady=5, sticky="w")

# 操作选择
operation_label = tk.Label(root, text="选择操作:")
operation_label.grid(row=9, column=1, padx=10, pady=5, sticky="w")
operation_choice = ttk.Combobox(root, values=("移动", "复制"))
operation_choice.set("移动")
operation_choice.grid(row=10, column=1, padx=10, pady=5, sticky="w")

# 执行按钮
execute_button = tk.Button(root, text="开始执行", command=perform_operation)
execute_button.grid(row=11, column=1, columnspan=2, padx=10, pady=10)

# 进度条
progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.grid(row=12, column=1, columnspan=2, padx=10, pady=5)


# 主事件循环
root.mainloop()
