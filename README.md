# FinSolve RAG Assistant - Role-Based Access Control System

## 🏢 Overview

This project implements a **Retrieval-Augmented Generation (RAG) chatbot** for FinSolve Technologies, providing role-based access to department-specific insights. The system uses FastAPI, ChromaDB, Google Gemini, and Streamlit for a secure, scalable, and insightful assistant.

## 🎯 Key Features

### 🔐 Role-Based Access Control (RBAC)
Key aspects of the Role-Based Access Control system include:
- **Finance Team**: Access to financial reports, marketing expenses, equipment costs, reimbursements
- **Marketing Team**: Access to campaign performance data, customer feedback, and sales metrics
- **HR Team**: Access to employee data, attendance records, payroll, and performance reviews
- **Engineering Department**: Access to technical architecture, development processes, and operational guidelines
- **C-Level Executives**: Full access to all company data
- **Employee Level**: Access only to general company information, policies, and FAQs

### 🤖 RAG Capabilities
The RAG pipeline incorporates the following capabilities:
- **Document Processing**: Handles multiple file formats (Markdown, CSV, TXT)
- **Vector Search**: Semantic search using ChromaDB and sentence transformers
- **Context-Aware Responses**: Google Gemini generates responses based on retrieved context
- **Source Attribution**: All responses include source documents and relevance scores

### 🏗️ Technical Architecture
The system is built upon the following technical components:
- **Backend**: FastAPI with JWT authentication
- **Frontend**: Streamlit with modern UI
- **Vector Database**: ChromaDB for document storage and retrieval
- **LLM**: Google Gemini 2.0 Flash for response generation
- **Embeddings**: Sentence Transformers for document vectorization

## 📁 Project Structure