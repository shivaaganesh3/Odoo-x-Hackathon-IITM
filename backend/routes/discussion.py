from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Discussions, Projects, Tasks, TeamMembers
from datetime import datetime

discussion_bp = Blueprint('discussion', __name__)

# ---------- CREATE DISCUSSION ----------
@discussion_bp.route("/", methods=["POST"])
@login_required
def create_discussion():
    data = request.get_json()
    message = data.get("message")
    project_id = data.get("project_id")
    task_id = data.get("task_id")
    parent_id = data.get("parent_id")

    if not message or not project_id:
        return jsonify({"error": "Message and project_id are required"}), 400

    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # If task_id provided, verify it belongs to the project
    if task_id:
        task = Tasks.query.filter_by(id=task_id, project_id=project_id).first()
        if not task:
            return jsonify({"error": "Task not found in project"}), 404

    # If parent_id provided, verify it exists and belongs to same project
    if parent_id:
        parent = Discussions.query.filter_by(id=parent_id, project_id=project_id).first()
        if not parent:
            return jsonify({"error": "Parent discussion not found"}), 404

    discussion = Discussions(
        message=message,
        project_id=project_id,
        task_id=task_id,
        parent_id=parent_id,
        user_id=current_user.id
    )

    db.session.add(discussion)
    db.session.commit()

    return jsonify({
        "message": "Discussion created",
        "discussion_id": discussion.id
    }), 201

# ---------- GET PROJECT DISCUSSIONS ----------
@discussion_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_project_discussions(project_id):
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # Get root-level discussions (no parent_id)
    discussions = Discussions.query.filter_by(
        project_id=project_id,
        parent_id=None,
        task_id=None  # Exclude task-specific discussions
    ).order_by(Discussions.timestamp.desc()).all()

    return jsonify([{
        "id": d.id,
        "message": d.message,
        "timestamp": d.timestamp.isoformat(),
        "user_id": d.user_id,
        "author_name": d.author.name,
        "replies_count": len(d.replies)
    } for d in discussions]), 200

# ---------- GET TASK DISCUSSIONS ----------
@discussion_bp.route("/task/<int:task_id>", methods=["GET"])
@login_required
def get_task_discussions(task_id):
    task = Tasks.query.get_or_404(task_id)

    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # Get root-level discussions for the task
    discussions = Discussions.query.filter_by(
        task_id=task_id,
        parent_id=None
    ).order_by(Discussions.timestamp.desc()).all()

    return jsonify([{
        "id": d.id,
        "message": d.message,
        "timestamp": d.timestamp.isoformat(),
        "user_id": d.user_id,
        "author_name": d.author.name,
        "replies_count": len(d.replies)
    } for d in discussions]), 200

# ---------- GET DISCUSSION REPLIES ----------
@discussion_bp.route("/<int:discussion_id>/replies", methods=["GET"])
@login_required
def get_discussion_replies(discussion_id):
    discussion = Discussions.query.get_or_404(discussion_id)

    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=discussion.project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    return jsonify([{
        "id": d.id,
        "message": d.message,
        "timestamp": d.timestamp.isoformat(),
        "user_id": d.user_id,
        "author_name": d.author.name
    } for d in discussion.replies]), 200

# ---------- UPDATE DISCUSSION ----------
@discussion_bp.route("/<int:discussion_id>", methods=["PUT"])
@login_required
def update_discussion(discussion_id):
    discussion = Discussions.query.get_or_404(discussion_id)

    # Only allow the author to update
    if discussion.user_id != current_user.id:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    discussion.message = message
    db.session.commit()

    return jsonify({"message": "Discussion updated"}), 200

# ---------- DELETE DISCUSSION ----------
@discussion_bp.route("/<int:discussion_id>", methods=["DELETE"])
@login_required
def delete_discussion(discussion_id):
    discussion = Discussions.query.get_or_404(discussion_id)

    # Only allow the author to delete
    if discussion.user_id != current_user.id:
        return jsonify({"error": "Not authorized"}), 403

    db.session.delete(discussion)
    db.session.commit()

    return jsonify({"message": "Discussion deleted"}), 200
