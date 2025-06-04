from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Projects
from flask_security import roles_required


project_bp = Blueprint('project', __name__)

# ---------- CREATE PROJECT ----------
@project_bp.route("/", methods=["POST"])
@login_required
def create_project():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Project name is required"}), 400

    project = Projects(
        name=name,
        description=description,
        created_by=current_user.id
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({"message": "Project created", "project_id": project.id}), 201

# ---------- GET ALL PROJECTS (User Created) ----------
@project_bp.route("/", methods=["GET"])
@login_required
def get_user_projects():
    projects = Projects.query.filter_by(created_by=current_user.id).all()
    results = [{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "created_at": p.created_at
    } for p in projects]

    return jsonify(results), 200

# ---------- UPDATE PROJECT ----------
@project_bp.route("/<int:project_id>", methods=["PUT"])
@login_required
def update_project(project_id):
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    data = request.get_json()
    project.name = data.get("name", project.name)
    project.description = data.get("description", project.description)
    db.session.commit()

    return jsonify({"message": "Project updated"}), 200

# ---------- DELETE PROJECT ----------
@project_bp.route("/<int:project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id):
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({"message": "Project deleted"}), 200

@project_bp.route("/admin/projects", methods=["GET"])
@roles_required("admin")
def admin_only_projects():
    projects = Projects.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in projects])

