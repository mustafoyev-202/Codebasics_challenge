import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import config
from app.services.document_processor import DocumentProcessor
from app.services import auth_service

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.vector_store = None
        self.document_processor = DocumentProcessor()
    
    def _get_langchain_vector_store(self) -> Chroma:
        """Get or create the LangChain vector store object."""
        try:
            vector_store = Chroma(
                client=self.client,
                collection_name=config.COLLECTION_NAME,
                embedding_function=self.embeddings
            )
            return vector_store
        except Exception as e:
            print(f"Error creating LangChain vector store: {e}")
            return None
    
    def create_collection(self, collection_name: str = None) -> chromadb.Collection:
        """Create or get a ChromaDB collection."""
        if collection_name is None:
            collection_name = config.COLLECTION_NAME
        
        try:
            collection = self.client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
        except:
            collection = self.client.create_collection(name=collection_name)
            print(f"Created new collection: {collection_name}")
        
        return collection
    
    def add_documents(self, documents: List[Document], collection_name: str = None) -> bool:
        """Add documents to the vector store."""
        if not documents:
            print("No documents to add")
            return False
        
        try:
            # Create or get collection
            collection = self.create_collection(collection_name)
            
            # Prepare documents for ChromaDB
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            ids = [f"doc_{i}" for i in range(len(documents))]
            
            # Add documents to collection
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Successfully added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False
    
    def initialize_vector_store(self) -> bool:
        """Initialize the vector store with all department documents."""
        try:
            # Process all department documents
            all_documents = self.document_processor.process_all_departments()
            
            # Combine all documents
            combined_documents = []
            for department, docs in all_documents.items():
                combined_documents.extend(docs)
            
            if not combined_documents:
                print("No documents found to process")
                return False
            
            # Add documents to vector store
            success = self.add_documents(combined_documents)
            
            if success:
                # Initialize LangChain vector store
                self.vector_store = self._get_langchain_vector_store()
                
                if self.vector_store:
                    print(f"Vector store initialized with {len(combined_documents)} document chunks")
                    return True
                else:
                    print("Failed to create LangChain vector store")
                    return False
            
            return False
            
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            return False
    
    def search_documents(self, query: str, user_role: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search documents based on user role and permissions."""
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        if not self.vector_store:
            print("Vector store not initialized")
            return []
        
        try:
            # Get accessible departments for the user
            accessible_departments = config.get_accessible_departments(user_role)
            
            if not accessible_departments:
                print(f"No accessible departments for role: {user_role}")
                return []
            
            # Search with department filter
            filter_dict = {"department": {"$in": accessible_departments}}
            
            # Perform similarity search
            results = self.vector_store.similarity_search_with_relevance_scores(
                query=query,
                k=top_k,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_department_documents(self, department: str, user_role: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific department if user has access."""
        if not auth_service.check_permission(user_role, department):
            print(f"User role {user_role} does not have access to {department} department")
            return []
        
        if not self.vector_store:
            print("Vector store not initialized")
            return []
        
        try:
            # Search with department filter
            filter_dict = {"department": department}
            
            # Get all documents for the department
            results = self.vector_store.similarity_search_with_relevance_scores(
                query="",  # Empty query to get all documents
                k=1000,  # Large number to get all documents
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error getting department documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        try:
            collection = self.client.get_collection(name=config.COLLECTION_NAME)
            count = collection.count()
            
            # Get unique departments
            results = collection.get()
            departments = set()
            file_types = set()
            
            for metadata in results['metadatas']:
                if metadata:
                    departments.add(metadata.get('department', 'unknown'))
                    file_types.add(metadata.get('file_type', 'unknown'))
            
            return {
                "total_documents": count,
                "departments": list(departments),
                "file_types": list(file_types)
            }
            
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}
    
    def reset_collection(self) -> bool:
        """Reset the vector store collection."""
        try:
            self.client.delete_collection(name=config.COLLECTION_NAME)
            print(f"Deleted collection: {config.COLLECTION_NAME}")
            return True
        except Exception as e:
            print(f"Error resetting collection: {e}")
            return False 