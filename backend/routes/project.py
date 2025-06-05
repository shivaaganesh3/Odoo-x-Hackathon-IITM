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
    print(f"DEBUG: Project creation attempt by user: {current_user.email if current_user.is_authenticated else 'Not authenticated'}")
    print(f"DEBUG: User authenticated: {current_user.is_authenticated}")
    print(f"DEBUG: Current user ID: {current_user.id if current_user.is_authenticated else 'None'}")
    # Handle both JSON and form data (for file uploads)
    if request.is_json:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description", "")
        priority = data.get("priority", "MEDIUM")
        deadline = data.get("deadline")
        tags = data.get("tags", "")
        image_file = None
    else:
        # Form data (multipart/form-data)
        name = request.form.get("name")
        description = request.form.get("description", "")
        priority = request.form.get("priority", "MEDIUM")
        deadline = request.form.get("deadline")
        tags = request.form.get("tags", "")
        image_file = request.files.get("image")

    if not name:
        return jsonify({"error": "Project name is required"}), 400
    
    try:
        # Handle image upload if present
        image_path = None
        if image_file and image_file.filename:
            # For now, we'll just log that an image was uploaded
            # In a production app, you'd save this to a file storage service
            print(f"DEBUG: Image uploaded: {image_file.filename}")
            image_path = f"uploads/{image_file.filename}"  # Placeholder path
        
        # Create project with the current user as creator
        project = Projects(
            name=name.strip(),
            description=description.strip() if description else "",
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

        print(f"DEBUG: Project created successfully - ID: {project.id}, Name: {project.name}")

        return jsonify({
            "message": "Project created successfully", 
            "project_id": project.id,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "created_by": current_user.id,
                "priority": priority,
                "deadline": deadline,
                "tags": tags,
                "image_path": image_path
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error creating project: {str(e)}")
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

# ---------- GET PROJECT DETAILS ----------
@project_bp.route("/<int:project_id>", methods=["GET"])
@login_required
def get_project_details(project_id):
    try:
        # Check if user is a team member of this project
        team_membership = TeamMembers.query.filter_by(
            project_id=project_id, 
            user_id=current_user.id
        ).first()
        
        if not team_membership:
            return jsonify({"error": "Project not found or unauthorized"}), 404

        # Get project details
        project = Projects.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Get team members
        team_members = db.session.query(Users).join(TeamMembers).filter(
            TeamMembers.project_id == project_id
        ).all()

        # Get project owner details
        owner = Users.query.get(project.created_by)

        return jsonify({
            "id": project.id,
            "name": project.name,
            "description": project.description or "",
            "created_at": project.created_at.isoformat(),
            "created_by": project.created_by,
            "owner": {
                "id": owner.id,
                "name": owner.name,
                "email": owner.email
            } if owner else None,
            "is_owner": project.created_by == current_user.id,
            "team_members": [
                {
                    "id": member.id,
                    "name": member.name,
                    "email": member.email
                }
                for member in team_members
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch project details: {str(e)}"}), 500

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



