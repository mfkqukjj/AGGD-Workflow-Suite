import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from pathlib import Path
import numpy as np
from typing import List, Dict, Union
import threading
import subprocess

class FundFlowAnalysis:
    def __init__(self, master):
        self.master = master
        # 将window定义为类属性，方便其他方法调用
        self.window = None
        self.files_selected = []
        self.df = None
        self.required_columns = [
            '查询账号', '付款方支付帐号', '收款方支付帐号', '支付机构内部订单号',
            '交易时间', '借贷标志', '交易金额', '交易余额', '付款方银行卡号',
            '收款方银行卡号', '交易类型', '收款方的商户名称', '备注'
        ]
        
        self.create_main_window()

    def create_main_window(self):
        """创建主窗口"""
        self.window = tk.Toplevel(self.master)
        self.window.title("资金流向分析")
        self.window.geometry("800x600")
        # 设置窗口始终置顶
        self.window.transient(self.master)
        self.window.grab_set()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择区域
        self.file_frame = ttk.LabelFrame(self.main_frame, text="数据导入", padding="10")
        self.file_frame.pack(fill=tk.X, pady=5)
        
        # 按钮
        ttk.Button(self.file_frame, text="选择文件", command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.file_frame, text="选择文件夹", command=self.select_folders).pack(side=tk.LEFT, padx=5)
        
        # 文件列表
        self.file_list = tk.Listbox(self.main_frame, height=10)
        self.file_list.pack(fill=tk.X, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)
        
        # 状态标签
        self.status_label = ttk.Label(self.main_frame, text="等待导入数据...")
        self.status_label.pack(pady=5)
        
        # 开始分析按钮
        self.analyze_btn = ttk.Button(self.main_frame, text="开始分析", command=self.start_analysis)
        self.analyze_btn.pack(pady=10)

        # 添加自动保存选项
        self.auto_save_var = tk.BooleanVar(value=True)
        self.auto_save_check = ttk.Checkbutton(
            self.main_frame, 
            text="自动保存至源文件目录", 
            variable=self.auto_save_var
        )
        self.auto_save_check.pack(pady=5)

    def select_files(self):
        """选择多个文件"""
        self.window.withdraw()  # 临时隐藏主窗口
        files = filedialog.askopenfilenames(
            title="选择数据文件",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        self.window.deiconify()  # 重新显示主窗口
        self.window.lift()  # 将窗口提到最前
        self.window.focus_force()  # 强制获取焦点
        self.add_files(files)

    def select_folders(self):
        """选择多个文件夹"""
        self.window.withdraw()  # 临时隐藏主窗口
        folder = filedialog.askdirectory(title="选择数据文件夹")
        self.window.deiconify()  # 重新显示主窗口
        self.window.lift()  # 将窗口提到最前
        self.window.focus_force()  # 强制获取焦点
        if folder:
            for ext in ['*.xlsx', '*.xls', '*.csv', '*.txt']:
                self.add_files(Path(folder).glob(ext))

    def add_files(self, files):
        """添加文件到列表"""
        for file in files:
            if str(file) not in self.files_selected:
                self.files_selected.append(str(file))
                self.file_list.insert(tk.END, os.path.basename(str(file)))

    def read_data(self, file_path: str) -> pd.DataFrame:
        """读取数据文件"""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif ext == '.csv':
                return pd.read_csv(file_path)
            elif ext == '.txt':
                return pd.read_csv(file_path, sep='\t')
        except Exception as e:
            messagebox.showerror("错误", f"读取文件 {file_path} 时出错：{str(e)}")
            return None

    def show_mapping_dialog(self, columns: List[str]) -> Dict[str, str]:
        """显示字段映射对话框"""
        mapping_dialog = tk.Toplevel(self.window)
        mapping_dialog.title("字段映射")
        mapping_dialog.geometry("600x600")
        # 设置模态对话框
        mapping_dialog.transient(self.window)
        mapping_dialog.grab_set()
        
        mapping = {}
        
        # 创建映射选择界面
        ttk.Label(mapping_dialog, text="请为必需字段选择对应的数据列：").pack(pady=10)
        
        mapping_frame = ttk.Frame(mapping_dialog)
        mapping_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # 自动匹配相同字段名
        auto_mapped = {col: col for col in self.required_columns if col in columns}
        remaining_columns = [col for col in columns if col not in auto_mapped.values()]
        
        for i, req_col in enumerate(self.required_columns):
            ttk.Label(mapping_frame, text=req_col).grid(row=i, column=0, pady=2)
            combo = ttk.Combobox(mapping_frame, values=[''] + remaining_columns)
            combo.grid(row=i, column=1, pady=2)
            
            # 如果有自动匹配的字段，设置并禁用下拉框
            if req_col in auto_mapped:
                combo.set(auto_mapped[req_col])
                combo.configure(state='disabled')
            
            mapping[req_col] = combo
        
        def confirm_mapping():
            result = {}
            for k, v in mapping.items():
                # 对于已禁用的下拉框（自动匹配的字段），直接使用其值
                if v['state'] == 'disabled':
                    result[k] = v.get()
                else:
                    selected = v.get()
                    if selected:  # 只添加非空的映射
                        result[k] = selected
            self.column_mapping = result
            mapping_dialog.destroy()
        
        ttk.Button(mapping_dialog, text="确认映射", command=confirm_mapping).pack(pady=10)
        
        # 等待窗口关闭
        self.window.wait_window(mapping_dialog)
        return self.column_mapping

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理数据（对应SQL模型的逻辑）"""
        # 重命名列
        if hasattr(self, 'column_mapping'):
            df = df.rename(columns={v: k for k, v in self.column_mapping.items() if v})
        
        # 1. 基础处理
        df['交易日期时间'] = pd.to_datetime(df['交易时间'].astype(str).str.pad(14, fillchar='0'), 
                                  format='%Y%m%d%H%M%S')
        df = df[df['备注'] != "付款失败"]
        
        # 2. 计算商户类型
        def get_account_type(name):
            """判断账户类型
            Args:
                name: 商户名称
            Returns:
                str: "个人"/"公司"/None
            """
            if pd.isna(name) or len(str(name)) == 1:
                return None
            
            name = str(name)
            
            # 1. 最高优先级: 直接标注的个人
            explicit_person = ['（个人）', '(个人)', '个体户']
            if any(tag in name for tag in explicit_person):
                return "个人"
            
            # 2. 公司类型关键词
            company_keywords = [
                '公司', '集团', '机构', '基金', '金服', '协会',
                '商贸', '银行', '证券', '保险', '投资',
                '企业', '工厂',  '中心',
                '商城', '超市', '市场', '学校', '医院',
                '酒店', '餐厅', '网络', '科技', '信息',
                '有限', '股份', '合伙'
            ]
            
            # 3. 个人名称特征
            person_features = [
    # 维吾尔族人名特征（约80个）
    '买买提', '阿不都', '艾力', '麦麦提', '热依木', '吾买尔', '艾合买提', '依布拉音',
    '阿布都', '阿迪力', '阿里木', '艾尔肯', '巴合提', '迪力夏提', '古力', '哈力克',
    '艾克拜尔', '吾斯曼', '依米提', '玉素甫', '阿不力克', '阿不都拉', '阿不都热合曼',
    '阿地力江', '阿合买提江', '阿克木', '艾克木', '艾力江', '艾买提', '艾沙江',
    '艾斯卡尔', '巴哈尔', '巴哈提亚尔', '达吾提', '代力拜尔', '蒂力瓦尔', '地里夏提',
    '东来提', '都拉提', '额勒斯', '额敏', '恩维尔', '喀德尔', '卡德尔', '卡斯木',
    '凯赛尔', '库尔班', '库热西', '马合木提', '买合木提', '买买提江', '买提', '米吉提',
    '努尔买买提', '努尔曼', '帕尔哈提', '热合曼', '热扎克', '赛迪克', '赛力克',
    '司马义', '苏来曼', '苏联', '铁木尔', '托合提', '托乎提', '托合塔尔', '托克逊',
    '外力', '维力', '乌买尔', '吾布力', '吾甫尔', '吾拉木', '西地克', '希尔艾力',
    '肖开提', '亚库普', '亚森', '依布拉依木', '依德利斯', '依力亚斯', '依斯拉木',
    '尤努斯', '玉山', '玉素甫江', '再努拉', '扎克尔', '珠马力',

    # 藏族人名特征（约70个）
    '次仁', '卓玛', '索朗', '格桑', '仁增', '旺堆', '平措', '白玛', '降央', '央金',
    '次旺', '普布', '拉巴', '白珍', '其美', '达瓦', '泽仁', '曲珍', '群培', '顿珠',
    '洛桑', '嘉央', '强巴', '才旺', '扎西', '江措', '德吉', '桑珠', '朗杰', '嘎玛',
    '更登', '旺姆', '加央', '曲木', '达珍', '南杰', '尼玛', '旺青', '斯朗', '白让',
    '丹增', '益西', '多吉', '旺金', '降措', '次基', '玉珍', '拉姆', '达甲', '昂旺',
    '贡嘎', '措姆', '其米', '次珍', '索娜', '达吉', '才让', '白旦', '才顿', '占堆',
    '央宗', '白德', '多布杰', '白玛措', '噶玛', '降措', '绒措', '桑布', '却吉', '索朗旺堆',

    # 蒙古族人名特征（约60个）
    '格日勒', '乌云', '呼和', '额尔德尼', '巴特尔', '苏和', '斯琴', '萨仁', '朝克图', '宝音',
    '那顺', '道尔吉', '巴雅尔', '阿拉坦', '赛音', '满都拉', '图门', '图雅', '额日德尼', '乌兰',
    '其其格', '齐日古嘎', '白音', '胡日查', '包银', '金巴图', '玛拉沁', '达来', '特木尔', '金花',
    '锡林', '珠拉', '敖特根', '毕力格', '宝力高', '宝音吉雅', '布仁', '楚古拉', '达古拉', '达赖',
    '额尔敦', '额日图', '格根', '根登', '和日勒', '贺希格', '吉尔格勒', '吉日嘎拉', '金格尔', '闵柱',
    '那日苏', '纳森', '青格勒', '青格尔泰', '青斯格', '萨日娜', '色音', '苏布达', '苏和巴特尔', '苏勒',

    # 回族人名特征（约50个）
    '马哈木提', '穆罕默德', '阿訇', '艾买提', '麦麦提', '阿卜杜拉', '阿里', '哈桑', '侯赛因', '伊布拉欣',
    '叶海亚', '赛义德', '阿巴斯', '阿卜杜', '阿卜杜勒', '阿迪力', '阿訇', '艾山', '艾伟', '安外尔',
    '白有志', '拜勒', '本扬', '布尔汗', '察勒', '常志宁', '丁守中', '丁元庆', '丁志诚', '冯天保',
    '哈里勒', '哈米德', '海德尔', '胡赛尼', '胡有志', '霍志远', '贾福尔', '贾拉勒', '贾迈勒', '贾曼',
    '贾米勒', '卡德尔', '卡迪尔', '卡米力', '马合木', '马吉德', '马坚', '马建国', '马金山', '马俊',

    # 其他少数民族特征（约50个）
    '其其格', '阿依古丽', '玛依拉', '木合塔尔', '吐尔逊', '阿布都克热木', '卡米拉', '帕提曼',
    '阿依努尔', '古丽娜尔', '米热古丽', '古力班', '热依汗', '热西旦', '赛乃姆', '沙代提',
    '阿地力江', '吐尔洪', '阿布来提', '阿布都沙拉木', '玛依努尔', '木尔扎提', '努尔买买提',
    '热合曼', '吐尔逊江', '阿卜杜拉曼', '阿布都热依木', '阿卜杜热合曼', '玛依努尔', '木尔扎提',
    '努尔买买提', '热合曼', '吐尔逊江', '阿卜杜拉曼', '阿布都热依木', '阿卜杜热合曼', '阿布都外力',
    '阿布都瓦依提', '阿布都热合曼', '艾力', '艾尼瓦尔', '艾斯卡尔', '安尼瓦尔', '巴合提亚尔',
    '巴吾东', '达吾提', '迪力夏提', '东来提', '额勒斯', '恩维尔', '古力班', '哈力克'
]
            
            # 判断逻辑:
            # 1. 如果包含公司关键词且长度>10，判定为公司
            if any(keyword in name for keyword in company_keywords) and len(name) > 10:
                return "公司"
            
            # 2. 如果包含个人名称特征且长度<=10，判定为个人
            if any(feature in name for feature in person_features) and len(name) <= 10:
                return "个人"
            
            # 3. 仅从长度考虑
            if len(name) > 10:
                return "公司"
            elif 2 <= len(name) <= 4:  # 普通中文姓名一般2-4个字
                return "个人"
            
            # 其他情况返回None
            return None

        # 3. 按交易对手分组统计
        def calculate_group_stats(group):
            total_count = len(group)
            credit_records = group[group['借贷标志'] == '贷']
            debit_records = group[group['借贷标志'] == '借']
            
            flow_type = "有进有出"
            if total_count == len(credit_records):
                flow_type = "只进不出"
            elif total_count == len(debit_records):
                flow_type = "只出不进"
                
            # 按时间倒序排序后生成交易详情
            sorted_group = group.sort_values('交易日期时间', ascending=False)
            transaction_details = '; '.join(sorted_group.apply(
                lambda x: f"{x['交易日期时间'].strftime('%Y-%m-%d %H:%M')} ({'+' if x['借贷标志']=='贷' else '-'}{x['交易金额']})",
                axis=1
            ))
            
            return pd.Series({
                '系统姓名': group['收款方的商户名称'].iloc[0],
                '交易笔数': total_count,
                '收入笔数': len(credit_records),
                '支出笔数': len(debit_records),
                '进出类型': flow_type,
                '流水总额': group['交易金额'].sum(),
                '净流入金额': credit_records['交易金额'].sum() - debit_records['交易金额'].sum(),
                '最早交易时间': group['交易日期时间'].min(),
                '最新交易时间': group['交易日期时间'].max(),
                '交易天数跨度': (group['交易日期时间'].max() - group['交易日期时间'].min()).days,
                '收入金额': credit_records['交易金额'].sum(),
                '支出金额': debit_records['交易金额'].sum(),
                '平均单笔收入金额': credit_records['交易金额'].mean() if len(credit_records) > 0 else 0,
                '平均单笔支出金额': debit_records['交易金额'].mean() if len(debit_records) > 0 else 0,
                '最大单笔收入金额': credit_records['交易金额'].max() if len(credit_records) > 0 else 0,
                '最大单笔支出金额': debit_records['交易金额'].max() if len(debit_records) > 0 else 0,
                '交易备注': '; '.join(group['备注'].dropna().unique()),
                '关联交易详情': transaction_details
            })

        # 4. 生成最终结果
        result = df.groupby(['付款方支付帐号', '收款方支付帐号']).apply(calculate_group_stats).reset_index()
        result.columns = [
            '用户id', '交易对手', '系统姓名', '交易笔数', '收入笔数', '支出笔数',
            '进出类型', '流水总额', '净流入金额', '最早交易时间', '最新交易时间',
            '交易天数跨度', '收入金额', '支出金额', '平均单笔收入金额',
            '平均单笔支出金额', '最大单笔收入金额', '最大单笔支出金额',
            '交易备注', '关联交易详情'
        ]
        
        # 5. 添加其他字段
        result['对手账户类型'] = result['系统姓名'].apply(get_account_type)
        result['微信号'] = None  # 需要从原表恢复微信号表中获取
        result['对手微信号'] = None
        result['对手系统姓名'] = None
        
        # 6. 调整列顺序
        final_columns = [
            '用户id', '微信号', '系统姓名', '交易对手', '对手微信号', 
            '对手账户类型', '对手系统姓名', '交易笔数', '收入笔数', '支出笔数',
            '进出类型', '流水总额', '净流入金额', '最早交易时间', '最新交易时间',
            '交易天数跨度', '收入金额', '支出金额', '平均单笔收入金额',
            '平均单笔支出金额', '最大单笔收入金额', '最大单笔支出金额',
            '交易备注', '关联交易详情'
        ]
        
        return result[final_columns]

    def open_file_location(self, file_path):
        """打开文件所在目录并选中文件"""
        try:
            # 规范化路径
            normalized_path = os.path.normpath(file_path)
            # 使用 os.path.dirname 获取目录路径
            dir_path = os.path.dirname(normalized_path)
            
            if os.path.exists(normalized_path):
                # 方法1：使用 explorer 选中文件
                os.system(f'explorer /select,"{normalized_path}"')
            else:
                # 如果文件不存在，至少打开目录
                os.startfile(dir_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录：{str(e)}")

    def start_analysis(self):
        """开始分析流程"""
        if not self.files_selected:
            messagebox.showwarning("警告", "请先选择数据文件！")
            return
        
        def analysis_thread():
            try:
                # 读取所有文件
                total_files = len(self.files_selected)
                all_data = []
                
                for i, file in enumerate(self.files_selected):
                    self.status_label.config(text=f"正在读取文件: {os.path.basename(file)}...")
                    df = self.read_data(file)
                    
                    if df is not None:
                        # 首次读取时进行字段映射
                        if not hasattr(self, 'column_mapping'):
                            self.column_mapping = self.show_mapping_dialog(df.columns.tolist())
                        
                        all_data.append(df)
                    
                    self.progress_var.set((i + 1) / total_files * 50)
                
                # 合并数据
                self.status_label.config(text="正在合并数据...")
                combined_df = pd.concat(all_data, ignore_index=True)
                
                # 处理数据
                self.status_label.config(text="正在处理数据...")
                result_df = self.process_data(combined_df)
                
                self.progress_var.set(100)
                self.status_label.config(text="分析完成！")
                
                # 保存结果
                if self.auto_save_var.get():
                    source_dir = os.path.dirname(self.files_selected[0])
                    timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H%M')
                    output_file = os.path.join(source_dir, f"【结果表】资金分析反馈{timestamp}.xlsx")
                    result_df.to_excel(output_file, index=False)
                    
                    result = messagebox.askquestion("成功", 
                        f"结果已保存至:\n{output_file}\n\n是否打开输出目录？")
                    if result == 'yes':
                        self.window.after(100, lambda: self.open_file_location(output_file))
                else:
                    output_file = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        filetypes=[("Excel files", "*.xlsx")],
                        initialfile=f"【结果表】资金分析反馈{pd.Timestamp.now().strftime('%Y-%m-%d %H%M')}.xlsx"
                    )
                    if output_file:
                        result_df.to_excel(output_file, index=False)
                        result = messagebox.askquestion("成功", 
                            f"结果已保存至:\n{output_file}\n\n是否打开输出目录？")
                        if result == 'yes':
                            self.window.after(100, lambda: self.open_file_location(output_file))
            
            except Exception as e:
                messagebox.showerror("错误", f"处理过程中出错：{str(e)}")
                
        # 在新线程中运行分析
        threading.Thread(target=analysis_thread, daemon=True).start()