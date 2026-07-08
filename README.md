# ⚡ Smart Task Manager with AI Productivity Tracker

An intelligent, full-stack task management application that uses **LangChain** and **Google Gemini** to analyze task descriptions, priorities, and deadlines to automatically optimize your daily execution order. It includes interactive visual analytics to track your productivity metrics in real time.

---

## 🚀 Key Features

* **AI-Powered Prioritization Queue:** Uses LangChain + Gemini (`gemini-1.5-flash`) to strategically sort and rank your tasks dynamically based on urgency.
* **AI Sub-Task Breakdown:** Instantly breaks down large, complex milestones into actionable step-by-step checklists with a single click.
* **Interactive Data Visualizations:** A stacked bar chart interface powered by **Recharts** that groups pending vs. completed items across priority tiers.
* **Productivity Tracker:** Real-time completion analytics mapping overall task execution efficiency.
* **Full CRUD Support:** Easily add, complete, and delete entries securely with a persistent relational storage engine.

---

## 🛠️ Tech Stack

### Frontend
* **React.js** (Vite SPA Engine)
* **Recharts** (SVG Data Visualization Layer)
* **Axios** (HTTP Client Wrapper)

### Backend
* **FastAPI** (High-Performance Python Web Framework)
* **LangChain** (AI Agent & Prompt Abstraction Model)
* **Google Gemini API** (`gemini-1.5-flash` LLM Core)
* **SQLAlchemy** (Object-Relational Mapping Framework)
* **MySQL** (Relational Database Storage Engine)

---

## 📁 Project Directory Structure

```text
smart-task-manager/
├── backend/
│   ├── ai_service.py       # LangChain + Gemini Integration Pipeline
│   ├── main.py             # FastAPI REST Routes & SQLAlchemy Models
│   ├── requirement.txt     # Backend Dependencies
│   └── .env                # Local API Keys and DB Credentials (Hidden)
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Dashboard Shell Core View
│   │   └── main.jsx        # App DOM Mount Point
│   ├── vite.config.js      # Dev Server Engine & CORS API Proxy Map
│   └── package.json        # Frontend Dependencies
└── .gitignore              # Global Git Exclusions File
```

---

⚙️ Installation & Local Setup
1. Prerequisites
Make sure you have Node.js, Python 3.8+, and MySQL Server installed on your system.

2. Database Creation
Open MySQL Workbench or your favorite CLI tool and run:

CREATE DATABASE task_db;

3. Backend Setup
Navigate into the backend folder, configure your environment, and spin up the server:

cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  
pip install -r requirement.txt

Create a .env file inside the backend/ directory:

DATABASE_URL=mysql+pymysql://user:password@localhost:3306/task_db
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE

Run the FastAPI application:

python -m uvicorn main:app --reload
The API documentation will now be interactive at http://127.0.0.1:8000/docs

4. Frontend Setup
Open a separate terminal window, move to the frontend repository folder, install packages, and initialize:

cd frontend
npm install
npm run dev
Launch http://localhost:5173 in your browser to explore the running platform!

---

🔒 License
Distributed under the MIT License. See LICENSE for more information.