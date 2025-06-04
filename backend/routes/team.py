from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import TeamMembers, Projects, Users

team_bp = Blueprint('team', __name__)

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

