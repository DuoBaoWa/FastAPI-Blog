# FastAPI Blog 博客应用

<div align="center">

[English](#english) | [中文](#中文)

</div>

---

<a id="english"></a>

## 📝 FastAPI Blog - A Modern Markdown Blog Platform

### Overview

FastAPI Blog is a modern, lightweight blog platform built with FastAPI and SQLite. It supports Markdown content, multilingual interface (English/Chinese), and provides a clean, responsive design for both readers and content creators.

### ✨ Features

- **Markdown Support**: Write your blog posts in Markdown format for easy formatting and readability.
- **Responsive Design**: Enjoy a seamless experience across desktop and mobile devices.
- **User Authentication**: Secure login system for administrators and content creators.
- **Admin Dashboard**: Intuitive interface for managing posts and users.
- **Multilingual Support**: Switch between English and Chinese interfaces with a single click.
- **Dark/Light Theme**: Choose your preferred viewing experience.
- **RESTful API**: Well-documented API for programmatic access to blog content.

### 🛠️ Technology Stack

- <img src="https://fastapi.tiangolo.com/img/favicon.png" width="16" height="16"> **Backend**: FastAPI (Python)
- <img src="https://www.sqlite.org/images/sqlite370_banner.gif" width="16" height="16"> **Database**: SQLite
- <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/html/html.png" width="16" height="16"> <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/css/css.png" width="16" height="16"> <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/javascript/javascript.png" width="16" height="16"> **Frontend**: HTML, CSS, JavaScript
- <img src="https://jwt.io/img/favicon/favicon-16x16.png" width="16" height="16"> **Authentication**: JWT (JSON Web Tokens)
- <img src="https://marked.js.org/img/logo-black.svg" width="16" height="16"> **Markdown Processing**: Marked.js
- <img src="https://highlightjs.org/favicon.png" width="16" height="16"> **Syntax Highlighting**: Highlight.js

### 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-blog.git
   cd fastapi-blog
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create an admin user:
   ```bash
   python create_admin.py
   ```

5. Start the application:
   ```bash
   python main.py
   ```

6. Access the blog at http://localhost:8000

### 🚀 Usage

#### For Readers

- Visit the homepage to see the latest blog posts
- Navigate to the Blog section to browse all published articles
- Switch between languages using the language toggle in the navigation bar
- Toggle between light and dark themes with the theme switch

#### For Administrators

- Log in at /login with your admin credentials
- Access the admin dashboard at /admin
- Create, edit, and publish blog posts
- Manage user accounts and permissions

### 📸 Screenshots

*(Add screenshots of your application here)*

### 📄 API Documentation

The API documentation is available at http://localhost:8000/docs when the application is running.

---

<a id="中文"></a>

## 📝 FastAPI 博客 - 现代化的 Markdown 博客平台

### 概述

FastAPI 博客是一个基于 FastAPI 和 SQLite 构建的现代轻量级博客平台。它支持 Markdown 内容，多语言界面（英文/中文），并为读者和内容创作者提供简洁、响应式的设计。

### ✨ 特点

- **Markdown 支持**：使用 Markdown 格式编写博客文章，轻松实现格式化和提高可读性。
- **响应式设计**：在桌面和移动设备上享受无缝体验。
- **用户认证**：为管理员和内容创作者提供安全的登录系统。
- **管理员仪表板**：直观的界面用于管理文章和用户。
- **多语言支持**：一键切换英文和中文界面。
- **深色/浅色主题**：选择您喜欢的浏览体验。
- **RESTful API**：提供完善文档的 API，用于程序化访问博客内容。

### 🛠️ 技术栈

- <img src="https://fastapi.tiangolo.com/img/favicon.png" width="16" height="16"> **后端**：FastAPI (Python)
- <img src="https://www.sqlite.org/images/sqlite370_banner.gif" width="16" height="16"> **数据库**：SQLite
- <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/html/html.png" width="16" height="16"> <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/css/css.png" width="16" height="16"> <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/javascript/javascript.png" width="16" height="16"> **前端**：HTML, CSS, JavaScript
- <img src="https://jwt.io/img/favicon/favicon-16x16.png" width="16" height="16"> **认证**：JWT (JSON Web Tokens)
- <img src="https://marked.js.org/img/logo-black.svg" width="16" height="16"> **Markdown 处理**：Marked.js
- <img src="https://highlightjs.org/favicon.png" width="16" height="16"> **语法高亮**：Highlight.js

### 📦 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/fastapi-blog.git
   cd fastapi-blog
   ```

2. 创建虚拟环境并激活：
   ```bash
   python -m venv venv
   # Windows 系统
   venv\Scripts\activate
   # macOS/Linux 系统
   source venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 创建管理员用户：
   ```bash
   python create_admin.py
   ```

5. 启动应用：
   ```bash
   python main.py
   ```

6. 访问博客：http://localhost:8000

### 🚀 使用方法

#### 对于读者

- 访问首页查看最新博客文章
- 导航到博客部分浏览所有已发布文章
- 使用导航栏中的语言切换按钮切换语言
- 使用主题开关在浅色和深色主题之间切换

#### 对于管理员

- 在 /login 使用管理员凭据登录
- 在 /admin 访问管理员仪表板
- 创建、编辑和发布博客文章
- 管理用户账户和权限

### 📸 截图

*(在此处添加应用程序的截图)*

### 📄 API 文档

应用程序运行时，API 文档可在 http://localhost:8000/docs 获取。