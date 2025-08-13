from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False)
    role = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    deadline = Column(DateTime, nullable=True)
    priority = Column(String(16), nullable=True)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(64), index=True, nullable=False)
    workflow_name = Column(String(128), nullable=False)
    execution_status = Column(String(32), nullable=False)
    execution_details = Column(Text, nullable=True)
    executed_at = Column(DateTime, server_default=func.now(), nullable=False)

