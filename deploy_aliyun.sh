#!/bin/bash
echo "=== 学生成绩管理系统 - 阿里云部署脚本 ==="

APP_DIR="/www/wwwroot/student-management"

echo "1. 创建部署目录..."
mkdir -p $APP_DIR
cd $APP_DIR

echo "2. 克隆代码..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/why6619/student-management-system.git .
fi

echo "3. 安装依赖..."
pip install -r requirements.txt

echo "4. 创建 systemd 服务..."
cat > /etc/systemd/system/student-management.service << EOF
[Unit]
Description=Student Management System
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment=SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
ExecStart=/usr/local/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "5. 启动服务..."
systemctl daemon-reload
systemctl enable student-management
systemctl restart student-management

echo "6. 配置防火墙..."
firewall-cmd --zone=public --add-port=5000/tcp --permanent
firewall-cmd --reload

echo "部署完成！"
echo "访问地址: http://你的服务器IP:5000"
echo "默认账号: admin / admin123"
