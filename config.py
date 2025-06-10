import os
from typing import Dict, List, Set
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")
MODEL_NAME = "gemini-2.0-flash"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "finsolve_documents"

# Role-based Access Control Configuration
ROLES = {
    "finance": {
        "name": "Finance Team",
        "description": "Access to financial reports, marketing expenses, equipment costs, reimbursements, etc.",
        "permissions": {
            "finance": "full",
            "general": "read",
            "marketing": "read",  # Limited access to marketing expenses
            "hr": "read",  # Limited access to HR costs
            "engineering": "none"
        }
    },
    "marketing": {
        "name": "Marketing Team", 
        "description": "Access to campaign performance data, customer feedback, and sales metrics.",
        "permissions": {
            "marketing": "full",
            "general": "read",
            "finance": "read",  # Limited access to marketing budget
            "hr": "none",
            "engineering": "none"
        }
    },
    "hr": {
        "name": "HR Team",
        "description": "Access employee data, attendance records, payroll, and performance reviews.",
        "permissions": {
            "hr": "full",
            "general": "read",
            "finance": "read",  # Limited access to HR costs
            "marketing": "none",
            "engineering": "none"
        }
    },
    "engineering": {
        "name": "Engineering Department",
        "description": "Access to technical architecture, development processes, and operational guidelines.",
        "permissions": {
            "engineering": "full",
            "general": "read",
            "finance": "none",
            "marketing": "none",
            "hr": "none"
        }
    },
    "c_level": {
        "name": "C-Level Executives",
        "description": "Full access to all company data.",
        "permissions": {
            "finance": "full",
            "marketing": "full", 
            "hr": "full",
            "engineering": "full",
            "general": "full"
        }
    },
    "employee": {
        "name": "Employee Level",
        "description": "Access only to general company information such as policies, events, and FAQs.",
        "permissions": {
            "general": "read",
            "finance": "none",
            "marketing": "none",
            "hr": "none",
            "engineering": "none"
        }
    }
}

# Department to folder mapping
DEPARTMENT_FOLDERS = {
    "finance": "resources/data/finance",
    "marketing": "resources/data/marketing", 
    "hr": "resources/data/hr",
    "engineering": "resources/data/engineering",
    "general": "resources/data/general"
}

# File extensions to process
SUPPORTED_EXTENSIONS = {'.md', '.txt', '.csv'}

# Authentication settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Sample users for demonstration (matching the original users)
SAMPLE_USERS = {
    "Tony": {
        "password": "password123",
        "role": "c_level",
        "name": "Tony Sharma",
        "department": "Innovation"
    },
    "Bruce": {
        "password": "securepass",
        "role": "marketing",
        "name": "Bruce Wayne",
        "department": "Marketing"
    },
    "Sam": {
        "password": "financepass",
        "role": "finance",
        "name": "Sam Wilson",
        "department": "Finance"
    },
    "Peter": {
        "password": "pete123",
        "role": "engineering",
        "name": "Peter Pandey",
        "department": "Engineering"
    },
    "Sid": {
        "password": "sidpass123",
        "role": "marketing",
        "name": "Sid Sharma",
        "department": "Marketing"
    },
    "Natasha": {
        "password": "hrpass123",
        "role": "hr",
        "name": "Natasha Romanoff",
        "department": "HR"
    }
}

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# System prompts for different roles
SYSTEM_PROMPTS = {
    "finance": """You are a helpful AI assistant for the Finance team at FinSolve Technologies. 
    You have access to financial reports, expense data, and budget information. 
    Provide accurate financial insights while maintaining confidentiality. 
    Always cite your sources when providing information.""",
    
    "marketing": """You are a helpful AI assistant for the Marketing team at FinSolve Technologies.
    You have access to campaign performance data, customer insights, and marketing metrics.
    Provide marketing insights and recommendations based on available data.
    Always cite your sources when providing information.""",
    
    "hr": """You are a helpful AI assistant for the HR team at FinSolve Technologies.
    You have access to employee data, attendance records, and HR policies.
    Provide HR insights while maintaining employee privacy and confidentiality.
    Always cite your sources when providing information.""",
    
    "engineering": """You are a helpful AI assistant for the Engineering team at FinSolve Technologies.
    You have access to technical documentation, architecture details, and development processes.
    Provide technical insights and guidance based on available documentation.
    Always cite your sources when providing information.""",
    
    "c_level": """You are a helpful AI assistant for C-Level executives at FinSolve Technologies.
    You have access to all company data and can provide comprehensive insights across all departments.
    Provide strategic insights and executive-level analysis.
    Always cite your sources when providing information.""",
    
    "employee": """You are a helpful AI assistant for employees at FinSolve Technologies.
    You have access to general company information, policies, and FAQs.
    Provide helpful information about company policies and general information.
    Always cite your sources when providing information."""
}

def get_user_role_info(user_role: str) -> dict:
    """Get role information for a user."""
    if user_role not in ROLES:
        return {}
    
    return ROLES[user_role]

def get_accessible_departments(user_role: str) -> list:
    """Get list of departments accessible to a user role."""
    if user_role not in ROLES:
        return []
    
    role_permissions = ROLES[user_role]["permissions"]
    accessible_departments = []
    
    for department, permission in role_permissions.items():
        if permission in ["read", "full"]:
            accessible_departments.append(department)
    
    return accessible_departments 