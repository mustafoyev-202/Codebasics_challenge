import os
import pandas as pd
import markdown
from typing import List, Dict, Any
from pathlib import Path
from app.services import config
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def load_markdown_file(self, file_path: str) -> str:
        """Load and process markdown files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Convert markdown to plain text for better processing
            html_content = markdown.markdown(content)
            # Remove HTML tags for cleaner text
            import re
            clean_text = re.sub(r'<[^>]+>', '', html_content)
            return clean_text
        except Exception as e:
            print(f"Error loading markdown file {file_path}: {e}")
            return ""
    
    def load_csv_file(self, file_path: str) -> str:
        """Load and process CSV files."""
        try:
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to text representation
            text_content = []
            
            # Add column descriptions
            text_content.append("Column Descriptions:")
            for col in df.columns:
                text_content.append(f"- {col}: {df[col].dtype}")
            
            # Add sample data (first 10 rows)
            text_content.append("\nSample Data:")
            text_content.append(df.head(10).to_string())
            
            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                text_content.append("\nSummary Statistics:")
                text_content.append(df[numeric_cols].describe().to_string())
            
            # Add department-specific insights
            if "department" in df.columns:
                text_content.append("\nDepartment Distribution:")
                dept_counts = df['department'].value_counts()
                for dept, count in dept_counts.items():
                    text_content.append(f"- {dept}: {count} employees")
            
            if "salary" in df.columns:
                text_content.append("\nSalary Insights:")
                text_content.append(f"- Average Salary: ${df['salary'].mean():,.2f}")
                text_content.append(f"- Median Salary: ${df['salary'].median():,.2f}")
                text_content.append(f"- Salary Range: ${df['salary'].min():,.2f} - ${df['salary'].max():,.2f}")
            
            if "performance_rating" in df.columns:
                text_content.append("\nPerformance Insights:")
                text_content.append(f"- Average Performance Rating: {df['performance_rating'].mean():.2f}")
                text_content.append(f"- Performance Distribution:")
                perf_counts = df['performance_rating'].value_counts().sort_index()
                for rating, count in perf_counts.items():
                    text_content.append(f"  - Rating {rating}: {count} employees")
            
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error loading CSV file {file_path}: {e}")
            return ""
    
    def load_text_file(self, file_path: str) -> str:
        """Load plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading text file {file_path}: {e}")
            return ""
    
    def load_document(self, file_path: str) -> str:
        """Load document based on file extension."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.md':
            return self.load_markdown_file(file_path)
        elif file_extension == '.csv':
            return self.load_csv_file(file_path)
        elif file_extension == '.txt':
            return self.load_text_file(file_path)
        else:
            print(f"Unsupported file type: {file_extension}")
            return ""
    
    def chunk_document(self, content: str, metadata: Dict[str, Any]) -> List[Document]:
        """Split document content into chunks."""
        if not content.strip():
            return []
        
        # Create a single document first
        doc = Document(page_content=content, metadata=metadata)
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        return chunks
    
    def process_department_data(self, department: str) -> List[Document]:
        """Process all documents for a specific department."""
        documents = []
        department_folder = config.DEPARTMENT_FOLDERS.get(department)
        
        if not department_folder or not os.path.exists(department_folder):
            print(f"Department folder not found: {department_folder}")
            return documents
        
        for file_name in os.listdir(department_folder):
            file_path = os.path.join(department_folder, file_name)
            
            if os.path.isfile(file_path):
                file_extension = Path(file_path).suffix.lower()
                
                if file_extension in config.SUPPORTED_EXTENSIONS:
                    print(f"Processing {file_path}")
                    
                    # Load document content
                    content = self.load_document(file_path)
                    
                    if content:
                        # Create metadata
                        metadata = {
                            "department": department,
                            "file_name": file_name,
                            "file_path": file_path,
                            "file_type": file_extension[1:],  # Remove the dot
                            "source": f"{department}/{file_name}"
                        }
                        
                        # Chunk the document
                        chunks = self.chunk_document(content, metadata)
                        documents.extend(chunks)
        
        return documents
    
    def process_all_departments(self) -> Dict[str, List[Document]]:
        """Process documents for all departments."""
        all_documents = {}
        
        for department in config.DEPARTMENT_FOLDERS.keys():
            print(f"Processing department: {department}")
            documents = self.process_department_data(department)
            all_documents[department] = documents
            print(f"Processed {len(documents)} chunks for {department}")
        
        return all_documents
    
    def get_document_summary(self, documents: List[Document]) -> Dict[str, Any]:
        """Get summary statistics for processed documents."""
        if not documents:
            return {}
        
        total_chunks = len(documents)
        departments = set()
        file_types = set()
        total_content_length = 0
        
        for doc in documents:
            departments.add(doc.metadata.get("department", "unknown"))
            file_types.add(doc.metadata.get("file_type", "unknown"))
            total_content_length += len(doc.page_content)
        
        return {
            "total_chunks": total_chunks,
            "departments": list(departments),
            "file_types": list(file_types),
            "average_chunk_length": total_content_length / total_chunks if total_chunks > 0 else 0,
            "total_content_length": total_content_length
        } 