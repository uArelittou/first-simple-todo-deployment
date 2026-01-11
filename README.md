# 🚀 Flask + MySQL + Nginx 全栈部署实战 (CentOS 9)

本项目记录了在 CentOS Stream 9 环境下，从零搭建一个完整任务管理系统（Todo List）的全过程。项目涵盖了数据库配置、后端接口开发、前端页面部署以及 Nginx 反向代理与 SELinux 安全加固。

## 🏗️ 架构概览

```mermaid
graph LR
    User("用户浏览器") -- HTTP/80 --> Nginx("反向代理/静态服务")
    subgraph CentOS_System
        Nginx -- 转发/3000 --> Systemd("守护进程")
        Systemd -- 管理 --> Gunicorn("WSGI")
        Gunicorn -- 运行 --> Flask("后端 API")
        Flask -- 读写 --> MySQL("数据库")
    end
