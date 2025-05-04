# 🧠 Tasks GPT

Tasks GPT is a smart, AI-powered to-do list application that integrates natural language processing with GenAI to help users manage tasks effortlessly. Built with a FastAPI backend and a simple CLI, it allows users to interact using natural commands like “show me all the tasks I didn’t complete” or “add a new task to clean the kitchen.”

### 🚀 Features

✍️ Natural Language Command Interpretation via Gemini AI

✅ CRUD Task Management (Create, Read, Update, Delete)

📅 Due Date & Status Tracking (complete, incomplete, overdue, upcoming)

🔐 User Authentication

🐳 Dockerized FastAPI Backend with PostgreSQL

🌐 Async HTTP Client for efficient API calls

### 🧱 Tech Stack
- Frontend:  Python CLI 

- Backend: FastAPI, SQLAlchemy

- Database: PostgreSQL

- AI Model: Gemini 2.0 Flash (via Google SDK)

- Containerization: Docker, Docker-Compose

- Test: Using Pytest

### 📦 Setup Instructions
1. Clone the repo
```
git clone https://github.com/Elinor-Israeli/tasks-gpt.git
cd tasks-gpt
```
2. Configure environment variables
   
A .env file is a plain text file used to store environment variables — configuration settings your app needs, like API keys, database credentials, and other secrets — in key=value format. You will need to store the Gemini API key that you can get from this [link](https://ai.google.dev/gemini-api/docs/api-key?hl=he "link") in `client/.env` in the format shown below.
> [!CAUTION]
> Do not commit the .env file to GitHub (.env is in .gitignore to prevent it from happening).

```
GENAI_API_KEY=your_api_key
```
3. Run the backend with Docker
```
docker-compose up --build
```
4. Run the CLI
```
cd client
python todo_app.py

```

[comment]: <> (docker run --name my-postgres -e POSTGRES_USER=elinor -e POSTGRES_PASSWORD=elinor123 -e POSTGRES_DB=ToDoApp_DB -p 5432:5432 -d postgres)
[comment]: <> (docker build -t fastapi .)
[comment]: <> (docker run -d -p 8000:8000 fastapi)
