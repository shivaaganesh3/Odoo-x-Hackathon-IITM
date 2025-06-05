from flask import Blueprint, request, jsonify
from flask_security.utils import hash_password, verify_password, login_user, logout_user
from flask_security import current_user
from models import Users
from database import db
from flask_security import SQLAlchemyUserDatastore
from models import Users, Roles
from flask_security import login_required, current_user

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
    
    print(f"DEBUG: User found: {user.email}, checking password...")
    
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
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from database import User, Project, Task
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime, date
    
    # Create connection to the main app database
    engine = create_engine('sqlite:///taskmanager.db')
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()
    
    try:
        # Find the user in the app database by email (since emails should match)
        user = db_session.query(User).filter_by(email=current_user.email).first()
        
        if not user:
            return jsonify({
                "total_projects": 0,
                "active_tasks": 0,
                "team_members": 0,
                "overdue_tasks": 0
            }), 200
        
        # Total Projects (owned + collaborated)
        owned_projects = db_session.query(Project).filter_by(owner_id=user.id).count()
        collaborated_projects = len(user.collaborations)
        total_projects = owned_projects + collaborated_projects
        
        # Active Tasks (assigned to user)
        active_tasks = db_session.query(Task).filter_by(assignee_id=user.id).count()
        
        # Team Members (unique collaborators across all owned projects)
        team_members = set()
        for project in user.projects:
            for collaborator in project.collaborators:
                team_members.add(collaborator.id)
        team_members_count = len(team_members)
        
        # Overdue Tasks (assigned to user, past deadline)
        today = date.today()
        overdue_tasks = db_session.query(Task).filter(
            Task.assignee_id == user.id,
            Task.deadline < today
        ).count()
        
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
    finally:
        db_session.close()

# ---------- RECENT PROJECTS ----------
@auth_bp.route('/recent-projects', methods=['GET'])
@login_required
def get_recent_projects():
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from database import User, Project
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create connection to the main app database
    engine = create_engine('sqlite:///taskmanager.db')
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()
    
    try:
        # Find the user in the app database by email
        user = db_session.query(User).filter_by(email=current_user.email).first()
        
        if not user:
            return jsonify([]), 200
        
        # Get user's projects (owned + collaborated), limit to 5 most recent
        owned_projects = db_session.query(Project).filter_by(owner_id=user.id).all()
        all_projects = owned_projects + list(user.collaborations)
        
        # Sort by creation date and limit to 5
        recent_projects = sorted(all_projects, key=lambda x: x.id, reverse=True)[:5]
        
        projects_data = []
        for project in recent_projects:
            projects_data.append({
                "id": project.id,
                "name": project.name,
                "description": project.description or "",
                "priority": project.priority.value if project.priority else "MEDIUM",
                "created_at": datetime.now().isoformat(),
                "image": project.image
            })
        
        return jsonify(projects_data), 200
        
    except Exception as e:
        print(f"Error fetching recent projects: {e}")
        return jsonify([]), 200
    finally:
        db_session.close()

