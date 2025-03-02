from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from jose import JWTError, jwt
from typing import Dict, Any, Optional
import traceback

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("blog-app")

# 配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="FastAPI Markdown Blog")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库，如果表不存在则创建"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # 创建文章表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        author_id INTEGER NOT NULL,
        FOREIGN KEY (author_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

# 在启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("应用启动，数据库已初始化")

def verify_password(plain_password, hashed_password):
    """验证密码"""
    try:
        return bcrypt.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密码验证错误: {e}")
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    """获取当前登录用户"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={"detail": "未认证"}, status_code=401)
        
        token = authorization.replace("Bearer ", "")
        
        try:
            # 验证令牌
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                return JSONResponse(content={"detail": "无效的凭证"}, status_code=401)
        except JWTError as e:
            logger.error(f"JWT解析错误: {e}")
            return JSONResponse(content={"detail": "无效的凭证"}, status_code=401)
        
        # 获取用户
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, email, is_active, is_admin FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        conn.close()
        
        if not user:
            return JSONResponse(content={"detail": "用户不存在"}, status_code=404)
        
        user_dict = dict(user)
        user_dict['is_active'] = bool(user_dict['is_active'])
        user_dict['is_admin'] = bool(user_dict['is_admin'])
        
        return user_dict
    
    except Exception as e:
        logger.exception("获取当前用户时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 请求日志记录中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"收到请求: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.debug(f"请求处理完成: {request.method} {request.url} - {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"请求处理异常: {request.method} {request.url}")
        raise

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误", "detail": str(exc)},
    )

# 前端页面路由
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/blog")
async def blog_posts(request: Request):
    return templates.TemplateResponse("blog/post_list.html", {"request": request})

@app.get("/blog/{post_id}")
async def blog_post(request: Request, post_id: int):
    # 获取文章数据
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if not post:
        return templates.TemplateResponse("blog/post.html", {"request": request, "post_id": post_id, "error": "Post not found"})
    
    # 将post对象传递给模板
    return templates.TemplateResponse("blog/post.html", {"request": request, "post_id": post_id, "post": post})

@app.get("/admin")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@app.get("/admin/posts/new")
async def new_post(request: Request):
    return templates.TemplateResponse("admin/post_editor.html", {"request": request})

@app.get("/admin/posts/{post_id}/edit")
async def edit_post(request: Request, post_id: int):
    return templates.TemplateResponse("admin/post_editor.html", {"request": request, "post_id": post_id})

# API 路由
@app.post("/api/login")
async def login(request: Request):
    try:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        
        if not username or not password:
            return JSONResponse(content={"detail": "用户名和密码不能为空"}, status_code=400)
        
        # 验证用户
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, email, hashed_password, is_active, is_admin FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        conn.close()
        
        if not user:
            return JSONResponse(content={"detail": "用户名或密码不正确"}, status_code=401)
        
        # 验证密码
        if not verify_password(password, user['hashed_password']):
            return JSONResponse(content={"detail": "用户名或密码不正确"}, status_code=401)
        
        # 检查用户是否激活
        if not user['is_active']:
            return JSONResponse(content={"detail": "账户未激活"}, status_code=400)
        
        # 生成令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        logger.exception("登录时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/register")
async def register(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if not username or not email or not password:
            return JSONResponse(content={"detail": "用户名、邮箱和密码不能为空"}, status_code=400)
        
        # 检查用户名和邮箱是否已存在
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return JSONResponse(content={"detail": "用户名或邮箱已被注册"}, status_code=400)
        
        # 创建新用户
        hashed_password = bcrypt.hash(password)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)',
            (username, email, hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {"id": user_id, "username": username, "email": email}
    
    except Exception as e:
        logger.exception("注册时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/users/me")
async def get_current_user_info(request: Request):
    return await get_current_user(request)

@app.get("/api/users")
async def get_users(request: Request):
    try:
        # 验证管理员权限
        current_user = await get_current_user(request)
        if isinstance(current_user, JSONResponse):
            return current_user
        
        if not current_user.get('is_admin', False):
            return JSONResponse(content={"detail": "权限不足"}, status_code=403)
        
        # 获取所有用户
        conn = get_db_connection()
        users = conn.execute('SELECT id, username, email, is_active, is_admin FROM users').fetchall()
        conn.close()
        
        user_list = []
        for user in users:
            user_dict = dict(user)
            user_dict['is_active'] = bool(user_dict['is_active'])
            user_dict['is_admin'] = bool(user_dict['is_admin'])
            user_list.append(user_dict)
            
        return user_list
    except Exception as e:
        logger.exception("获取用户列表时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/posts")
async def get_posts(request: Request, limit: int = 100):
    try:
        # 获取当前用户（如果已登录）
        token = request.headers.get("Authorization")
        is_admin = False
        
        if token and token.startswith("Bearer "):
            try:
                token = token.replace("Bearer ", "")
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                
                if username:
                    conn = get_db_connection()
                    user = conn.execute(
                        'SELECT is_admin FROM users WHERE username = ?', 
                        (username,)
                    ).fetchone()
                    conn.close()
                    
                    if user and user['is_admin']:
                        is_admin = True
            except:
                # 忽略令牌错误，将用户视为普通访问者
                pass
        
        # 获取文章列表
        conn = get_db_connection()
        if is_admin:
            # 管理员可以看到所有文章
            query = '''
                SELECT p.id, p.title, p.content, p.published, p.created_at, p.updated_at, 
                       p.author_id, u.username as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                ORDER BY p.created_at DESC
                LIMIT ?
            '''
            posts = conn.execute(query, (limit,)).fetchall()
        else:
            # 普通用户只能看到已发布的文章
            query = '''
                SELECT p.id, p.title, p.content, p.published, p.created_at, p.updated_at, 
                       p.author_id, u.username as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.published = 1
                ORDER BY p.created_at DESC
                LIMIT ?
            '''
            posts = conn.execute(query, (limit,)).fetchall()
        
        conn.close()
        
        post_list = []
        for post in posts:
            post_dict = dict(post)
            post_dict['published'] = bool(post_dict['published'])
            post_list.append(post_dict)
            
        return post_list
    except Exception as e:
        logger.exception("获取文章列表时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/posts/{post_id}")
async def get_post(request: Request, post_id: int):
    try:
        # 获取当前用户（如果已登录）
        token = request.headers.get("Authorization")
        is_admin = False
        
        if token and token.startswith("Bearer "):
            try:
                token = token.replace("Bearer ", "")
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                
                if username:
                    conn = get_db_connection()
                    user = conn.execute(
                        'SELECT is_admin FROM users WHERE username = ?', 
                        (username,)
                    ).fetchone()
                    conn.close()
                    
                    if user and user['is_admin']:
                        is_admin = True
            except:
                # 忽略令牌错误，将用户视为普通访问者
                pass
        
        # 获取文章
        conn = get_db_connection()
        query = '''
            SELECT p.id, p.title, p.content, p.published, p.created_at, p.updated_at, 
                   p.author_id, u.username as author_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            WHERE p.id = ?
        '''
        
        if not is_admin:
            # 非管理员只能看到已发布文章
            query += ' AND p.published = 1'
            
        post = conn.execute(query, (post_id,)).fetchone()
        conn.close()
        
        if post is None:
            return JSONResponse(content={"detail": "文章不存在"}, status_code=404)
        
        post_dict = dict(post)
        post_dict['published'] = bool(post_dict['published'])
        
        return post_dict
    except Exception as e:
        logger.exception("获取文章详情时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/posts")
async def create_post(request: Request):
    try:
        logger.info("接收到创建文章请求")
        
        # 验证用户权限
        current_user = await get_current_user(request)
        if isinstance(current_user, JSONResponse):
            return current_user
        
        if not current_user.get('is_admin', False):
            return JSONResponse(content={"detail": "权限不足"}, status_code=403)
        
        # 获取文章数据
        try:
            data = await request.json()
            logger.debug(f"接收到的文章数据: {data}")
        except json.JSONDecodeError:
            return JSONResponse(content={"detail": "无效的JSON格式"}, status_code=400)
        
        title = data.get('title')
        content = data.get('content')
        published = data.get('published', True)
        
        if not title or not content:
            return JSONResponse(content={"detail": "标题和内容不能为空"}, status_code=400)
        
        # 插入文章
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO posts (title, content, published, author_id, created_at, updated_at) VALUES (?, ?, ?, ?, datetime("now"), datetime("now"))',
            (title, content, 1 if published else 0, current_user['id'])
        )
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"文章创建成功, ID: {post_id}")
        
        # 返回成功响应
        return {
            "id": post_id,
            "title": title,
            "content": content,
            "published": published,
            "author_id": current_user['id'],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.exception("创建文章时出错")
        traceback.print_exc()  # 打印详细错误到控制台
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.put("/api/posts/{post_id}")
async def update_post(request: Request, post_id: int):
    try:
        # 验证用户权限
        current_user = await get_current_user(request)
        if isinstance(current_user, JSONResponse):
            return current_user
        
        if not current_user.get('is_admin', False):
            return JSONResponse(content={"detail": "权限不足"}, status_code=403)
        
        # 获取文章数据
        data = await request.json()
        
        # 获取现有文章
        conn = get_db_connection()
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
        
        if not post:
            conn.close()
            return JSONResponse(content={"detail": "文章不存在"}, status_code=404)
        
        # 更新字段
        title = data.get('title', post['title'])
        content = data.get('content', post['content'])
        published = data.get('published', post['published'])
        
        conn.execute(
            'UPDATE posts SET title = ?, content = ?, published = ?, updated_at = datetime("now") WHERE id = ?',
            (title, content, 1 if published else 0, post_id)
        )
        conn.commit()
        conn.close()
        
        return {
            "id": post_id,
            "title": title,
            "content": content,
            "published": published,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.exception("更新文章时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/api/posts/{post_id}")
async def delete_post(request: Request, post_id: int):
    try:
        # 验证用户权限
        current_user = await get_current_user(request)
        if isinstance(current_user, JSONResponse):
            return current_user
        
        if not current_user.get('is_admin', False):
            return JSONResponse(content={"detail": "权限不足"}, status_code=403)
        
        # 检查文章是否存在
        conn = get_db_connection()
        post = conn.execute('SELECT id FROM posts WHERE id = ?', (post_id,)).fetchone()
        
        if not post:
            conn.close()
            return JSONResponse(content={"detail": "文章不存在"}, status_code=404)
        
        # 删除文章
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        
        return JSONResponse(content={"detail": "文章已删除"}, status_code=200)
    
    except Exception as e:
        logger.exception("删除文章时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.put("/api/users/{user_id}")
async def update_user(request: Request, user_id: int):
    try:
        # 验证管理员权限
        current_user = await get_current_user(request)
        if isinstance(current_user, JSONResponse):
            return current_user
        
        if not current_user.get('is_admin', False):
            return JSONResponse(content={"detail": "权限不足"}, status_code=403)
        
        # 获取更新数据
        data = await request.json()
        username = data.get('username')
        email = data.get('email')
        is_active = data.get('is_active')
        is_admin = data.get('is_admin')
        password = data.get('password')
        
        # 获取现有用户
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            conn.close()
            return JSONResponse(content={"detail": "用户不存在"}, status_code=404)
        
        # 更新用户信息
        updates = []
        params = []
        
        if username is not None:
            # 检查用户名是否已存在
            existing = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, user_id)).fetchone()
            if existing:
                conn.close()
                return JSONResponse(content={"detail": "用户名已被使用"}, status_code=400)
            
            updates.append("username = ?")
            params.append(username)
        
        if email is not None:
            # 检查邮箱是否已存在
            existing = conn.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id)).fetchone()
            if existing:
                conn.close()
                return JSONResponse(content={"detail": "邮箱已被使用"}, status_code=400)
            
            updates.append("email = ?")
            params.append(email)
        
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if is_admin is not None:
            updates.append("is_admin = ?")
            params.append(1 if is_admin else 0)
        
        if password is not None:
            updates.append("hashed_password = ?")
            params.append(bcrypt.hash(password))
        
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            params.append(user_id)
            conn.execute(query, params)
            conn.commit()
        
        # 获取更新后的用户信息
        updated_user = conn.execute('SELECT id, username, email, is_active, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not updated_user:
            return JSONResponse(content={"detail": "用户更新失败"}, status_code=500)
        
        updated_user_dict = dict(updated_user)
        updated_user_dict['is_active'] = bool(updated_user_dict['is_active'])
        updated_user_dict['is_admin'] = bool(updated_user_dict['is_admin'])
        
        return updated_user_dict
    
    except Exception as e:
        logger.exception("更新用户时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/api/users/{user_id}")
async def delete_user(request: Request, user_id: int):
    try:
        # 验证管理员权限
        current_user = await get_current_user(request)
        if isinstance(current_user, JSONResponse):
            return current_user
        
        if not current_user.get('is_admin', False):
            return JSONResponse(content={"detail": "权限不足"}, status_code=403)
        
        # 防止删除自己
        if current_user['id'] == user_id:
            return JSONResponse(content={"detail": "不能删除自己的账户"}, status_code=400)
        
        # 检查用户是否存在
        conn = get_db_connection()
        user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            conn.close()
            return JSONResponse(content={"detail": "用户不存在"}, status_code=404)
        
        # 删除用户
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return JSONResponse(content={"detail": "用户已删除"}, status_code=200)
    
    except Exception as e:
        logger.exception("删除用户时出错")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")