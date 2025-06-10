from fastapi import FastAPI, HTTPException, status, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import timedelta

from app.schemas.auth import (
    Token, TokenData, User, LoginRequest, QueryRequest, 
    QueryResponse, UserPermissions, SystemStats
)
from app.services import auth_service
from app.services.rag_engine import RAGEngine
import config

# Initialize FastAPI app
app = FastAPI(
    title="FinSolve RAG Assistant API",
    description="Role-based RAG system for FinSolve Technologies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()

# Authentication endpoints
@app.post("/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Authenticate user and return JWT token."""
    user = auth_service.authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user["role"],
        "user_name": user["name"]
    }

@app.get("/me", response_model=User)
async def get_current_user(current_user: dict = Depends(auth_service.verify_token)):
    """Get current user information."""
    return current_user

# Query endpoints
@app.post("/chat", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    current_user: dict = Depends(auth_service.verify_token)
):
    """Process a user query and return response with sources."""
    try:
        result = rag_engine.query(query_request.message, current_user["role"])
        return QueryResponse(
            response=result["response"],
            sources=result["sources"],
            total_sources=result["total_sources"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/department/{department}/summary", response_model=QueryResponse)
async def get_department_summary(
    department: str,
    current_user: dict = Depends(auth_service.verify_token)
):
    """Get a summary of documents for a specific department."""
    try:
        result = rag_engine.get_department_summary(department, current_user["role"])
        return QueryResponse(
            response=result["response"],
            sources=result["sources"],
            total_sources=result["total_sources"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting department summary: {str(e)}"
        )

# User permissions and system info
@app.get("/permissions", response_model=UserPermissions)
async def get_user_permissions(current_user: dict = Depends(auth_service.verify_token)):
    """Get user permissions and accessible departments."""
    try:
        permissions = rag_engine.get_user_permissions(current_user["role"])
        return UserPermissions(**permissions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting permissions: {str(e)}"
        )

@app.get("/system/stats", response_model=SystemStats)
async def get_system_stats(current_user: dict = Depends(auth_service.verify_token)):
    """Get system statistics."""
    # Only allow C-level executives to view system stats
    if current_user["role"] != "c_level":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only C-level executives can view system statistics"
        )
    
    try:
        stats = rag_engine.get_system_stats()
        return SystemStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system stats: {str(e)}"
        )

@app.get("/roles", response_model=Dict[str, Any])
async def get_available_roles():
    """Get available roles and their descriptions."""
    return config.ROLES

@app.get("/departments", response_model=List[str])
async def get_available_departments():
    """Get available departments."""
    return list(config.DEPARTMENT_FOLDERS.keys())

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "FinSolve RAG Assistant is running"}

# Sample users endpoint (for demonstration)
@app.get("/sample-users")
async def get_sample_users():
    """Get sample users for demonstration."""
    # Only return username and role for security
    sample_users = {}
    for username, user_data in config.SAMPLE_USERS.items():
        sample_users[username] = {
            "name": user_data["name"],
            "role": user_data["role"],
            "department": user_data["department"]
        }
    return sample_users

# Legacy endpoints for backward compatibility
@app.get("/test")
async def test(user=Depends(auth_service.verify_token)):
    """Test endpoint for backward compatibility."""
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)