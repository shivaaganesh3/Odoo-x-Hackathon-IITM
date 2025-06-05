from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Users, Projects, TeamMembers
from datetime import datetime


project_bp = Blueprint('project', __name__)

# ---------- CREATE PROJECT ----------
@project_bp.route("/", methods=["POST"])
@login_required
def create_project():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description", "")

    if not name:
        return jsonify({"error": "Project name is required"}), 400
    
    try:
        # Create project with the current user as creator
        project = Projects(
            name=name,
            description=description,
            created_by=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()

        # Add the creator as a team member
        team_member = TeamMembers(
            user_id=current_user.id,
            project_id=project.id
        )
        db.session.add(team_member)
        db.session.commit()

        return jsonify({
            "message": "Project created successfully", 
            "project_id": project.id,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "created_by": current_user.id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create project: {str(e)}"}), 500

# ---------- GET ALL PROJECTS (User Created + Collaborated) ----------
@project_bp.route("/", methods=["GET"])
@login_required
def get_user_projects():
    try:
        # Get projects where user is a team member
        user_team_memberships = TeamMembers.query.filter_by(user_id=current_user.id).all()
        project_ids = [membership.project_id for membership in user_team_memberships]
        
        # Get all projects for these IDs
        projects = Projects.query.filter(Projects.id.in_(project_ids)).all()
        
        results = []
        for project in projects:
            results.append({
                "id": project.id,
                "name": project.name,
                "description": project.description or "",
                "created_at": project.created_at.isoformat(),
                "is_owner": project.created_by == current_user.id
            })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch projects: {str(e)}"}), 500

# ---------- UPDATE PROJECT ----------
@project_bp.route("/<int:project_id>", methods=["PUT"])
@login_required
def update_project(project_id):
    try:
        # Find project and check ownership
        project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
        if not project:
            return jsonify({"error": "Project not found or unauthorized"}), 404

        data = request.get_json()
        project.name = data.get("name", project.name)
        project.description = data.get("description", project.description)
        
        db.session.commit()

        return jsonify({"message": "Project updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update project: {str(e)}"}), 500

# ---------- DELETE PROJECT ----------
@project_bp.route("/<int:project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id):
    try:
        # Find project and check ownership
        project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
        if not project:
            return jsonify({"error": "Project not found or unauthorized"}), 404

        # Delete associated team members first
        TeamMembers.query.filter_by(project_id=project_id).delete()
        
        # Delete the project
        db.session.delete(project)
        db.session.commit()

        return jsonify({"message": "Project deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete project: {str(e)}"}), 500



