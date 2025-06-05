from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Tasks, TaskComments, TeamMembers, Projects
from datetime import datetime

task_comment_bp = Blueprint('task_comment', __name__)

# Helper function to check if user is a team member of the project
def is_team_member(user_id, project_id):
    team_member = TeamMembers.query.filter_by(
        user_id=user_id,
        project_id=project_id
    ).first()
    return team_member is not None

# ---------- CREATE COMMENT ----------
@task_comment_bp.route("/", methods=["POST"])
@login_required
def create_comment():
    data = request.get_json()
    task_id = data.get("task_id")
    content = data.get("content")
    parent_id = data.get("parent_id")  # Optional, for threaded replies
    
    if not task_id or not content:
        return jsonify({"error": "Task ID and comment content are required"}), 400
    
    # Get the task and its project
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Check if user is a team member of the project
    if not is_team_member(current_user.id, task.project_id):
        return jsonify({"error": "Only team members can comment on tasks"}), 403
    
    # If it's a reply, verify the parent comment exists and belongs to the same task
    if parent_id:
        parent_comment = TaskComments.query.get(parent_id)
        if not parent_comment or parent_comment.task_id != task_id:
            return jsonify({"error": "Invalid parent comment"}), 400
    
    # Create the comment
    comment = TaskComments(
        content=content,
        task_id=task_id,
        user_id=current_user.id,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # Return the created comment with author info
    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "timestamp": comment.timestamp.isoformat(),
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "user_name": comment.author.name,
        "parent_id": comment.parent_id
    }), 201

# ---------- GET COMMENTS FOR A TASK ----------
@task_comment_bp.route("/task/<int:task_id>", methods=["GET"])
@login_required
def get_task_comments(task_id):
    # Get the task and its project
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Check if user is a team member of the project
    if not is_team_member(current_user.id, task.project_id):
        return jsonify({"error": "Only team members can view task comments"}), 403
    
    # Get all top-level comments (no parent)
    comments = TaskComments.query.filter_by(
        task_id=task_id,
        parent_id=None
    ).order_by(TaskComments.timestamp.asc()).all()
    
    result = []
    for comment in comments:
        # Get all replies for this comment
        replies = TaskComments.query.filter_by(
            parent_id=comment.id
        ).order_by(TaskComments.timestamp.asc()).all()
        
        # Format replies
        formatted_replies = [{
            "id": reply.id,
            "content": reply.content,
            "timestamp": reply.timestamp.isoformat(),
            "user_id": reply.user_id,
            "user_name": reply.author.name
        } for reply in replies]
        
        # Format the main comment with its replies
        result.append({
            "id": comment.id,
            "content": comment.content,
            "timestamp": comment.timestamp.isoformat(),
            "user_id": comment.user_id,
            "user_name": comment.author.name,
            "replies": formatted_replies
        })
    
    return jsonify(result), 200

# ---------- UPDATE COMMENT ----------
@task_comment_bp.route("/<int:comment_id>", methods=["PUT"])
@login_required
def update_comment(comment_id):
    comment = TaskComments.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Only the author can update their comment
    if comment.user_id != current_user.id:
        return jsonify({"error": "You can only edit your own comments"}), 403
    
    data = request.get_json()
    content = data.get("content")
    
    if not content:
        return jsonify({"error": "Comment content is required"}), 400
    
    comment.content = content
    db.session.commit()
    
    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "timestamp": comment.timestamp.isoformat(),
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "user_name": comment.author.name,
        "parent_id": comment.parent_id
    }), 200

# ---------- DELETE COMMENT ----------
@task_comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    comment = TaskComments.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Only the author can delete their comment
    if comment.user_id != current_user.id:
        return jsonify({"error": "You can only delete your own comments"}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"message": "Comment deleted"}), 200