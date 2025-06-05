from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import TeamMembers, Projects, Users

team_bp = Blueprint('team', __name__)

# ---------- GET ALL TEAMS (PROJECTS) FOR CURRENT USER ----------
@team_bp.route("/", methods=["GET"])
@login_required
def get_all_teams():
    # Get projects owned by current user
    owned_projects = Projects.query.filter_by(created_by=current_user.id).all()
    
    # Get projects where current user is a team member
    team_memberships = TeamMembers.query.filter_by(user_id=current_user.id).all()
    member_project_ids = [tm.project_id for tm in team_memberships]
    member_projects = Projects.query.filter(Projects.id.in_(member_project_ids)).all() if member_project_ids else []
    
    # Combine and deduplicate projects
    all_projects = {}
    
    # Add owned projects
    for project in owned_projects:
        team_members = TeamMembers.query.filter_by(project_id=project.id).all()
        member_list = []
        for tm in team_members:
            user = Users.query.get(tm.user_id)
            if user:
                member_list.append({
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                })
        
        all_projects[project.id] = {
            "team_id": project.id,
            "team_name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat(),
            "is_owner": True,
            "member_count": len(member_list),
            "members": member_list
        }
    
    # Add member projects (if not already added as owner)
    for project in member_projects:
        if project.id not in all_projects:
            team_members = TeamMembers.query.filter_by(project_id=project.id).all()
            member_list = []
            for tm in team_members:
                user = Users.query.get(tm.user_id)
                if user:
                    member_list.append({
                        "id": user.id,
                        "email": user.email,
                        "name": user.name
                    })
            
            all_projects[project.id] = {
                "team_id": project.id,
                "team_name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "is_owner": False,
                "member_count": len(member_list),
                "members": member_list
            }
    
    return jsonify(list(all_projects.values())), 200

# ---------- ADD USER TO PROJECT TEAM BY EMAIL ----------
@team_bp.route("/add-by-email", methods=["POST"])
@login_required
def add_team_member_by_email():
    data = request.get_json()
    project_id = data.get("project_id")
    user_email = data.get("user_email")
    
    if not project_id or not user_email:
        return jsonify({"error": "Project ID and user email are required"}), 400

    # Check project ownership
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by you"}), 403

    # Find user by email
    user = Users.query.filter_by(email=user_email.lower().strip()).first()
    if not user:
        return jsonify({"error": "User with this email not found"}), 404

    # Check if already on team
    existing = TeamMembers.query.filter_by(project_id=project_id, user_id=user.id).first()
    if existing:
        return jsonify({"message": "User is already part of the team"}), 200

    # Add user to team
    member = TeamMembers(user_id=user.id, project_id=project_id)
    db.session.add(member)
    db.session.commit()

    return jsonify({
        "message": "User added to project team",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }), 201

# ---------- ADD USER TO PROJECT TEAM ----------
@team_bp.route("/add", methods=["POST"])
@login_required
def add_team_member():
    data = request.get_json()
    project_id = data.get("project_id")
    user_id = data.get("user_id")
    

    # Check project ownership
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by you"}), 403

    # Check user exists
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if already on team
    existing = TeamMembers.query.filter_by(project_id=project_id, user_id=user_id).first()
    if existing:
        return jsonify({"message": "User is already part of the team"}), 200

    member = TeamMembers(user_id=user_id, project_id=project_id)
    db.session.add(member)
    db.session.commit()

    return jsonify({"message": "User added to project team"}), 201

# ---------- GET TEAM MEMBERS FOR A PROJECT ----------
@team_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_team_members(project_id):
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by you"}), 403

    members = TeamMembers.query.filter_by(project_id=project_id).all()
    users = []
    for m in members:
        user = Users.query.get(m.user_id)
        if user:
            users.append({
                "id": user.id,
                "email": user.email,
                "name": user.name
            })

    return jsonify(users), 200

# ---------- REMOVE USER FROM PROJECT TEAM ----------
@team_bp.route("/remove", methods=["POST"])
@login_required
def remove_team_member():
    data = request.get_json()
    project_id = data.get("project_id")
    user_id = data.get("user_id")
    
    if not project_id or not user_id:
        return jsonify({"error": "Project ID and user ID are required"}), 400

    # Check project ownership
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by you"}), 403

    # Find team member
    member = TeamMembers.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        return jsonify({"error": "User is not a member of this team"}), 404

    # Remove from team
    db.session.delete(member)
    db.session.commit()

    return jsonify({"message": "User removed from project team"}), 200

