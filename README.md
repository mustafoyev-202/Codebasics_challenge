# FinSolve RAG Assistant - Role-Based Access Control System

## 🏢 Overview

This project implements a **Retrieval-Augmented Generation (RAG) chatbot** for FinSolve Technologies, providing role-based access to department-specific insights. The system uses FastAPI, ChromaDB, Google Gemini, and Streamlit for a secure, scalable, and insightful assistant.

## 🎯 Key Features

### 🔐 Role-Based Access Control (RBAC)
- **Finance Team**: Access to financial reports, marketing expenses, equipment costs, reimbursements
- **Marketing Team**: Access to campaign performance data, customer feedback, and sales metrics
- **HR Team**: Access to employee data, attendance records, payroll, and performance reviews
- **Engineering Department**: Access to technical architecture, development processes, and operational guidelines
- **C-Level Executives**: Full access to all company data
- **Employee Level**: Access only to general company information, policies, and FAQs

### 🤖 RAG Capabilities
- **Document Processing**: Handles multiple file formats (Markdown, CSV, TXT)
- **Vector Search**: Semantic search using ChromaDB and sentence transformers
- **Context-Aware Responses**: Google Gemini generates responses based on retrieved context
- **Source Attribution**: All responses include source documents and relevance scores

### 🏗️ Technical Architecture
- **Backend**: FastAPI with JWT authentication
- **Frontend**: Streamlit with modern UI
- **Vector Database**: ChromaDB for document storage and retrieval
- **LLM**: Google Gemini 2.0 Flash for response generation
- **Embeddings**: Sentence Transformers for document vectorization

## 📁 Project Structure

```
ds-rpc-01/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── schemas/
│   │   └── auth.py            # Pydantic models
│   └── services/
│       ├── auth_service.py    # Authentication & authorization
│       ├── document_processor.py # Document loading & processing
│       ├── vector_store.py    # Vector database management
│       └── rag_engine.py      # RAG pipeline implementation
├── resources/
│   └── data/                  # Department documents
│       ├── finance/           # Financial documents
│       ├── marketing/         # Marketing reports
│       ├── hr/               # HR data and policies
│       ├── engineering/      # Technical documentation
│       └── general/          # General company information
├── config.py                 # Configuration and role definitions
├── streamlit_app.py          # Streamlit frontend
├── requirements.txt          # Python dependencies
├── run.py                   # Application launcher
├── env_example.txt          # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ds-rpc-01
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env file with your actual API keys
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## 👥 Demo Users

The system comes with pre-configured demo users for testing:

| Username | Role | Department | Password |
|----------|------|------------|----------|
| Tony | C-Level Executive | Innovation | password123 |
| Peter | Engineering | Engineering | pete123 |
| Sam | Finance | Finance | financepass |
| Bruce | Marketing | Marketing | securepass |
| Sid | Marketing | Marketing | sidpass123 |
| Natasha | HR | HR | hrpass123 |

## 🔧 API Endpoints

### Authentication
- `POST /login` - User login
- `GET /me` - Get current user info

### Query Processing
- `POST /chat` - Process user query
- `GET /department/{department}/summary` - Get department summary

### System Information
- `GET /permissions` - Get user permissions
- `GET /system/stats` - Get system statistics (C-level only)
- `GET /roles` - Get available roles
- `GET /departments` - Get available departments

## 📊 Role Permissions Matrix

| Role | Finance | Marketing | HR | Engineering | General |
|------|---------|-----------|----|-------------|---------|
| Finance Team | Full | Read | Read | None | Read |
| Marketing Team | Read | Full | None | None | Read |
| HR Team | Read | None | Full | None | Read |
| Engineering | None | None | None | Full | Read |
| C-Level | Full | Full | Full | Full | Full |
| Employee | None | None | None | None | Read |

## 🎨 User Interface Features

### Chat Interface
- Real-time chat with the RAG assistant
- Source attribution for all responses
- Role-based access indicators
- Chat history persistence

### Analytics Dashboard (C-Level Only)
- System statistics overview
- Department document distribution
- Role permissions heatmap
- Performance metrics

### Department Summaries
- Quick access to department-specific summaries
- Role-based filtering
- Source document references

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions per department
- **Source Filtering**: Documents filtered based on user permissions
- **Session Management**: Secure session handling in Streamlit

## 📈 Performance Optimization

- **Document Chunking**: Efficient text splitting for better retrieval
- **Vector Caching**: ChromaDB persistence for faster queries
- **Batch Processing**: Efficient document processing pipeline
- **Memory Management**: Optimized for large document collections

## 🛠️ Customization

### Adding New Roles
1. Update `config.py` with new role definition
2. Add role permissions in the `ROLES` dictionary
3. Update system prompts in `SYSTEM_PROMPTS`

### Adding New Departments
1. Create department folder in `resources/data/`
2. Add department mapping in `DEPARTMENT_FOLDERS`
3. Update role permissions for new department

### Customizing LLM
1. Modify `MODEL_NAME` in `config.py`
2. Adjust temperature and max_tokens settings
3. Update system prompts for different roles

## 🐛 Troubleshooting

### Common Issues

1. **Vector store not initializing**
   - Check if ChromaDB directory exists
   - Ensure documents are in correct format
   - Verify file paths in configuration

2. **Authentication errors**
   - Verify JWT secret key
   - Check user credentials in config
   - Ensure proper token format

3. **API connection issues**
   - Verify FastAPI server is running
   - Check CORS settings
   - Ensure proper URL configuration

4. **Google Gemini API errors**
   - Verify your Google API key is valid
   - Check API quota and billing
   - Ensure the model name is correct

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=True
```

## 📝 API Documentation

Once the FastAPI server is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative API Docs**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FinSolve Technologies** for the business case
- **Codebasics** for the challenge framework
- **Google** for the Gemini language model
- **ChromaDB** for vector storage
- **Streamlit** for the web interface

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section

---

**Built with ❤️ for FinSolve Technologies**
#   C o d e b a s i c s _ c h a l l e n g e  
 #   C o d e b a s i c s _ c h a l l e n g e  
 #   C o d e b a s i c s _ c h a l l e n g e  
 