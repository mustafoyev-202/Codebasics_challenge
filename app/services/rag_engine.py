import google.generativeai as genai
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import config
from app.services.vector_store import VectorStoreManager
from app.services import auth_service

class RAGEngine:
    def __init__(self):
        # Initialize Google Gemini client
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            max_output_tokens=config.MAX_TOKENS,
            google_api_key=config.GOOGLE_API_KEY
        )
        
        # Initialize vector store manager
        self.vector_store_manager = VectorStoreManager()
        
        # Initialize vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store if not already done."""
        try:
            # Check if vector store is already initialized
            stats = self.vector_store_manager.get_collection_stats()
            if stats.get("total_documents", 0) == 0:
                print("Initializing vector store...")
                success = self.vector_store_manager.initialize_vector_store()
                if success:
                    print("✅ Vector store initialized successfully")
                else:
                    print("❌ Failed to initialize vector store")
            else:
                print(f"✅ Vector store already initialized with {stats['total_documents']} documents")
                # Ensure the vector store object is properly set
                if not self.vector_store_manager.vector_store:
                    self.vector_store_manager.vector_store = self.vector_store_manager._get_langchain_vector_store()
        except Exception as e:
            print(f"❌ Error initializing vector store: {e}")
            # Try to initialize anyway
            try:
                self.vector_store_manager.initialize_vector_store()
            except Exception as e2:
                print(f"❌ Failed to initialize vector store on retry: {e2}")
    
    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results into context for the LLM."""
        if not search_results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            content = result["content"]
            metadata = result["metadata"]
            score = result["relevance_score"]
            
            # Format the context with source information
            context_part = f"Source {i} (Relevance: {score:.3f}):\n"
            context_part += f"Department: {metadata.get('department', 'Unknown')}\n"
            context_part += f"File: {metadata.get('file_name', 'Unknown')}\n"
            context_part += f"Content: {content}\n"
            context_part += "-" * 50 + "\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _get_system_prompt(self, user_role: str) -> str:
        """Get the appropriate system prompt for the user role."""
        base_prompt = config.SYSTEM_PROMPTS.get(user_role, config.SYSTEM_PROMPTS["employee"])
        
        # Add role-specific instructions
        role_info = auth_service.get_user_role_info(user_role)
        if role_info:
            role_description = role_info.get("description", "")
            base_prompt += f"\n\nYour role: {role_description}"
        
        return base_prompt
    
    def _create_messages(self, query: str, context: str, user_role: str) -> List:
        """Create messages for the LLM."""
        system_prompt = self._get_system_prompt(user_role)
        
        # Create the user message with context
        user_message = f"""Based on the following context, please answer the user's question. 
        If the context doesn't contain enough information to answer the question, 
        please say so and suggest what additional information might be needed.

        Context:
        {context}

        User Question: {query}

        Please provide a comprehensive answer and cite the sources you used."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        return messages
    
    def query(self, user_query: str, user_role: str) -> Dict[str, Any]:
        """Process a user query and return a response with sources."""
        try:
            # Ensure vector store is initialized
            if not self.vector_store_manager.vector_store:
                print("Vector store not initialized, attempting to initialize...")
                self._initialize_vector_store()
            
            # Search for relevant documents
            search_results = self.vector_store_manager.search_documents(
                query=user_query,
                user_role=user_role
            )
            
            # Format context from search results
            context = self._format_context(search_results)
            
            # Create messages for LLM
            messages = self._create_messages(user_query, context, user_role)
            
            # Generate response
            response = self.llm(messages)
            
            # Extract sources from search results
            sources = []
            for result in search_results:
                metadata = result["metadata"]
                sources.append({
                    "department": metadata.get("department", "Unknown"),
                    "file_name": metadata.get("file_name", "Unknown"),
                    "relevance_score": result["relevance_score"]
                })
            
            return {
                "response": response.content,
                "sources": sources,
                "context_used": context,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your query: {str(e)}",
                "sources": [],
                "context_used": "",
                "total_sources": 0
            }
    
    def get_department_summary(self, department: str, user_role: str) -> Dict[str, Any]:
        """Get a summary of documents for a specific department."""
        if not auth_service.check_permission(user_role, department):
            return {
                "response": f"You don't have permission to access {department} department data.",
                "sources": [],
                "context_used": "",
                "total_sources": 0
            }
        
        try:
            # Ensure vector store is initialized
            if not self.vector_store_manager.vector_store:
                print("Vector store not initialized, attempting to initialize...")
                self._initialize_vector_store()
            
            # Get all documents for the department
            documents = self.vector_store_manager.get_department_documents(department, user_role)
            
            if not documents:
                return {
                    "response": f"No documents found for {department} department.",
                    "sources": [],
                    "context_used": "",
                    "total_sources": 0
                }
            
            # Create a summary query
            summary_query = f"Provide a comprehensive summary of the {department} department data, including key insights, trends, and important information."
            
            # Format context
            context = self._format_context(documents)
            
            # Create messages for LLM
            messages = self._create_messages(summary_query, context, user_role)
            
            # Generate response
            response = self.llm(messages)
            
            # Extract sources
            sources = []
            for doc in documents:
                metadata = doc["metadata"]
                sources.append({
                    "department": metadata.get("department", "Unknown"),
                    "file_name": metadata.get("file_name", "Unknown"),
                    "relevance_score": doc["relevance_score"]
                })
            
            return {
                "response": response.content,
                "sources": sources,
                "context_used": context,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            print(f"Error getting department summary: {e}")
            return {
                "response": f"I apologize, but I encountered an error while generating the department summary: {str(e)}",
                "sources": [],
                "context_used": "",
                "total_sources": 0
            }
    
    def get_user_permissions(self, user_role: str) -> Dict[str, Any]:
        """Get user permissions and accessible departments."""
        role_info = auth_service.get_user_role_info(user_role)
        accessible_departments = auth_service.get_accessible_departments(user_role)
        
        return {
            "role": user_role,
            "role_name": role_info.get("name", "Unknown"),
            "role_description": role_info.get("description", ""),
            "accessible_departments": accessible_departments,
            "permissions": role_info.get("permissions", {})
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = self.vector_store_manager.get_collection_stats()
        return {
            "vector_store_stats": stats,
            "total_departments": len(config.DEPARTMENT_FOLDERS),
            "supported_roles": list(config.ROLES.keys())
        } 