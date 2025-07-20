import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import os

class AboutViewer(tk.Toplevel):
    """关于页面查看器 - 优化Markdown渲染版本"""
    def __init__(self, master):
        super().__init__(master)
        self.title("关于我们")
        self.geometry("800x600")
        
        # 保持窗口始终在最前
        self.transient(master)
        self.grab_set()
        
        # 创建主容器和滚动条
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本显示区域
        self.create_text_widget()
        
        # 加载README文件
        self.load_readme()

    def create_text_widget(self):
        """创建文本显示区域"""
        # 创建带滚动条的文本框
        self.text_widget = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            font=('微软雅黑', 10),
            padx=20,
            pady=10
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 配置样式
        self.styles = {
            'h1': {'font': ('微软雅黑', 20, 'bold'), 'spacing1': 15, 'spacing3': 15, 'justify': 'center'},
            'h2': {'font': ('微软雅黑', 16, 'bold'), 'spacing1': 12, 'spacing3': 8},
            'h3': {'font': ('微软雅黑', 14, 'bold'), 'spacing1': 10, 'spacing3': 6},
            'h4': {'font': ('微软雅黑', 12, 'bold'), 'spacing1': 8, 'spacing3': 4},
            'quote': {'font': ('微软雅黑', 10, 'italic'), 'background': '#f0f0f0', 
                     'lmargin1': 20, 'lmargin2': 20, 'spacing1': 10, 'spacing3': 10},
            'code': {'font': ('Consolas', 10), 'background': '#f6f8fa', 
                    'lmargin1': 20, 'lmargin2': 20},
            'list': {'lmargin1': 20, 'lmargin2': 40},
            'bold': {'font': ('微软雅黑', 10, 'bold')},
            'italic': {'font': ('微软雅黑', 10, 'italic')},
            'divider': {'foreground': '#cccccc'}
        }
        
        for tag, style in self.styles.items():
            self.text_widget.tag_configure(tag, **style)

    def load_readme(self):
        """加载并显示README.md文件"""
        try:
            readme_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'README-about.md'
            )
            if not os.path.exists(readme_path):
                raise FileNotFoundError("未找到README-about.md文件")
                
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.render_markdown(content)
            self.text_widget.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败：{str(e)}")
            self.destroy()
    
    def render_markdown(self, content):
        """高效稳定的Markdown渲染引擎"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
        # 预处理：合并连续列表项
        content = self.preprocess_lists(content)
        lines = content.split('\n')
        in_list = False  # 跟踪是否在列表中
        
        for i, line in enumerate(lines):
            # 跳过空行（除非在列表中需要保持缩进）
            if not line.strip() and not in_list:
                self.text_widget.insert(tk.END, '\n')
                continue
                
            # 处理标题
            if re.match(r'^#\s+', line):  # H1
                self.insert_heading(line[2:].strip(), 'h1')
            elif re.match(r'^##\s+', line):  # H2
                self.insert_heading(line[3:].strip(), 'h2')
            elif re.match(r'^###\s+', line):  # H3
                self.insert_heading(line[4:].strip(), 'h3')
            elif re.match(r'^####\s+', line):  # H4
                self.insert_heading(line[5:].strip(), 'h4')
                
            # 处理列表项
            elif re.match(r'^[\*\-]\s+', line) or re.match(r'^\d+\.\s+', line):
                # 如果是列表的第一个项，添加空行分隔
                if not in_list:
                    self.text_widget.insert(tk.END, '\n')
                    in_list = True
                    
                # 获取列表符号和内容
                if re.match(r'^\d+\.\s+', line):
                    # 有序列表
                    match = re.match(r'^(\d+\.)\s+(.*)', line)
                    marker = match.group(1) + " "
                    text = match.group(2)
                else:
                    # 无序列表
                    match = re.match(r'^([\*\-])\s+(.*)', line)
                    marker = "• "
                    text = match.group(2)
                
                self.text_widget.insert(tk.END, marker, 'list')
                self.render_inline_styles(text, 'list')
                self.text_widget.insert(tk.END, '\n')
                
            # 列表结束处理
            elif in_list and line.strip() == '':
                in_list = False
                self.text_widget.insert(tk.END, '\n')
                
            # 处理引用块
            elif re.match(r'^>\s+', line):
                self.text_widget.insert(tk.END, line[2:].strip() + '\n', 'quote')
                
            # 处理分隔线
            elif re.match(r'^[-*_]{3,}$', line.strip()):
                self.text_widget.insert(tk.END, '─' * 80 + '\n\n', 'divider')
                
            # 处理普通段落
            else:
                # 如果不是列表中的第一行，添加段落分隔
                if not in_list and i > 0 and lines[i-1].strip() != '':
                    self.text_widget.insert(tk.END, '\n')
                self.render_inline_styles(line)
                self.text_widget.insert(tk.END, '\n')

    def preprocess_lists(self, content):
        """预处理列表项，解决连续列表项间的空行问题"""
        # 合并连续的列表项
        lines = content.split('\n')
        processed = []
        in_list = False
        
        for line in lines:
            # 检测列表项开始
            is_list_item = re.match(r'^(\s*)([\*\-]|\d+\.)\s+', line.strip())
            
            if is_list_item:
                if not in_list and processed and processed[-1] != '':
                    # 在列表前添加空行
                    processed.append('')
                in_list = True
                processed.append(line)
            elif line.strip() == '':
                # 空行保留，但不在列表中的空行减少为一个
                if in_list:
                    # 列表中的空行保留
                    processed.append(line)
                elif not processed or processed[-1] != '':
                    # 非列表中的连续空行只保留一个
                    processed.append('')
            else:
                # 非列表内容
                if in_list:
                    # 列表结束，添加空行分隔
                    processed.append('')
                    in_list = False
                processed.append(line)
                
        return '\n'.join(processed)
    
    def insert_heading(self, text, tag):
        """插入标题"""
        self.text_widget.insert(tk.END, text + '\n', tag)
        self.text_widget.insert(tk.END, '\n')  # 标题后空行
    
    def render_inline_styles(self, line, base_tag=None):
        """渲染行内样式：加粗(**text**)和斜体(*text*)"""
        if not line.strip():
            return
            
        # 处理加粗文本 (**text**)
        parts = re.split(r'(\*\*)', line)
        bold_active = False
        text_buffer = ""
        tag_stack = []
        
        for part in parts:
            if part == "**":
                # 切换加粗状态
                if base_tag:
                    current_tag = base_tag + '_bold' if not bold_active else base_tag
                else:
                    current_tag = 'bold' if not bold_active else ''
                
                # 应用当前文本样式
                if text_buffer:
                    self.text_widget.insert(tk.END, text_buffer, ' '.join(tag_stack))
                    text_buffer = ""
                
                bold_active = not bold_active
                # 更新标签栈
                if bold_active:
                    tag_stack.append('bold')
                else:
                    if 'bold' in tag_stack:
                        tag_stack.remove('bold')
            elif part == "*":
                # 斜体处理 - 简化处理
                text_buffer += part
            else:
                text_buffer += part
                
        # 插入剩余文本
        if text_buffer:
            self.text_widget.insert(tk.END, text_buffer, ' '.join(tag_stack))
    
    # 备选方案：使用嵌套正则表达式处理内联样式（更准确但稍复杂）
    def render_inline_styles_alternative(self, line, base_tag=None):
        """备选方案：使用正则表达式处理内联样式"""
        # 处理加粗 (**text**)
        line = re.sub(r'\*\*(.+?)\*\*', r'{\1}', line)
        # 处理斜体 (*text*)
        line = re.sub(r'\*(.+?)\*', r'[\1]', line)
        
        # 分割处理后的文本
        parts = re.split(r'([{}[\]])', line)
        
        bold_active = False
        italic_active = False
        tags = []
        text_buffer = ""
        
        for part in parts:
            if part == '{':
                # 开始加粗
                if text_buffer:
                    self.apply_tags(text_buffer, tags, base_tag)
                    text_buffer = ""
                bold_active = True
                tags.append('bold')
            elif part == '}':
                # 结束加粗
                if text_buffer:
                    self.apply_tags(text_buffer, tags, base_tag)
                    text_buffer = ""
                bold_active = False
                if 'bold' in tags:
                    tags.remove('bold')
            elif part == '[':
                # 开始斜体
                if text_buffer:
                    self.apply_tags(text_buffer, tags, base_tag)
                    text_buffer = ""
                italic_active = True
                tags.append('italic')
            elif part == ']':
                # 结束斜体
                if text_buffer:
                    self.apply_tags(text_buffer, tags, base_tag)
                    text_buffer = ""
                italic_active = False
                if 'italic' in tags:
                    tags.remove('italic')
            else:
                text_buffer += part
                
        # 处理剩余文本
        if text_buffer:
            self.apply_tags(text_buffer, tags, base_tag)
    
    def apply_tags(self, text, tags, base_tag=None):
        """应用标签组合"""
        if not text:
            return
            
        all_tags = []
        if base_tag:
            all_tags.append(base_tag)
        all_tags.extend(tags)
        
        self.text_widget.insert(tk.END, text, ' '.join(all_tags) if all_tags else '')

# 使用示例
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    def show_about():
        about = AboutViewer(root)
        root.wait_window(about)
    
    btn = tk.Button(root, text="关于我们", command=show_about)
    btn.pack(padx=50, pady=50)
    root.mainloop()