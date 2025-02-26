import jwt
import datetime
import os

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

def generate_token(username: str) -> str:
    """生成 JWT token"""
    payload = {
        "username": username,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24),  # token 24小时后过期
        "iat": datetime.datetime.now(datetime.UTC)  # token 创建时间
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str) -> bool:
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception as e:
        print(f"{e = }")
        return None