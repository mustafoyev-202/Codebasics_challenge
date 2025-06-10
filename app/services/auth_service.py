from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import config

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password."""
    if username not in config.SAMPLE_USERS:
        return None
    
    user = config.SAMPLE_USERS[username]
    if not verify_password(password, get_password_hash(user["password"])):
        return None
    
    return {
        "username": username,
        "name": user["name"],
        "role": user["role"],
        "department": user["department"]
    }

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if username not in config.SAMPLE_USERS:
        raise credentials_exception
    
    user = config.SAMPLE_USERS[username]
    return {
        "username": username,
        "name": user["name"],
        "role": user["role"],
        "department": user["department"]
    }

def check_permission(user_role: str, department: str, permission_level: str = "read") -> bool:
    """Check if user has permission to access a specific department."""
    if user_role not in config.ROLES:
        return False
    
    role_permissions = config.ROLES[user_role]["permissions"]
    
    if department not in role_permissions:
        return False
    
    user_permission = role_permissions[department]
    
    if permission_level == "read":
        return user_permission in ["read", "full"]
    elif permission_level == "full":
        return user_permission == "full"
    
    return False

def get_accessible_departments(user_role: str) -> list:
    """Get list of departments accessible to a user role."""
    if user_role not in config.ROLES:
        return []
    
    role_permissions = config.ROLES[user_role]["permissions"]
    accessible_departments = []
    
    for department, permission in role_permissions.items():
        if permission in ["read", "full"]:
            accessible_departments.append(department)
    
    return accessible_departments

def get_user_role_info(user_role: str) -> dict:
    """Get role information for a user."""
    if user_role not in config.ROLES:
        return {}
    
    return config.ROLES[user_role] 