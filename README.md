# AITS (AI-empowered Intelligent Testing System) 

AITS 是一个由 AI 驱动的下一代自动化测试与智能实验室平台。它通过前后端分离微服务架构，以大语言模型（如 DeepSeek、OpenAI）赋能传统的接口测试（API）与 Web 端到端自动化（Web UI），提供诸如智能生成 API 场景、全链路数据驱动关联、自动转化测试步骤等重磅效能特性。

## 🎯 核心能力

*   **API 接口自动化测试**: 整合 HttpRunner 与 Pytest 引擎，支持断言、变量提取提取以及可视化场景流执行。
*   **Web UI 自动化与重构版面**: 面向 Web 管理高度可定制的多彩列表页面、提供完善的过滤（类别、优先级）、集成化脚本挂载（MidScene 关联）。
*   **AI 智能助手引擎**: 搭载定制大模型，基于 WebSocket 机制流式输出打字机交互，支持让 AI 为您梳理生成接口的场景拓扑。
*   **内置 Allure 测试报告**: 在后端直接派发 Pytest 用例的同时整合 Allure 工具透明构建可视化网页并在客户端悬挂调出。
*   **定时任务与调配中心 (规划中)**: 针对所有的测试环境支持强大的 Celery Beat 级别 Cron 表达式监控与循环发射策略。

## 🛠 技术栈

*   **Frontend (前端):** [Vue 3](https://vuejs.org/), [Vite](https://vitejs.dev/), [Element Plus](https://element-plus.org/), [Pinia](https://pinia.vuejs.org/)
*   **Backend (后端):** [Django 5](https://www.djangoproject.com/), [Django REST Framework](https://www.django-rest-framework.org/), [Django Channels](https://channels.readthedocs.io/) (WebSockets)
*   **Asynchronous Engine (异步执行引擎):** [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/)
*   **Database (数据库):** [PostgreSQL](https://www.postgresql.org/) (Production) / SQLite (Local Dev)
*   **Test Engines (测试执行器):** Pytest, Allure-pytest

## 🚀 快速启动

你可以通过 Docker Compose 实现极其简单的一键启动方案，无需配置本地的 Python 或 Nodejs。

### 环境依赖
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### Docker 容器化启动 (生产/极速演示)

在项目根目录下直接运行：

```bash
docker-compose up -d --build
```

此时系统将自动拉起：
1. **PostgreSQL** 数据库
2. **Redis** 缓存与消息服
3. **Django Backend** 后端服务 (端口 8000)
4. **Celery Worker** 测试消费节点
5. **Celery Beat** 调度器 (支持定时任务)
6. **Nginx Frontend** 静态前端网页 (端口 80)

在浏览器中打开 `http://localhost` 即可体验平台。

### 本地原生开发环境搭建

若您需要参与框架核心的代码二次开发。详尽启动需要如下两部分依赖：

#### 1. Backend (后端)
```bash
cd aits_backend
# 推荐新建 python 虚拟环境
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# 启动 Django 服务器
python manage.py runserver 0.0.0.0:8000
```
*(注意：需要本地开启 Redis 支持 Celery / Channels)*
并在另一终端启动 Celery Worker 监听测试任务:
```bash
python -m celery -A aits_backend worker -l info
```

#### 2. Frontend (前端)
```bash
cd aits_frontend
npm install
npm run dev
```
打开 `http://localhost:5173` 进行前后端联调开发。


---
*由 AI Agentic Assistant AITS Team 构建并维护。*
