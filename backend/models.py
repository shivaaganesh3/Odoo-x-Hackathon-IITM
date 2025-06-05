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


# ------------------ DISCUSSIONS ------------------
class Discussions(db.Model):
    __tablename__ = 'discussions'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    parent_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)  # Optional task reference

    replies = db.relationship('Discussions', backref=db.backref('parent', remote_side=[id]), lazy=True)
    task = db.relationship('Tasks', backref='discussions', lazy=True)  # Add relationship to Tasks


# ------------------ NOTIFICATIONS ------------------
class Notifications(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'deadline_warning', 'task_overdue', 'general'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional references for context
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # Priority level for notifications
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    
    # For deadline warnings - when to trigger again
    next_reminder_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('Users', backref='notifications', lazy=True)
    task = db.relationship('Tasks', backref='notifications', lazy=True)
    project = db.relationship('Projects', backref='notifications', lazy=True)


# ------------------ BUDGET ------------------
class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    project = db.relationship('Projects', backref='budgets')
    task = db.relationship('Tasks', backref='budgets')
    creator = db.relationship('Users', backref='created_budgets')

    def __repr__(self):
        return f'<Budget {self.id}: {self.amount}>'


# ------------------ EXPENSE CATEGORIES ------------------
class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'


# ------------------ EXPENSES ------------------
class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    receipt_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    project = db.relationship('Projects', backref='expenses')
    task = db.relationship('Tasks', backref='expenses')
    category = db.relationship('ExpenseCategory', backref='expenses')
    creator = db.relationship('Users', backref='created_expenses')

    def __repr__(self):
        return f'<Expense {self.id}: {self.amount}>'
