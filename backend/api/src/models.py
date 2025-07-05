"""
SQLAlchemy models for the TaskGPT application.

This module defines the database models for users and tasks,
including their relationships and constraints.
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base
    
class User(Base):
    """
    User model representing application users.
    
    Attributes:
        id: Primary key identifier
        username: Unique username for login
        password: Hashed password for authentication
        tasks: Relationship to user's tasks
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    tasks = relationship("Task", back_populates="user")

class Task(Base):
    """
    Task model representing user tasks.
    
    Attributes:
        id: Primary key identifier
        title: Task title/description
        due_date: Optional due date for the task
        done: Completion status of the task
        user_id: Foreign key to the user who owns this task
        user: Relationship to the task owner
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    due_date = Column(Date)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="tasks")