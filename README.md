# 🧠 Tasks GPT

Tasks GPT is a smart, AI-powered task assistant agent  that understands natural language. Say things like  
“remind me to call mom tomorrow” or “show overdue tasks” — and Tasks GPT figures it out using **Gemini AI**.

## 🚀 Features

- ✨ Natural Language Command Parsing (via Gemini 2.0 Flash)
- ✅ Full CRUD Task Management (Create, Read, Update, Delete)
- 📅 Due Date Tracking (overdue, upcoming, complete/incomplete)
- 🔐 User Authentication
- 🧠 Smart AI Editing: Detects what the user wants to edit
- 🔍 Extracts Task Title/ID Automatically from natural phrases
- 🧠 Vector Store + Semantic Search (via Qdrant)
- 🐳 Dockerized Backend + PostgreSQL
- ⚡ Async FastAPI + HTTP Services
- 🧪 CLI-based task management with intelligent fallback flows

## 🧱 Tech Stack
| Layer         | Technology             |
|---------------|------------------------|
| Frontend      | Python CLI             |
| Backend       | FastAPI, SQLAlchemy    |
| Database      | PostgreSQL             |
| AI Model      | Gemini 2.0 Flash (Google SDK) |
| Vector Search | Qdrant (optional)      |
| Container     | Docker, Docker Compose |
| Testing       | Pytest                 |

## 🧬 Architecture Diagrams
### Overall Project Structure (FastAPI, Services & Models)
![TaskGPT UML 2](https://github.com/user-attachments/assets/d71d835c-7ebb-4335-89ef-3cd354b6c195)

###  Request Flow, AI & Vector Search Integration
![TaskGPT UML 1](https://github.com/user-attachments/assets/633f66b8-6362-4fb8-950d-0a0b7c26e8c4)

###  Microservices Architecture
![microservices chart](https://github.com/user-attachments/assets/12fc228e-554b-4db1-a7db-d2f4b1f8aadb)


## 📦 Setup Instructions

### 1. Clone the repo
```
git clone https://github.com/Elinor-Israeli/tasks-gpt.git
cd tasks-gpt
```
### 2. Set Up the Environment
Create a .env file inside the client/ folder:

```
GENAI_API_KEY=your_api_key
```
> [!NOTE]
>🔐 Your .env is already in .gitignore. Never commit it.
>🔑 Get your API key from: [Google Gemini Console](https://ai.google.dev/gemini-api/docs/api-key?hl=he "Google Gemini Console")

### 3. Run the backend with Docker
```
docker-compose up --build
```
This will start:
- The FastAPI app
- A PostgreSQL database
- Qdrant vector store for semantic task similarity
  
### 4. Run the CLI
```
cd client
python cli_client.py

```
## 🛠 Developer Notes
- AI logic lives in genai.py
- Schemas in task_schema.py and user_schema.py
- Request handlers like EditTaskUserRequest live in commands/
- Semantic search handled by TaskVectorStore using Qdrant
- Async services via HttpClient, TaskHttpService, and UserHttpService
 
## 👩‍💻 Author
Built by Elinor Israeli
Exploring the blend of natural language, clean code, and intelligent systems.

[comment]: <> (docker run --name my-postgres -e POSTGRES_USER=elinor -e POSTGRES_PASSWORD=elinor123 -e POSTGRES_DB=ToDoApp_DB -p 5432:5432 -d postgres)
[comment]: <> (docker build -t fastapi .)
[comment]: <> (docker run -d -p 8000:8000 fastapi)
[comment]: <> ($env:PYTHONPATH="C:\Users\Elinor\Desktop\TaskGPT\backend\app" - for testing when import don't work)
