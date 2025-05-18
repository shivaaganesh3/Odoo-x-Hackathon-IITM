from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum, Table
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# Enum for task priority
class PriorityEnum(enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

# Association table for many-to-many between Task and Tag
task_tags = Table(
    'task_tags', Base.metadata,
    Column('task_id', ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)
project_tags = Table(
    'project_tags', Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)
project_collaborators = Table(
    'project_collaborators', Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)

    projects = relationship("Project", back_populates="owner")
    collaborations = relationship("Project", secondary=project_collaborators, back_populates="collaborators")
    assigned_tasks = relationship("Task", back_populates="assignee")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    image = Column(String)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="projects")
    collaborators = relationship("User", secondary=project_collaborators, back_populates="collaborations")
    tasks = relationship("Task", back_populates="project")
    tags = relationship("Tag", secondary=project_tags, back_populates="projects")


class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    assignee_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))
    image = Column(String)
    description = Column(Text)
    deadline = Column(DateTime)
    priority = Column(Enum(PriorityEnum))

    assignee = relationship("User", back_populates="assigned_tasks")
    project = relationship("Project", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    tasks = relationship("Task", secondary=task_tags, back_populates="tags")
    projects = relationship("Project", secondary=project_tags, back_populates="tags")