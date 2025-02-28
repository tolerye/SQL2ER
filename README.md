# SQL ER图生成器

一个基于 Web 的 SQL ER 图生成器，可以将 SQL 建表语句转换为 ER 图，支持多种导出格式。

## 功能特点

- 🎯 支持从 SQL CREATE TABLE 语句生成 ER 图
- 🌐 支持中文表名和字段名
- 📐 可调整表间距和字段到表的距离
- 📝 可选择是否显示数据类型
- 📊 支持生成 PNG 格式的 ER 图
- 📥 支持导出为 Draw.io 可编辑格式
- 🔗 支持直接在 Draw.io 在线编辑
- 🎨 简洁美观的界面设计
- 👀 实时预览生成的 ER 图

## 安装要求

- Python 3.7+
- Graphviz

### 系统依赖

首先需要安装 Graphviz：

- Windows:
  ```bash
  # 从 https://graphviz.org/download/ 下载并安装
  ```
- Mac:
  ```bash
  brew install graphviz
  ```
- Linux:
  ```bash
  sudo apt-get install graphviz
  ```

### Python 依赖

```bash
pip install -r requirements.txt
```

## 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/sql-er-generator.git
cd sql-er-generator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 在浏览器中访问：`http://localhost:5000`

## 使用说明

1. 在文本框中输入 CREATE TABLE 语句
2. 调整配置选项（可选）：
   - 表间距：调整表之间的距离
   - 字段到表距离：调整字段与表之间的距离
   - 显示数据类型：选择是否显示字段的数据类型
3. 选择操作：
   - 点击"生成ER图"：在右侧预览生成的图片
   - 点击"下载Draw.io"：下载可在 Draw.io 中编辑的文件
   - 点击"在线打开"：直接在 Draw.io 网站中打开并编辑

## 示例 SQL

```sql
CREATE TABLE 客户表 (
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
```

## 技术栈

- 后端：
  - Flask
  - Graphviz
  - Python
- 前端：
  - HTML5
  - CSS3
  - JavaScript

## 注意事项

- 确保系统已正确安装 Graphviz
- SQL 语句必须使用标准的 CREATE TABLE 语法
- 支持中文字符，使用 UTF-8 编码
- 建议使用现代浏览器（Chrome、Firefox、Edge 等）

## 常见问题

1. 如果遇到 "Command 'dot' not found" 错误：
   - 检查是否已安装 Graphviz
   - 确保 Graphviz 已添加到系统环境变量

2. 如果生成的图片中文显示为方块：
   - 检查系统是否安装了对应的中文字体
   - 确保使用 UTF-8 编码

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

[Tolerye]

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的 ER 图生成功能
- 支持 Draw.io 导出和在线编辑
