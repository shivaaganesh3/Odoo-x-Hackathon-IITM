from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Tasks, Projects
from datetime import datetime,timedelta

task_bp = Blueprint('task', __name__)
def calculate_priority(due_date):
    if not due_date:
        return "Low"
    days_left = (due_date - datetime.utcnow().date()).days
    if days_left <= 1:
        return "Urgent"
    elif days_left <= 3:
        return "High"
    elif days_left <= 7:
        return "Medium"
    else:
        return "Low"
# ---------- CREATE TASK ----------
@task_bp.route("/", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    status = data.get("status", "To-Do")
    due_date_str = data.get("due_date")
    project_id = data.get("project_id")
    assigned_to = data.get("assigned_to")

    if not title or not project_id:
        return jsonify({"error": "Task title and project_id required"}), 400

    # Convert due date
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None

    # Check ownership
    project = Projects.query.filter_by(id=project_id, created_by=current_user.id).first()
    if not project:
        return jsonify({"error": "Project not found or not owned by user"}), 403

    # ✅ Calculate priority
    priority = calculate_priority(due_date)

    task = Tasks(
        title=title,
        description=description,
        status=status,
        due_date=due_date,
        project_id=project_id,
        assigned_to=assigned_to,
        priority=priority  # ✅ store it
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created", "task_id": task.id, "priority": task.priority}), 201
# ---------- GET TASKS BY PROJECT ----------
@task_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_tasks_for_project(project_id):
    # Validate project ownership (or skip if handled elsewhere)
    project = Projects.query.filter_by(id=project_id).first()
    if not project or (project.created_by != current_user.id):
        return jsonify({"error": "Project not found or not owned by user"}), 403

    # Read optional filters
    status = request.args.get("status")
    due_date = request.args.get("due_date")  # e.g., "2025-06-10"
    assigned_to = request.args.get("assigned_to")  # integer ID

    # Base query
    query = Tasks.query.filter_by(project_id=project_id)

    # Apply filters if provided
    if status:
        query = query.filter(Tasks.status == status)
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            query = query.filter(Tasks.due_date == parsed_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if assigned_to:
        try:
            query = query.filter(Tasks.assigned_to == int(assigned_to))
        except ValueError:
            return jsonify({"error": "Invalid assigned_to value"}), 400

    tasks = query.order_by(Tasks.due_date.asc()).all()

    results = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "due_date": str(t.due_date),
        "assigned_to": t.assigned_to
    } for t in tasks]

    return jsonify(results), 200
# ---------- UPDATE TASK ----------
@task_bp.route("/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Ensure the project owner is the current user
    if task.project.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    task.due_date = data.get("due_date", task.due_date)
    task.assigned_to = data.get("assigned_to", task.assigned_to)

    db.session.commit()
    return jsonify({"message": "Task updated"}), 200

# ---------- DELETE TASK ----------
@task_bp.route("/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.project.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

@task_bp.route("/my", methods=["GET"])
@login_required
def get_my_tasks():
    # Filters
    status = request.args.get("status")
    due_date = request.args.get("due_date")

    query = Tasks.query.filter_by(assigned_to=current_user.id)

    if status:
        query = query.filter(Tasks.status == status)
    
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            query = query.filter(Tasks.due_date == parsed_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    tasks = query.order_by(Tasks.due_date.asc()).all()

    results = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "due_date": str(t.due_date),
        "project_id": t.project_id
    } for t in tasks]

    return jsonify(results), 200
