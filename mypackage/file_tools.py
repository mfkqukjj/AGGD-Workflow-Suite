import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import time

class FileExplorerDialog(tk.Toplevel):
    """文件遍历工具"""
    def __init__(self, master):
        super().__init__(master)
        self.title("文件遍历")
        self.geometry("800x600")
        self.grab_set()
        self.dir_path = tk.StringVar()
        self.include_subdir = tk.BooleanVar(value=True)
        self.pattern = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # 选择文件夹
        dirfrm = ttk.Frame(frm)
        dirfrm.pack(fill=tk.X, pady=5)
        ttk.Label(dirfrm, text="选择文件夹：").pack(side=tk.LEFT)
        ttk.Entry(dirfrm, textvariable=self.dir_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(dirfrm, text="浏览", command=self.select_dir).pack(side=tk.LEFT)

        # 选项
        optfrm = ttk.Frame(frm)
        optfrm.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(optfrm, text="包含子目录", variable=self.include_subdir).pack(side=tk.LEFT)
        ttk.Label(optfrm, text="正则匹配(文件名)：").pack(side=tk.LEFT, padx=10)
        ttk.Entry(optfrm, textvariable=self.pattern, width=30).pack(side=tk.LEFT)

        # 按钮区
        btnfrm = ttk.Frame(frm)
        btnfrm.pack(fill=tk.X, pady=5)
        ttk.Button(btnfrm, text="开始遍历", command=self.start_explore).pack(side=tk.LEFT, padx=5)
        ttk.Button(btnfrm, text="一键复制", command=self.copy_menu).pack(side=tk.LEFT, padx=5)

        # 文件树
        treefrm = ttk.Frame(frm)
        treefrm.pack(fill=tk.BOTH, expand=True)
        columns = ("类型", "大小", "创建时间", "修改时间")
        self.tree = ttk.Treeview(treefrm, columns=columns, show="tree headings")
        self.tree.heading("#0", text="名称")
        self.tree.column("#0", width=250, anchor="w")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def select_dir(self):
        dirname = filedialog.askdirectory(title="选择文件夹")
        if dirname:
            self.dir_path.set(dirname)

    def start_explore(self):
        path = self.dir_path.get()
        if not path or not os.path.isdir(path):
            messagebox.showerror("错误", "请选择有效的文件夹")
            return
        pattern = self.pattern.get()
        regex = None
        if pattern:
            try:
                regex = re.compile(pattern)
            except re.error as e:
                messagebox.showerror("正则错误", f"正则表达式无效：{e}")
                return
        self.tree.delete(*self.tree.get_children())
        self.insert_tree("", path, regex, self.include_subdir.get())

    def insert_tree(self, parent, path, regex, recursive):
        try:
            entries = os.listdir(path)
        except Exception:
            return
        dirs = []
        files = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            elif os.path.isfile(full_path):
                if not regex or regex.search(entry):
                    files.append(entry)
        dirs.sort()
        files.sort()
        # 文件夹优先
        for entry in dirs:
            full_path = os.path.join(path, entry)
            stat = os.stat(full_path)
            node = self.tree.insert(parent, "end", text=entry, values=(
                "文件夹", "", 
                time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_ctime)),
                time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
            ))
            if recursive:
                self.insert_tree(node, full_path, regex, recursive)
        for entry in files:
            full_path = os.path.join(path, entry)
            stat = os.stat(full_path)
            size = stat.st_size
            ext = os.path.splitext(entry)[1][1:]
            self.tree.insert(parent, "end", text=entry, values=(
                ext or "文件", f"{size:,}", 
                time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_ctime)),
                time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
            ))

    def copy_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="复制所有文件名", command=self.copy_all_filenames)
        menu.add_command(label="复制全部结构", command=self.copy_tree_structure)
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def copy_all_filenames(self):
        names = []
        def collect_names(item):
            for child in self.tree.get_children(item):
                text = self.tree.item(child, "text")
                values = self.tree.item(child, "values")
                if values and values[0] != "文件夹":
                    names.append(text)
                collect_names(child)
        collect_names("")
        if names:
            self.clipboard_clear()
            self.clipboard_append("\n".join(names))
            messagebox.showinfo("复制成功", f"已复制{len(names)}个文件名")
        else:
            messagebox.showinfo("提示", "没有可复制的文件名")

    def copy_tree_structure(self):
        lines = []
        def walk(item, prefix=""):
            for child in self.tree.get_children(item):
                text = self.tree.item(child, "text")
                values = self.tree.item(child, "values")
                lines.append(f"{prefix}{text}")
                walk(child, prefix + "    ")
        walk("")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            messagebox.showinfo("复制成功", "已复制全部结构")
        else:
            messagebox.showinfo("提示", "没有可复制的内容")

