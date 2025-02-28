from flask import Flask, render_template, request, jsonify, send_file
import graphviz
import re
import math
import os
import tempfile
from datetime import datetime
import io

app = Flask(__name__)

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
                                     'charset': 'utf8'
                                 })
        self.dot.attr('node', shape='rectangle', fontname='Microsoft YaHei')

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
                field_label = f"{field_name}\n{field_type}" if show_type else field_name
                
                self.dot.node(field_node_name, 
                            field_label,
                            shape='ellipse',
                            pos=f"{field_x},{field_y}!",
                            fontname='Microsoft YaHei')
                
                self.dot.edge(table_name, field_node_name)

    def generate(self, output_file):
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 生成图片
            result = self.dot.render(output_file, format='png', cleanup=True)
            
            # 验证输出文件是否存在
            if not os.path.exists(result):
                raise Exception("图片生成失败")
                
            return result
        except Exception as e:
            raise Exception(f"Graphviz错误: {str(e)}")

class DrawioGenerator:
    def __init__(self):
        self.next_id = 2  # 从2开始，因为0和1已被根节点使用

    def get_next_id(self):
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    sql_content = request.form.get('sql', '')
    show_type = request.form.get('show_type') == 'true'
    table_radius = float(request.form.get('table_radius', 6))
    field_radius = float(request.form.get('field_radius', 2))
    
    if not sql_content:
        return jsonify({'error': '请输入SQL语句'}), 400

    try:
        generator = ERDiagramGenerator()
        generator.parse_sql(sql_content, table_radius, field_radius, show_type)
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        try:
            # 使用完整的绝对路径
            output_base = os.path.join(os.path.abspath(temp_dir), 'er_diagram')
            
            # 生成图片，graphviz会自动添加.png后缀
            output_path = generator.generate(output_base)
            
            # 确保文件存在
            if not os.path.exists(output_path):
                raise Exception("生成的图片文件未找到")
            
            # 读取图片并返回
            with open(output_path, 'rb') as f:
                image_data = f.read()
            
            # 清理临时文件
            try:
                os.unlink(output_path)  # 删除.png文件
                dot_file = f"{output_base}.dot"  # graphviz生成的dot文件
                if os.path.exists(dot_file):
                    os.unlink(dot_file)
            finally:
                os.rmdir(temp_dir)
            
            return send_file(
                io.BytesIO(image_data),
                mimetype='image/png',
                as_attachment=False
            )
            
        except Exception as e:
            # 清理临时目录
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.unlink(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            raise Exception(f"生成图片失败: {str(e)}")
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export-drawio', methods=['POST'])
def export_drawio():
    sql_content = request.form.get('sql', '')
    show_type = request.form.get('show_type') == 'true'
    table_radius = float(request.form.get('table_radius', 6))
    field_radius = float(request.form.get('field_radius', 2))
    
    if not sql_content:
        return jsonify({'error': '请输入SQL语句'}), 400

    try:
        generator = DrawioGenerator()
        xml_content = generator.generate_drawio(sql_content, table_radius, field_radius, show_type)
        
        # 检查是否需要下载文件
        if request.args.get('download') == 'true':
            return send_file(
                io.BytesIO(xml_content.encode('utf-8')),
                mimetype='application/xml',
                as_attachment=True,
                download_name='er_diagram.drawio'
            )
        else:
            # 直接返回 XML 内容
            return xml_content, 200, {'Content-Type': 'application/xml'}
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 