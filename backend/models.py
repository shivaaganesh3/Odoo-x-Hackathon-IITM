from database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

# ------------------ ROLES ------------------
class Roles(db.Model, RoleMixin):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


# ------------------ USERS ------------------
class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=True)

    name = db.Column(db.String(100))

    # Role-based access
    roles = db.relationship('Roles', secondary='user_roles')

    # Relationships
    assigned_tasks = db.relationship('Tasks', backref='assignee', lazy=True)
    discussions = db.relationship('Discussions', backref='author', lazy=True)


# ------------------ USER-ROLE LINK TABLE ------------------
class UserRoles(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


# ------------------ PROJECTS ------------------
class Projects(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    tasks = db.relationship('Tasks', backref='project', lazy=True)
    team_members = db.relationship('TeamMembers', backref='project', lazy=True)
    discussions = db.relationship('Discussions', backref='project', lazy=True)
    custom_statuses = db.relationship('CustomStatus', backref='project', lazy=True, cascade='all, delete-orphan')


# ------------------ CUSTOM STATUS ------------------
class CustomStatus(db.Model):
    __tablename__ = 'custom_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6B7280')  # Hex color code
    position = db.Column(db.Integer, default=0)  # For ordering statuses
    is_default = db.Column(db.Boolean, default=False)  # Mark default status for new tasks
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Tasks', backref='custom_status', lazy=True)

    # Unique constraint: status name must be unique per project
    __table_args__ = (db.UniqueConstraint('name', 'project_id', name='unique_status_per_project'),)


# ------------------ TEAM MEMBERS ------------------
class TeamMembers(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)


# ------------------ TASKS ------------------
class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    
    # Updated to reference custom status instead of hardcoded string
    status_id = db.Column(db.Integer, db.ForeignKey('custom_status.id'), nullable=True)
    
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Urgent
    priority_score = db.Column(db.Float, default=0.0)  # Smart calculated priority score
    
    # Smart Task Prioritization Engine fields
    effort_score = db.Column(db.Integer, default=3)  # 1=Very Easy, 2=Easy, 3=Medium, 4=Hard, 5=Very Hard
    impact_score = db.Column(db.Integer, default=3)  # 1=Low, 2=Medium-Low, 3=Medium, 4=High, 5=Critical
    dependency_map = db.Column(db.JSON, default=list)  # List of task IDs that depend on this task
    blocked_by = db.Column(db.JSON, default=list)  # List of task IDs that block this task
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to discussions/comments
    discussions = db.relationship('Discussions', backref='task', lazy=True)


# ------------------ DISCUSSIONS ------------------
class Discussions(db.Model):
    __tablename__ = 'discussions'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    parent_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)

    replies = db.relationship('Discussions', backref=db.backref('parent', remote_side=[id]), lazy=True)
