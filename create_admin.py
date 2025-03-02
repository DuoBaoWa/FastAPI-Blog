import sys
from sqlalchemy.orm import Session
from app.models import SessionLocal
from app import crud, schemas

def create_admin_user(username: str, email: str, password: str):
    db = SessionLocal()
    try:
        # 检查用户是否已存在
        existing_user = crud.get_user_by_username(db, username)
        if existing_user:
            print(f"用户 {username} 已存在")
            return False
            
        # 创建用户
        user_in = schemas.UserCreate(
            username=username,
            email=email,
            password=password
        )
        user = crud.create_user(db, user_in)
        
        # 设置为管理员
        user.is_admin = True
        db.commit()
        
        print(f"管理员用户 {username} 创建成功!")
        return True
        
    except Exception as e:
        print(f"创建管理员时出错: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("使用方法: python create_admin.py 用户名 邮箱 密码")
        sys.exit(1)
        
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    success = create_admin_user(username, email, password)
    if not success:
        sys.exit(1)