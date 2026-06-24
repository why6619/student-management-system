#!/bin/bash
echo "=== 学生成绩管理系统部署脚本 ==="

echo "1. 安装依赖..."
pip install -r requirements.txt

echo "2. 设置环境变量..."
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(16))")

echo "3. 启动服务..."
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app

echo "服务已启动！访问地址: http://localhost:5000"
echo "默认账号: admin / admin123"
