import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Cleaned up imports at the top
from ai_service import prioritize_tasks_with_ai, breakdown_task_with_ai

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    priority = Column(String(50))
    status = Column(String(50), default="Pending")
    ai_order = Column(Integer, default=0)

# Automatically create table if it doesn't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic validation schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str

# DB Dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).order_by(TaskModel.ai_order.asc(), TaskModel.id.desc()).all()

@app.post("/tasks/optimize")
def optimize_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TaskModel).filter(TaskModel.status == "Pending").all()
    if not tasks:
        raise HTTPException(status_code=400, detail="No pending tasks available to optimize.")
    
    tasks_data = [
        {"id": t.id, "title": t.title, "description": t.description, "deadline": t.deadline, "priority": t.priority} 
        for t in tasks
    ]
    
    ordered_ids = prioritize_tasks_with_ai(tasks_data)
    
    for index, task_id in enumerate(ordered_ids):
        db.query(TaskModel).filter(TaskModel.id == task_id).update({"ai_order": index + 1})
    
    db.commit()
    return {"status": "success", "optimized_order": ordered_ids}

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    db.query(TaskModel).filter(TaskModel.id == task_id).update({"status": "Completed"})
    db.commit()
    return {"status": "success", "message": f"Task {task_id} marked complete"}

@app.post("/tasks/{task_id}/breakdown")
def breakdown_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    sub_tasks = breakdown_task_with_ai(task.title, task.description)
    return {"status": "success", "sub_tasks": sub_tasks}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"status": "success", "message": f"Task {task_id} successfully deleted"}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

b_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(b_dir, "dist")

# Ensure build target folder exists cleanly
os.makedirs(dist_dir, exist_ok=True)

# Endpoint explicitly handling the root browser favicon lookup
@app.get("/taskfavicon.jpg", include_in_schema=False)
async def get_favicon():
    fav_path = os.path.join(dist_dir, "taskfavicon.jpg")
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return HTTPException(status_code=404)

# Mount the entire directory to handle everything else (assets, scripts, layout images)
app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")

# Catch-all route for SPA view reloads
@app.get("/{catchall:path}")
async def serve_frontend(catchall: str):
    return FileResponse(os.path.join(dist_dir, "index.html"))