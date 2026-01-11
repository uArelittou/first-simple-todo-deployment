# 🚀 Flask + MySQL + Nginx 全栈部署实战 (CentOS 9)

本项目记录了在 CentOS Stream 9 环境下，从零搭建一个完整任务管理系统（Todo List）的全过程。项目涵盖了数据库配置、后端接口开发、前端页面部署以及 Nginx 反向代理与 SELinux 安全加固。

## 🏗️ 架构概览

```mermaid
graph LR
    User(用户浏览器) -- HTTP/80 --> Nginx(反向代理/静态服务)
    subgraph CentOS_System
        Nginx -- 转发/3000 --> Systemd(守护进程)
        Systemd -- 管理 --> Gunicorn(WSGI)
        Gunicorn -- 运行 --> Flask(后端 API)
        Flask -- 读写 --> MySQL(数据库)
    end
🛠️ 第一步：环境初始化与数据库 (MySQL)
为了防止环境冲突，首先清理系统默认数据库并安装 MySQL 8.0。

1. 安装 MySQL
Bash

# 清理旧环境
sudo dnf remove mariadb mariadb-server mysql mysql-server -y
sudo dnf module disable mysql -y

# 安装 MySQL 8.0 社区版
sudo dnf install [https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm](https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm) -y
sudo dnf install mysql-community-server -y

# 启动并自启
sudo systemctl start mysqld
sudo systemctl enable mysqld
2. 初始配置与用户创建
Bash

# 获取临时密码
sudo grep 'temporary password' /var/log/mysqld.log

# 登录并修改 Root 密码
mysql -u root -p
# ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourStrongPassword!';

# 创建业务数据库与用户
CREATE DATABASE todo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'qqq'@'127.0.0.1' IDENTIFIED BY 'qqq';
GRANT ALL PRIVILEGES ON todo.* TO 'qqq'@'127.0.0.1';
FLUSH PRIVILEGES;
3. 建表与数据预热
SQL

USE todo;
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content VARCHAR(255) NOT NULL,
    status TINYINT(1) DEFAULT 0
);

-- 插入测试数据
INSERT INTO tasks (content) VALUES ('完成后端部署学习');
INSERT INTO tasks (content) VALUES ('解决 SELinux 报错');
🐍 第二步：后端开发与部署 (Flask)
1. Python 环境准备
注意：为了避免 SELinux 路径问题，我们将项目统一部署在 /var/www/todo。

Bash

# 安装依赖
sudo dnf install python3 python3-pip python3-devel -y

# 创建目录与虚拟环境
mkdir -p /var/www/todo/backend
cd /var/www/todo/backend
python3 -m venv venv
source venv/bin/activate

# 安装 Flask 与 Gunicorn
pip install flask gunicorn pymysql cryptography
2. 业务代码 (app.py)
代码位于 todo/app.py，主要实现了连接 MySQL 并返回 JSON 数据。

3. Systemd 进程守护
创建 /etc/systemd/system/flask_app.service，确保服务开机自启且崩溃重启。

Ini, TOML

[Unit]
Description=Flask Backend
After=network.target

[Service]
User=qqq
Group=qqq
WorkingDirectory=/var/www/todo/backend
# 必须使用虚拟环境内的 gunicorn 绝对路径
ExecStart=/var/www/todo/backend/venv/bin/gunicorn -w 3 -b 127.0.0.1:3000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
🎨 第三步：前端与反向代理 (Nginx)
1. 前端文件部署
将 HTML/CSS/JS 文件放置于 /var/www/todo/frontend。

index.html: 包含 Fetch API 逻辑，自动从 /api/tasks 获取数据并渲染。

2. Nginx 配置
创建 /etc/nginx/conf.d/todo.conf 实现动静分离：

Nginx

server {
    listen 80;
    server_name 192.168.8.11; # 你的服务器 IP

    # 前端静态文件
    location / {
        root /var/www/todo/frontend;
        index index.html;
    }

    # 后端 API 转发
    location /api {
        proxy_pass [http://127.0.0.1:3000](http://127.0.0.1:3000);
        proxy_set_header Host $host;
    }
}
🛡️ 第四步：安全加固 (SELinux & Firewall)
这是部署中最具挑战性的一环，我们坚持不关闭 SELinux，而是配置正确的规则。

1. 防火墙放行
Bash

sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
2. SELinux 策略配置
允许 Nginx 联网转发 (解决 502 错误): sudo setsebool -P httpd_can_network_connect 1

允许 Nginx 连接数据库 (如果 Web 服务器直连 DB): sudo setsebool -P httpd_can_network_connect_db 1

修复文件上下文标签 (解决 403 Permission Denied):

Bash

# 注册 Web 内容标签
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/todo(/.*)?"
# 注册二进制执行标签 (针对 venv)
sudo semanage fcontext -a -t bin_t "/var/www/todo/backend/venv/bin(/.*)?"
# 应用更改
sudo restorecon -Rv /var/www/todo
🔧 踩坑与故障排查记录 (Troubleshooting)
在学习过程中遇到的典型问题及解决方案：

1. 进程启动报错 203/EXEC
原因：Systemd 指定用户 (qqq) 对父级目录没有执行权限 (+x)，无法进入目录。

解决：确保 /var/www 及 todo 目录权限正确，且 ExecStart 路径无误。

2. 虚拟环境失效
现象：移动项目目录后 Flask 无法启动。

原因：venv 内部路径硬编码。

解决：严禁移动虚拟环境。若必须移动，需删除旧 venv 并重新创建。

3. MySQL 登录失败
现象：日志中找不到临时密码或忘记密码。

解决：修改 /etc/my.cnf 添加 skip-grant-tables 开启免密模式，登录后刷新权限并重置密码。

4. Nginx 403 Permission Denied
现象：日志报错 open() failed (13: Permission denied)。

原因：SELinux 标签不匹配。

解决：使用 chcon -Rt httpd_sys_content_t ... 或 semanage 修复标签。

5. Python 缩进错误
现象：IndentationError 导致服务起不来。

技巧：使用 vim 的粘贴模式 :set paste 防止复制代码时缩进错乱，或使用 =G 自动格式化。
