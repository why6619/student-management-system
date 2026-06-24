# 学生成绩管理系统 - 部署指南

## 环境要求

- Python 3.8+
- pip
- 可选：Docker, Docker Compose

## 部署方式

### 方式一：直接运行（开发环境）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

访问 http://localhost:5000

### 方式二：使用 Waitress（Windows 生产环境）

```bash
# 安装 Waitress
pip install waitress

# 启动服务
waitress-serve --listen=0.0.0.0:5000 wsgi:app
```

### 方式三：使用 Gunicorn（Linux 生产环境）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### 方式四：使用 Docker（推荐）

```bash
# 构建镜像
docker build -t student-management .

# 运行容器
docker run -d -p 5000:5000 --name student-management student-management
```

或使用 Docker Compose：

```bash
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SECRET_KEY | Flask 密钥，用于会话加密 | your_secret_key_here_change_in_production |
| FLASK_ENV | 运行环境 | development |

### 安全建议

1. **修改默认密钥**：在生产环境中必须修改 `SECRET_KEY`
2. **设置强密码**：首次登录后立即修改管理员密码
3. **使用 HTTPS**：在生产环境中配置 SSL/TLS
4. **限制访问**：配置防火墙只允许必要的 IP 访问

## 默认账号

- **用户名**: admin
- **密码**: admin123

## 项目结构

```
student_management/
├── app.py              # 主应用文件
├── wsgi.py             # WSGI 入口文件
├── requirements.txt    # 依赖列表
├── Dockerfile          # Docker 配置
├── docker-compose.yml  # Docker Compose 配置
├── instance/
│   └── site.db         # SQLite 数据库文件
├── lib/                # 本地依赖库
└── templates/          # HTML 模板文件
```
