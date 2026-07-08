import os
import sys
import jwt
from datetime import datetime, timedelta
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

# Fix absolute path lookup for local modules like ai_service
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# AI imports from local directory
from ai_service import prioritize_tasks_with_ai, breakdown_task_with_ai

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- DATABASE MODELS ---

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    priority = Column(String(50))
    status = Column(String(50), default="Pending")
    ai_order = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


# --- TEMPORARY WIPE AND CREATE INITIALIZATION ---
# Base.metadata.drop_all(bind=engine) # Keeping this commented out as we planned
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Smart Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- VALIDATION SCHEMAS ---

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str

class UserAuth(BaseModel):
    username: str
    password: str


# --- DATABASE DEPENDENCY ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- SECURITY & CONFIGURATIONS ---

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pw(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_pw(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=1)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(db: Session = Depends(get_db), token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        if uid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(UserModel).filter(UserModel.id == uid).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# --- AUTHENTICATION ENDPOINTS ---

@app.post("/register")
def register(user: UserAuth, db: Session = Depends(get_db)):
    exists = db.query(UserModel).filter(UserModel.username == user.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = UserModel(username=user.username, hashed_password=hash_pw(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User registered successfully"}

@app.post("/login")
def login(user: UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if not db_user or not verify_pw(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = create_token({"sub": db_user.id})
    return {"status": "success", "token": token, "username": db_user.username}


# --- USER ROUTE ENDPOINTS (TASKS ISOLATED PER USER) ---

@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_task = TaskModel(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return db.query(TaskModel).filter(TaskModel.user_id == current_user.id).order_by(TaskModel.ai_order.asc(), TaskModel.id.desc()).all()

@app.post("/tasks/optimize")
def optimize_tasks(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    tasks = db.query(TaskModel).filter(TaskModel.user_id == current_user.id, TaskModel.status == "Pending").all()
    if not tasks:
        raise HTTPException(status_code=400, detail="No pending tasks available to optimize.")
    
    tasks_data = [
        {"id": t.id, "title": t.title, "description": t.description, "deadline": t.deadline, "priority": t.priority} 
        for t in tasks
    ]
    
    ordered_ids = prioritize_tasks_with_ai(tasks_data)
    
    for index, task_id in enumerate(ordered_ids):
        db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).update({"ai_order": index + 1})
    
    db.commit()
    return {"status": "success", "optimized_order": ordered_ids}

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = "Completed"
    db.commit()
    return {"status": "success", "message": f"Task {task_id} marked complete"}

@app.post("/tasks/{task_id}/breakdown")
def breakdown_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    sub_tasks = breakdown_task_with_ai(task.title, task.description)
    return {"status": "success", "sub_tasks": sub_tasks}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"status": "success", "message": f"Task {task_id} successfully deleted"}


# --- FRONTEND ROUTING BLOCK ---
dist_dir = os.path.join(current_dir, "dist")

os.makedirs(dist_dir, exist_ok=True)

@app.get("/taskfavicon.jpg", include_in_schema=False)
async def get_favicon():
    fav_path = os.path.join(dist_dir, "taskfavicon.jpg")
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    raise HTTPException(status_code=404, detail="Favicon missing")

assets_dir = os.path.join(dist_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/{catchall:path}")
async def serve_frontend(catchall: str):
    if catchall.startswith("tasks") or catchall.startswith("register") or catchall.startswith("login"):
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    if "taskfavicon.jpg" in catchall:
        fav_path = os.path.join(dist_dir, "taskfavicon.jpg")
        if os.path.exists(fav_path):
            return FileResponse(fav_path)

    index_path = os.path.join(dist_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    raise HTTPException(status_code=404, detail="Frontend build missing")