from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: str
    user_name: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    name: str
    role: str
    department: str

class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    message: str

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    total_sources: int

class UserPermissions(BaseModel):
    role: str
    role_name: str
    role_description: str
    accessible_departments: List[str]
    permissions: Dict[str, str]

class SystemStats(BaseModel):
    vector_store_stats: Dict[str, Any]
    total_departments: int
    supported_roles: List[str] 