import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from backend.models import User, RateLimit
from backend.database import SessionLocal
from backend.schemas import UserRole

SECRET_KEY = "43ed080f1efd09b6856bb5b5c01bde00b5925beb1a8ce35573bc0a06bd8c192c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="Bearer")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=2)

    to_encode.update({"exp": expire, "sub": str(data["sub"])})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def is_admin(user=Depends(get_current_user)):
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


RATE_LIMIT = 5
TIME_WINDOW = 60

class DBRateLimiter:
    def __init__(self, request: Request):
        self.request = request
        self.user = None

    def __call__(self):
        if self.request.url.path in ["/users/register", "/users/login"]:
            print("inside if condition")
            return
        self.user = get_current_user()
        identifier = self.user.id
        db = SessionLocal()
        rate_record = db.query(RateLimit).filter(RateLimit.user_id == identifier).first()
        now = datetime.utcnow()

        if not rate_record:
            rate_record = RateLimit(user_id=identifier, count=1, start_time=now)
            db.add(rate_record)
            db.commit()
        else:
            elapsed = (now - rate_record.start_time).total_seconds()
            if elapsed > TIME_WINDOW:
                rate_record.count = 1
                rate_record.start_time = now
            else:
                if rate_record.count >= RATE_LIMIT:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                rate_record.count += 1
            db.commit()