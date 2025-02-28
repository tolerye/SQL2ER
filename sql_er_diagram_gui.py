import re
import graphviz
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import math

class ERDiagramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL ER图生成器")
        self.root.geometry("1200x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧框架
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 右侧框架
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        
        # SQL输入区域标题
        title_frame = ttk.Frame(self.left_frame)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.sql_label = ttk.Label(title_frame, text="SQL创建表语句", font=('Microsoft YaHei', 10, 'bold'))
        self.sql_label.pack(side=tk.LEFT)
        
        # SQL文本框
        self.sql_text = scrolledtext.ScrolledText(
            self.left_frame, 
            height=15, 
            font=('Consolas', 10),
            wrap=tk.WORD,
            background='#ffffff',
            padx=5,
            pady=5
        )
        self.sql_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 左侧按钮
        self.load_btn = ttk.Button(self.button_frame, text="加载SQL", command=self.load_sql)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(self.button_frame, text="保存SQL", command=self.save_sql)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(self.button_frame, text="清空", command=self.clear_sql)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 右侧按钮
        self.export_drawio_btn = ttk.Button(self.button_frame, text="导出Draw.io", command=self.export_drawio)
        self.export_drawio_btn.pack(side=tk.RIGHT, padx=5)
        
        self.generate_btn = ttk.Button(self.button_frame, text="生成ER图", command=self.generate_diagram)
        self.generate_btn.pack(side=tk.RIGHT, padx=5)
        
        # 右侧配置区域
        ttk.Label(self.right_frame, text="配置选项", font=('Microsoft YaHei', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # 配置选项使用LabelFrame
        settings_frame = ttk.LabelFrame(self.right_frame, text="图形设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 表间距设置
        ttk.Label(settings_frame, text="表间距:").pack(anchor=tk.W)
        self.table_radius_var = tk.StringVar(value="6")
        self.table_radius_entry = ttk.Entry(settings_frame, textvariable=self.table_radius_var, width=10)
        self.table_radius_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # 字段间距设置
        ttk.Label(settings_frame, text="字段到表距离:").pack(anchor=tk.W)
        self.field_radius_var = tk.StringVar(value="2")
        self.field_radius_entry = ttk.Entry(settings_frame, textvariable=self.field_radius_var, width=10)
        self.field_radius_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # 在字段间距设置后添加数据类型选项
        self.show_type_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="显示数据类型", 
                       variable=self.show_type_var).pack(anchor=tk.W, pady=(0, 10))
        
        # 在右侧配置区域添加新选项
        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 添加表格选择下拉框
        ttk.Label(settings_frame, text="单表生成:").pack(anchor=tk.W)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(settings_frame, textvariable=self.table_var, state='readonly')
        self.table_combo.pack(anchor=tk.W, pady=(0, 5))
        
        # 单表生成按钮区域
        single_table_btn_frame = ttk.Frame(settings_frame)
        single_table_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加单表生成按钮
        self.generate_single_btn = ttk.Button(single_table_btn_frame, text="生成单表ER图", 
                                            command=self.generate_single_table_diagram)
        self.generate_single_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加单表导出Draw.io按钮
        self.export_single_drawio_btn = ttk.Button(single_table_btn_frame, text="导出单表Draw.io", 
                                                  command=self.export_single_table_drawio)
        self.export_single_drawio_btn.pack(side=tk.LEFT, padx=5)
        
        # 更新表格列表
        self.sql_text.bind('<KeyRelease>', self.update_table_list)
        
        # 预填充示例SQL
        self.load_example_sql()
        
        # 初始化表格列表 - 移到加载示例SQL之后
        self.update_table_list()
        
    def load_example_sql(self):
        example_sql = '''CREATE TABLE 客户表 (
        客户ID INT PRIMARY KEY,
        姓名 VARCHAR(100),
        邮箱 VARCHAR(100),
        电话 VARCHAR(20)
    );

    CREATE TABLE 订单表 (
        订单ID INT PRIMARY KEY,
        客户ID INT,
        下单时间 TIMESTAMP,
        总金额 DECIMAL(10,2)
    );

    CREATE TABLE 商品表 (
        商品ID INT PRIMARY KEY,
        商品名称 VARCHAR(200),
        价格 DECIMAL(10,2),
        库存 INT
    );'''
        self.sql_text.delete(1.0, tk.END)
        self.sql_text.insert(tk.END, example_sql)

    def load_sql(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.sql_text.delete(1.0, tk.END)
                    self.sql_text.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("错误", f"读取文件时出错：{str(e)}")

    def save_sql(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.sql_text.get(1.0, tk.END))
                messagebox.showinfo("成功", "SQL已保存！")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错：{str(e)}")

    def clear_sql(self):
        if messagebox.askyesno("确认", "确定要清空当前SQL吗？"):
            self.sql_text.delete(1.0, tk.END)

    def generate_diagram(self):
        sql_content = self.sql_text.get(1.0, tk.END)
        if not sql_content.strip():
            messagebox.showwarning("警告", "请先输入SQL语句！")
            return
            
        try:
            # 获取用户设置的参数
            table_radius = float(self.table_radius_var.get())
            field_radius = float(self.field_radius_var.get())
            show_type = self.show_type_var.get()  # 获取是否显示数据类型
            
            generator = ERDiagramGenerator()
            generator.parse_sql(sql_content, table_radius, field_radius, show_type)  # 添加 show_type 参数
            generator.generate()
            messagebox.showinfo("成功", "ER图已生成！")
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数值！")
        except Exception as e:
            messagebox.showerror("错误", f"生成ER图时出错：{str(e)}")

    def update_table_list(self, event=None):
        """更新表格下拉列表"""
        sql_content = self.sql_text.get(1.0, tk.END)
        table_pattern = r'CREATE TABLE\s+`?(\w+)`?\s*\('
        tables = re.finditer(table_pattern, sql_content, re.IGNORECASE)
        table_names = [table.group(1) for table in tables]
        self.table_combo['values'] = table_names
        if table_names and not self.table_var.get():
            self.table_combo.set(table_names[0])

    def generate_single_table_diagram(self):
        """生成单个表的ER图"""
        selected_table = self.table_var.get()
        if not selected_table:
            messagebox.showwarning("警告", "请先选择一个表！")
            return
            
        sql_content = self.sql_text.get(1.0, tk.END)
        try:
            table_pattern = f"CREATE TABLE\\s+`?{selected_table}`?\\s*\\([^;]+\\);"
            match = re.search(table_pattern, sql_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                table_sql = match.group(0)
                generator = ERDiagramGenerator()
                show_type = self.show_type_var.get()  # 获取是否显示数据类型
                generator.parse_sql(table_sql, table_radius=0, field_radius=2, show_type=show_type)
                generator.generate(f'er_diagram_{selected_table}')
                messagebox.showinfo("成功", f"{selected_table}的ER图已生成！")
            else:
                messagebox.showerror("错误", f"未找到表 {selected_table} 的定义！")
        except Exception as e:
            messagebox.showerror("错误", f"生成ER图时出错：{str(e)}")

    def export_drawio(self):
        """导出为draw.io可编辑的格式"""
        sql_content = self.sql_text.get(1.0, tk.END)
        if not sql_content.strip():
            messagebox.showwarning("警告", "请先输入SQL语句！")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".drawio",
                filetypes=[("Draw.io files", "*.drawio"), ("XML files", "*.xml"), ("All files", "*.*")]
            )
            if file_path:
                # 获取用户设置的参数
                table_radius = float(self.table_radius_var.get())
                field_radius = float(self.field_radius_var.get())
                show_type = self.show_type_var.get()  # 获取是否显示数据类型
                
                generator = DrawioGenerator()
                xml_content = generator.generate_drawio(sql_content, table_radius, field_radius, show_type)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                messagebox.showinfo("成功", "Draw.io文件已生成！")
        except Exception as e:
            messagebox.showerror("错误", f"生成Draw.io文件时出错：{str(e)}")

    def export_single_table_drawio(self):
        """导出单个表的Draw.io文件"""
        selected_table = self.table_var.get()
        if not selected_table:
            messagebox.showwarning("警告", "请先选择一个表！")
            return
            
        sql_content = self.sql_text.get(1.0, tk.END)
        try:
            # 提取选中表的SQL
            table_pattern = f"CREATE TABLE\\s+`?{selected_table}`?\\s*\\([^;]+\\);"
            match = re.search(table_pattern, sql_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                table_sql = match.group(0)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".drawio",
                    filetypes=[("Draw.io files", "*.drawio"), ("XML files", "*.xml"), ("All files", "*.*")]
                )
                if file_path:
                    generator = DrawioGenerator()
                    show_type = self.show_type_var.get()  # 获取是否显示数据类型
                    xml_content = generator.generate_drawio(table_sql, table_radius=0, field_radius=2, show_type=show_type)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(xml_content)
                    messagebox.showinfo("成功", f"{selected_table}的Draw.io文件已生成！")
            else:
                messagebox.showerror("错误", f"未找到表 {selected_table} 的定义！")
        except Exception as e:
            messagebox.showerror("错误", f"导出Draw.io文件时出错：{str(e)}")

class ERDiagramGenerator:
    def __init__(self):
        self.dot = graphviz.Graph('ER', 
                                 engine='neato',  
                                 graph_attr={
                                     'splines': 'spline',
                                     'overlap': 'scale',
                                     'sep': '+30',
                                     'esep': '+20',
                                     'nodesep': '1.0',
                                     'charset': 'utf8'  # 添加UTF-8支持
                                 })
        self.dot.attr('node', shape='rectangle', fontname='Microsoft YaHei')  # 使用中文字体

    def parse_sql(self, sql_content, table_radius=6, field_radius=2, show_type=False):
        table_pattern = r'CREATE TABLE\s+`?(\w+)`?\s*\(([\s\S]*?)\);'
        tables = list(re.finditer(table_pattern, sql_content, re.IGNORECASE))
        table_count = len(tables)
        
        table_angle_step = 360 / table_count if table_count > 1 else 0
        
        for i, table in enumerate(tables):
            table_name = table.group(1)
            fields_text = table.group(2)
            
            table_angle = i * table_angle_step
            table_x = table_radius * math.cos(math.radians(table_angle))
            table_y = table_radius * math.sin(math.radians(table_angle))
            
            self.dot.node(table_name, table_name, 
                         pos=f"{table_x},{table_y}!",
                         fontname='Microsoft YaHei')
            
            field_pattern = r'`?(\w+)`?\s+([^,\n]+)'
            field_count = len(list(re.finditer(field_pattern, fields_text)))
            angle_step = 360 / field_count
            
            for j, field in enumerate(re.finditer(field_pattern, fields_text)):
                field_name = field.group(1)
                field_type = field.group(2).strip()
                
                field_angle = j * angle_step
                field_x = table_x + field_radius * math.cos(math.radians(field_angle))
                field_y = table_y + field_radius * math.sin(math.radians(field_angle))
                
                field_node_name = f"{table_name}_{field_name}"
                # 根据选项决定是否显示数据类型
                field_label = f"{field_name}\n{field_type}" if show_type else field_name
                
                self.dot.node(field_node_name, 
                            field_label,
                            shape='ellipse',
                            pos=f"{field_x},{field_y}!",
                            fontname='Microsoft YaHei')
                
                self.dot.edge(table_name, field_node_name)

    def generate(self, output_file='er_diagram'):
        # 移除 encoding 参数
        self.dot.render(output_file, view=True, format='png')

class DrawioGenerator:
    def __init__(self):
        self.next_id = 2  # 从2开始，因为0和1已被根节点使用

    def get_next_id(self):
        # 使用字符串ID避免重复
        current_id = f"node_{self.next_id}"
        self.next_id += 1
        return current_id

    def generate_drawio(self, sql_content, table_radius=6, field_radius=2, show_type=False):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="SQL ER Generator" version="21.1.1">
  <diagram id="ER-Diagram" name="ER图">
    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
'''
        
        table_pattern = r'CREATE TABLE\s+`?(\w+)`?\s*\(([\s\S]*?)\);'
        tables = list(re.finditer(table_pattern, sql_content, re.IGNORECASE))
        table_count = len(tables)
        center_x, center_y = 400, 300
        
        for i, table in enumerate(tables):
            table_name = table.group(1)
            fields_text = table.group(2)
            
            angle = (2 * math.pi * i) / table_count if table_count > 1 else 0
            table_x = center_x + table_radius * 50 * math.cos(angle)
            table_y = center_y + table_radius * 50 * math.sin(angle)
            
            # 简化表格为普通方框
            table_id = self.get_next_id()
            xml += f'''        <mxCell id="{table_id}" value="{table_name}" style="whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="{table_x}" y="{table_y}" width="120" height="40" as="geometry"/>
        </mxCell>
'''
            
            field_pattern = r'`?(\w+)`?\s+([^,\n]+)'
            fields = list(re.finditer(field_pattern, fields_text))
            
            for j, field in enumerate(fields):
                field_name = field.group(1)
                field_type = field.group(2).strip()
                
                field_angle = (2 * math.pi * j) / len(fields)
                field_x = table_x + field_radius * 100 * math.cos(field_angle)
                field_y = table_y + field_radius * 100 * math.sin(field_angle)
                
                # 根据选项决定是否显示数据类型
                field_value = f"{field_name}&#10;{field_type}" if show_type else field_name
                
                field_id = self.get_next_id()
                xml += f'''        <mxCell id="{field_id}" value="{field_value}" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="{field_x}" y="{field_y}" width="120" height="60" as="geometry"/>
        </mxCell>
'''
                
                line_id = self.get_next_id()
                xml += f'''        <mxCell id="{line_id}" style="endArrow=none;html=1;edgeStyle=none;" edge="1" parent="1" source="{table_id}" target="{field_id}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
'''
        
        xml += '''      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
        
        return xml

if __name__ == "__main__":
    root = tk.Tk()
    app = ERDiagramGUI(root)
    root.mainloop() 