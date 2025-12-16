# 🤖 Physical AI & Humanoid Robotics Textbook  
### An Interactive Robotics Learning Platform with RAG Chatbot

This project is a complete **educational platform** built around the book  
**“Physical AI & Humanoid Robotics — Essentials”**.

It combines a **modern documentation website**, an **AI-powered RAG chatbot**,  
**personalized learning**, **content translation**, and **secure authentication**  
to deliver an advanced learning experience for robotics and AI students.

---

## 🚀 Project Overview

This platform allows users to:

- Read a structured **8-chapter robotics textbook**
- Ask questions from the book using an **AI RAG Chatbot**
- Get answers based on **full chapters or selected text**
- **Personalize** content based on their background
- **Translate** chapters into Urdu
- Securely **Sign up and Sign in** using modern authentication

---

## 📚 Chapters Covered

1. Introduction to Physical AI  
2. Basics of Humanoid Robotics  
3. AI and Control Systems for Humanoids  
4. Digital Twin Simulation  
5. ROS 2 Fundamentals  
6. Capstone – Simple AI-Robot Pipeline  
7. Vision-Language-Action (VLA) Systems  
8. Ethical and Future Implications  

---

## 🖥️ Frontend (Website)

**Technology Used:**
- Docusaurus (React-based documentation framework)
- TypeScript
- Custom CSS (Robotics-themed UI)
- Responsive and fast-loading design

**Frontend Features:**
- Modern **hero section** with robotics visuals
- Interactive **Table of Contents**
- Chapter-wise navigation
- Embedded **chatbot widget**
- Content personalization buttons
- Urdu translation toggle
- Clean header and footer layout

---

## ⚙️ Backend (API)

**Technology Used:**
- FastAPI
- OpenAI Agents / ChatKit SDK
- Python 3.11+

**Backend Responsibilities:**
- Handle chatbot queries
- Perform document retrieval
- Connect frontend with AI services
- Manage personalization logic
- Serve REST APIs for Q&A

---

## 🗄️ Database & Vector Store

### Relational Database
- **Neon Serverless PostgreSQL**
- SQLModel ORM

Used for:
- User profiles
- Authentication data
- Personalization preferences

### Vector Database
- **Qdrant (Cloud – Free Tier)**

Used for:
- Storing book embeddings
- Semantic search
- Retrieval-Augmented Generation (RAG)

---

## 🧠 RAG Chatbot System

**What the Chatbot Can Do:**
- Answer questions **only from the book**
- Answer based on **user-selected text**
- Cite relevant content internally
- Fall back to OpenAI if question is out-of-scope
- Personalize responses based on user background

**Tech Stack:**
- OpenAI (LLMs + Embeddings)
- Qdrant Client
- FastAPI
- OpenAI Agents SDK

---

## 🌐 Translation System

- One-click **Urdu translation** for each chapter
- Powered by LLM-based translation
- Keeps technical meaning intact
- Helps non-English learners understand robotics concepts

---

## 🎯 Personalization System

During signup, users are asked about:
- Software background
- Hardware/robotics experience

Based on this:
- Content explanations are simplified or advanced
- Chatbot answers adapt to user level
- Learning becomes more effective

---

## 🔐 Authentication

- Implemented using **Better Auth**
- Secure Signup & Signin
- User session management
- Required for personalization and bonus features

---

## 📦 How to Clone the Repository


git clone <your-repository-url>
cd Physical-AI-Humanoid-Robotics-Essentials


# 🔑 Environment Variables (.env)

Create a .env file in the backend root directory:

**OpenAI**
OPENAI_API_KEY=your_openai_api_key

**Qdrant**
QDRANT_URL=https://your-qdrant-cluster-url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=robotics_book_collection

**Database (Neon)**
DATABASE_URL=postgresql+psycopg://username:password@host/dbname

**Authentication**
BETTER_AUTH_SECRET=your_secret_key

# ▶️ Running the Backend
pip install -r requirements.txt
uvicorn src.main:app --reload


**Backend will run at:**
http://localhost:8000


**API Documentation**
http://localhost:8000/docs

# ▶️ Running the Frontend

yarn install
yarn start

Or

npm install
npm start

**Frontend will run at:**
http://localhost:3000