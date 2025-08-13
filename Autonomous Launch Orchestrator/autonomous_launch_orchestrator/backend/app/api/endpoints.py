import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from functools import lru_cache
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.db.models import Task, ExecutionLog
from backend.app.core.agents import PlannerAgent, RoleAgent
from backend.app.core.n8n_integration import N8NIntegration

router = APIRouter()

class PlanRequest(BaseModel):
    goal: Optional[str] = None
    message: Optional[str] = None

@lru_cache(maxsize=1)
def get_planner_agent():
    return PlannerAgent()

@lru_cache(maxsize=1)
def get_n8n_integration():
    return N8NIntegration(os.getenv("N8N_BASE_URL", "http://localhost:5678"))

def _normalize_tasks(tasks_raw: Any, target: str) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    if isinstance(tasks_raw, list):
        for t in tasks_raw:
            if isinstance(t, dict):
                tasks.append(t)
            else:
                tasks.append({"title": "Task", "role": "General", "description": str(t)})
    elif isinstance(tasks_raw, dict):
        tasks = [tasks_raw]
    elif tasks_raw is not None:
        tasks = [{"title": "Task", "role": "General", "description": str(tasks_raw)}]
    if not tasks:
        tasks = [
            {"title": "Define launch objectives", "role": "Product Manager", "description": f"Clarify goals for: {target}"},
            {"title": "Prepare marketing plan", "role": "Marketing", "description": "Channels, budget, timeline"},
            {"title": "Set up analytics", "role": "Data", "description": "Dashboards and tracking"},
        ]
    return tasks

@router.post("/create-plan")
async def create_launch_plan(payload: Optional[PlanRequest] = None, goal: Optional[str] = None, db: Session = Depends(get_db)):
    """Create a launch plan; accepts ?goal=... or JSON {goal|message}. Saves tasks to DB and returns them."""
    target = (payload.goal if payload else None) or (payload.message if payload else None) or goal
    if not target:
        raise HTTPException(status_code=400, detail="Provide 'goal' or 'message'")

    # Try planner, but fall back silently so the UI works without LLM
    tasks_raw = None
    try:
        tasks_raw = get_planner_agent().create_launch_plan(target)
    except Exception:
        tasks_raw = None

    tasks_norm = _normalize_tasks(tasks_raw, target)

    # Persist tasks
    saved = []
    now = datetime.utcnow()
    try:
        for idx, t in enumerate(tasks_norm, start=1):
            role = t.get("role") or "General"
            desc = t.get("description") or t.get("text") or t.get("title") or "Task"
            deadline = None
            if t.get("deadline"):
                try:
                    deadline = datetime.fromisoformat(t["deadline"])
                except Exception:
                    deadline = None
            priority = t.get("priority") or "medium"
            status = "pending"

            task = Task(
                task_id=f"TASK-{int(now.timestamp())}-{idx}",
                role=role,
                description=str(desc),
                deadline=deadline,
                priority=priority,
                status=status,
                created_at=now,
                updated_at=now,
            )
            db.add(task)
            db.flush()  # get PK
            saved.append({
                "id": task.id,
                "task_id": task.task_id,
                "role": task.role,
                "description": task.description,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at.isoformat() if task.created_at else None
            })
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save tasks: {e}")

    # Frontend expects top-level "message" and "tasks"
    return {
        "message": "Plan created",
        "tasks": saved
    }

@router.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return [
        {
            "id": task.id,
            "task_id": task.task_id,
            "role": task.role,
            "description": task.description,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "priority": task.priority,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None
        }
        for task in tasks
    ]

@router.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    now = datetime.utcnow()
    task.status = "approved"
    task.updated_at = now

    exec_status = "failed"
    exec_details: Dict[str, Any] = {}
    content = None
    workflow_name = "unknown"

    try:
        role_agent = RoleAgent(task.role)
        content = role_agent.generate_content(task.description)
    except Exception as e:
        exec_details["role_agent_error"] = str(e)

    try:
        role_key = (task.role or "general").strip().lower()
        workflow_name = get_n8n_integration().map_task_to_workflow(role_key, "default")
        result = get_n8n_integration().trigger_workflow(workflow_name, {
            "task_id": task.task_id,
            "role": task.role,
            "description": task.description,
            "content": content
        })
        exec_details["n8n_result"] = result
        exec_status = "success" if result.get("status") == "success" else "failed"
    except Exception as e:
        exec_details["n8n_error"] = str(e)

    log = ExecutionLog(
        task_id=task.task_id,
        workflow_name=str(workflow_name),
        execution_status=exec_status,
        execution_details=str(exec_details),
        executed_at=now,
    )
    db.add(log)
    task.status = "completed" if exec_status == "success" else "failed"
    db.commit()

    return {
        "status": "success",
        "message": f"Task {task_id} approved and executed",
        "execution_result": {"status": exec_status, "details": exec_details}
    }

@router.post("/tasks/{task_id}/reject")
async def reject_task(task_id: str, db: Session = Depends(get_db)):
    """Reject a task"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "rejected"
    task.updated_at = datetime.now()
    db.commit()
    
    return {
        "status": "success",
        "message": f"Task {task_id} rejected"
    }

@router.get("/logs")
async def get_execution_logs(db: Session = Depends(get_db)):
    """Get execution logs"""
    logs = db.query(ExecutionLog).order_by(ExecutionLog.executed_at.desc()).all()
    return [
        {
            "id": log.id,
            "task_id": log.task_id,
            "workflow_name": log.workflow_name,
            "execution_status": log.execution_status,
            "execution_details": log.execution_details,
            "executed_at": log.executed_at.isoformat() if log.executed_at else None
        }
        for log in logs
    ]

# Optional: test a webhook directly via backend
@router.post("/n8n/test")
async def n8n_test(payload: Dict[str, Any]):
    """Body: { "workflow": "<full URL or slug>", "data": {..} }"""
    workflow = payload.get("workflow")
    data = payload.get("data", {"ping": "pong"})
    if not workflow:
        raise HTTPException(status_code=400, detail="workflow is required")
    result = get_n8n_integration().trigger_workflow(workflow, data)
    status_code = 200 if result.get("status") == "success" else 502
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result)
    return result