class BatchRenameDialog(tk.Toplevel):
    """批量重命名工具"""
    def __init__(self, master):
        super().__init__(master)
        self.title("批量重命名")
        self.geometry("700x600")
        self.grab_set()
        self.dir_path = tk.StringVar()
        self.ignore_ext = tk.BooleanVar(value=True)
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # 选择文件夹
        dirfrm = ttk.Frame(frm)
        dirfrm.pack(fill=tk.X, pady=5)
        ttk.Label(dirfrm, text="选择文件夹：").pack(side=tk.LEFT)
        ttk.Entry(dirfrm, textvariable=self.dir_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(dirfrm, text="浏览", command=self.select_dir).pack(side=tk.LEFT)

        # 文件列表显示
        ttk.Label(frm, text="当前文件夹下文件：").pack(anchor="w", pady=(5,0))
        self.file_listbox = tk.Listbox(frm, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=False, pady=2)

        # 粘贴区和一键提取
        txtfrm = ttk.Frame(frm)
        txtfrm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(txtfrm, text="粘贴重命名对照表（原名 新名，每行一组，空格或Tab分隔）：").pack(anchor="w", pady=(10,0))
        self.txt_map = tk.Text(txtfrm, height=10)
        self.txt_map.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Button(txtfrm, text="一键提取", command=self.extract_filenames).pack(anchor="e", pady=2)

        # 选项
        ttk.Checkbutton(frm, text="忽略后缀名", variable=self.ignore_ext).pack(anchor="w", pady=5)

        # 按钮
        ttk.Button(frm, text="开始批量重命名", command=self.start_rename).pack(pady=8)

    def select_dir(self):
        dirname = filedialog.askdirectory(title="选择文件夹")
        if dirname:
            self.dir_path.set(dirname)
            self.update_file_list()

    def update_file_list(self):
        folder = self.dir_path.get()
        self.file_listbox.delete(0, tk.END)
        if folder and os.path.isdir(folder):
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            for f in files:
                self.file_listbox.insert(tk.END, f)

    def extract_filenames(self):
        folder = self.dir_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("错误", "请选择有效的文件夹")
            return
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            messagebox.showinfo("提示", "该文件夹下没有文件")
            return
        self.txt_map.delete("1.0", tk.END)
        for f in files:
            self.txt_map.insert(tk.END, f + "\n")

    def start_rename(self):
        folder = self.dir_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("错误", "请选择有效的文件夹")
            return
        lines = self.txt_map.get("1.0", tk.END).strip().splitlines()
        mapping = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 2:
                parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            mapping.append((parts[0], parts[1]))
        if not mapping:
            messagebox.showerror("错误", "请粘贴有效的重命名对照表")
            return
        ignore_ext = self.ignore_ext.get()
        files = os.listdir(folder)
        rename_count = 0
        for old, new in mapping:
            for fname in files:
                name, ext = os.path.splitext(fname)
                if (ignore_ext and name == old) or (not ignore_ext and fname == old):
                    new_name = new + ext if ignore_ext else new
                    src = os.path.join(folder, fname)
                    dst = os.path.join(folder, new_name)
                    try:
                        os.rename(src, dst)
                        rename_count += 1
                    except Exception as e:
                        messagebox.showwarning("警告", f"{fname} 重命名失败: {e}")
        self.update_file_list()
        messagebox.showinfo("完成", f"成功重命名 {rename_count} 个文件。")