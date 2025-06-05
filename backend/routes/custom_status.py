from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import CustomStatus, Projects
from datetime import datetime

custom_status_bp = Blueprint('custom_status', __name__)

# ---------- CREATE CUSTOM STATUS ----------
@custom_status_bp.route("/", methods=["POST"])
@login_required
def create_custom_status():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description", "")
    color = data.get("color", "#6B7280")
    position = data.get("position", 0)
    is_default = data.get("is_default", False)
    project_id = data.get("project_id")

    if not name or not project_id:
        return jsonify({"error": "Status name and project_id are required"}), 400

    # Check project ownership
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by user"}), 403

    # Check if status name already exists for this project
    existing_status = CustomStatus.query.filter_by(name=name, project_id=project_id).first()
    if existing_status:
        return jsonify({"error": "Status name already exists for this project"}), 400

    # If this is set as default, unset other defaults for this project
    if is_default:
        CustomStatus.query.filter_by(project_id=project_id, is_default=True).update({'is_default': False})

    custom_status = CustomStatus(
        name=name,
        description=description,
        color=color,
        position=position,
        is_default=is_default,
        project_id=project_id
    )
    
    db.session.add(custom_status)
    db.session.commit()

    return jsonify({
        "message": "Custom status created",
        "status": {
            "id": custom_status.id,
            "name": custom_status.name,
            "description": custom_status.description,
            "color": custom_status.color,
            "position": custom_status.position,
            "is_default": custom_status.is_default
        }
    }), 201

# ---------- GET CUSTOM STATUSES FOR PROJECT ----------
@custom_status_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_custom_statuses(project_id):
    # Check project ownership or membership
    project = Projects.query.filter_by(id=project_id).first()
    if not project or (project.created_by != current_user.id):
        return jsonify({"error": "Project not found or not owned by user"}), 403

    statuses = CustomStatus.query.filter_by(project_id=project_id).order_by(CustomStatus.position.asc()).all()

    results = [{
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "color": s.color,
        "position": s.position,
        "is_default": s.is_default,
        "task_count": len(s.tasks)
    } for s in statuses]

    return jsonify(results), 200

# ---------- UPDATE CUSTOM STATUS ----------
@custom_status_bp.route("/<int:status_id>", methods=["PUT"])
@login_required
def update_custom_status(status_id):
    custom_status = CustomStatus.query.get(status_id)
    if not custom_status:
        return jsonify({"error": "Custom status not found"}), 404

    # Check project ownership
    if custom_status.project.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    
    # Check if new name conflicts with existing status in same project
    new_name = data.get("name", custom_status.name)
    if new_name != custom_status.name:
        existing_status = CustomStatus.query.filter_by(
            name=new_name, 
            project_id=custom_status.project_id
        ).filter(CustomStatus.id != status_id).first()
        if existing_status:
            return jsonify({"error": "Status name already exists for this project"}), 400

    # If setting as default, unset other defaults
    is_default = data.get("is_default", custom_status.is_default)
    if is_default and not custom_status.is_default:
        CustomStatus.query.filter_by(
            project_id=custom_status.project_id, 
            is_default=True
        ).update({'is_default': False})

    # Update fields
    custom_status.name = new_name
    custom_status.description = data.get("description", custom_status.description)
    custom_status.color = data.get("color", custom_status.color)
    custom_status.position = data.get("position", custom_status.position)
    custom_status.is_default = is_default

    db.session.commit()
    return jsonify({"message": "Custom status updated"}), 200

# ---------- DELETE CUSTOM STATUS ----------
@custom_status_bp.route("/<int:status_id>", methods=["DELETE"])
@login_required
def delete_custom_status(status_id):
    custom_status = CustomStatus.query.get(status_id)
    if not custom_status:
        return jsonify({"error": "Custom status not found"}), 404

    # Check project ownership
    if custom_status.project.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Check if any tasks are using this status
    if custom_status.tasks:
        return jsonify({
            "error": f"Cannot delete status. {len(custom_status.tasks)} tasks are using this status. Please reassign them first."
        }), 400

    db.session.delete(custom_status)
    db.session.commit()
    return jsonify({"message": "Custom status deleted"}), 200

# ---------- CREATE DEFAULT STATUSES FOR NEW PROJECT ----------
@custom_status_bp.route("/create-defaults/<int:project_id>", methods=["POST"])
@login_required
def create_default_statuses(project_id):
    # Check project ownership
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by user"}), 403

    # Check if statuses already exist
    existing_count = CustomStatus.query.filter_by(project_id=project_id).count()
    if existing_count > 0:
        return jsonify({"error": "Project already has custom statuses"}), 400

    # Create default statuses
    default_statuses = [
        {"name": "To-Do", "description": "Tasks that need to be started", "color": "#FACC15", "position": 1, "is_default": True},
        {"name": "In Progress", "description": "Tasks currently being worked on", "color": "#3B82F6", "position": 2, "is_default": False},
        {"name": "Done", "description": "Completed tasks", "color": "#22C55E", "position": 3, "is_default": False}
    ]

    created_statuses = []
    for status_data in default_statuses:
        status = CustomStatus(
            name=status_data["name"],
            description=status_data["description"],
            color=status_data["color"],
            position=status_data["position"],
            is_default=status_data["is_default"],
            project_id=project_id
        )
        db.session.add(status)
        created_statuses.append(status_data["name"])

    db.session.commit()
    return jsonify({
        "message": "Default statuses created",
        "statuses": created_statuses
    }), 201 