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
    status = db.Column(db.String(50), default='To-Do')  # To-Do, In Progress, Done
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(20), default='Medium')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Urgent



# ------------------ DISCUSSIONS ------------------
class Discussions(db.Model):
    __tablename__ = 'discussions'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    parent_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    replies = db.relationship('Discussions', backref=db.backref('parent', remote_side=[id]), lazy=True)
# ------------------ TASKS ------------------
class Tasks(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='To-Do')  # To-Do, In Progress, Done
    due_date = db.Column(db.Date)

    # 🔥 NEW: Smart prioritization score
    priority_score = db.Column(db.Integer, default=0)  # Lower = more urgent

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
