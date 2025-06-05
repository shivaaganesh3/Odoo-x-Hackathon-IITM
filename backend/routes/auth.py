from flask import Blueprint, request, jsonify
from flask_security.utils import hash_password, verify_password, login_user, logout_user
from flask_security import current_user
from models import Users, Projects, Tasks
from database import db
from flask_security import SQLAlchemyUserDatastore
from models import Users, Roles
from flask_security import login_required, current_user
from datetime import datetime, date

auth_bp = Blueprint('auth', __name__)

# Setup UserDatastore
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)

# ---------- REGISTER ----------
@auth_bp.route('/register', methods=['POST'])
def register_user():
    from uuid import uuid4

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        name=name,
        fs_uniquifier=str(uuid4())
    )
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201

# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    print(f"DEBUG: Login attempt for email: {email}")
    
    user = Users.query.filter_by(email=email).first()
    
    if not user:
        print(f"DEBUG: No user found with email: {email}")
        return jsonify({"error": "Invalid email or password"}), 401
    
    print(f"DEBUG: User found: ID={user.id}, Email={user.email}")
    print(f"DEBUG: Password hash: {user.password[:50]}...")
    
    # Check if password hash has proper format
    if not user.password or user.password.count('$') < 2:
        print(f"DEBUG: Invalid password hash format for user: {email}")
        return jsonify({"error": "Invalid email or password"}), 401
    
    try:
        if verify_password(password, user.password):
            print(f"DEBUG: Password verification successful for user: {email}")
            login_user(user)
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }), 200
        else:
            print(f"DEBUG: Password verification failed for user: {email}")
    except Exception as e:
        print(f"DEBUG: Password verification error: {e}")
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"error": "Invalid email or password"}), 401

# DEBUG: Check users in database
@auth_bp.route('/debug/users', methods=['GET'])
def debug_users():
    users = Users.query.all()
    users_info = [{
        "id": user.id,
        "email": user.email,
        "name": user.name
    } for user in users]
    return jsonify({
        "total_users": len(users),
        "users": users_info
    }), 200

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }), 200

@auth_bp.route("/whoami", methods=["GET"])
@login_required
def whoami():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    })

# ---------- LOGOUT ----------
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

# ---------- DASHBOARD STATS ----------
@auth_bp.route('/dashboard-stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    try:
        # Total Projects created by the current user
        total_projects = Projects.query.filter_by(created_by=current_user.id).count()
        
        # Active Tasks assigned to the current user
        active_tasks = Tasks.query.filter_by(assigned_to=current_user.id).count()
        
        # Team Members (count unique team members across user's projects)
        from models import TeamMembers
        user_projects = Projects.query.filter_by(created_by=current_user.id).all()
        team_members = set()
        for project in user_projects:
            project_members = TeamMembers.query.filter_by(project_id=project.id).all()
            for member in project_members:
                team_members.add(member.user_id)
        team_members_count = len(team_members)
        
        # Overdue Tasks assigned to current user
        today = date.today()
        overdue_tasks = Tasks.query.filter(
            Tasks.assigned_to == current_user.id,
            Tasks.due_date < today
        ).count() if Tasks.query.filter_by(assigned_to=current_user.id).first() else 0
        
        return jsonify({
            "total_projects": total_projects,
            "active_tasks": active_tasks,
            "team_members": team_members_count,
            "overdue_tasks": overdue_tasks
        }), 200
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({
            "total_projects": 0,
            "active_tasks": 0,
            "team_members": 0,
            "overdue_tasks": 0
        }), 200

# ---------- RECENT PROJECTS ----------
@auth_bp.route('/recent-projects', methods=['GET'])
@login_required
def get_recent_projects():
    try:
        # Get recent projects created by current user
        recent_projects = Projects.query.filter_by(created_by=current_user.id)\
                                       .order_by(Projects.created_at.desc())\
                                       .limit(5).all()
        
        projects_data = []
        for project in recent_projects:
            # Count tasks for this project
            task_count = Tasks.query.filter_by(project_id=project.id).count()
            
            projects_data.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "task_count": task_count
            })
        
        return jsonify(projects_data), 200
        
    except Exception as e:
        print(f"Error fetching recent projects: {e}")
        return jsonify([]), 200

