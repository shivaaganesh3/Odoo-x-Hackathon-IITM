from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Discussions, Tasks, Projects, TeamMembers
from datetime import datetime

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/test-discussion')
def test_discussion():
    return {"message": "Discussion route working!"}

@discussion_bp.route('/task/<int:task_id>/thread', methods=['POST'])
@login_required
def create_task_thread(task_id):
    data = request.get_json()
    message = data.get('message')
    parent_id = data.get('parent_id')  # Optional, for replies
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    project_id = task.project_id

    # Check if user is a team member of the project
    team_member = TeamMembers.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not team_member:
        return jsonify({'error': 'Not authorized'}), 403

    discussion = Discussions(
        message=message,
        user_id=current_user.id,
        project_id=project_id,
        task_id=task_id,
        parent_id=parent_id,
        timestamp=datetime.utcnow()
    )
    db.session.add(discussion)
    db.session.commit()
    return jsonify({'message': 'Comment posted', 'discussion_id': discussion.id}), 201

@discussion_bp.route('/task/<int:task_id>/threads', methods=['GET'])
@login_required
def get_task_threads(task_id):
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    project_id = task.project_id
    # Check if user is a team member of the project
    team_member = TeamMembers.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not team_member:
        return jsonify({'error': 'Not authorized'}), 403
    # Get all top-level threads/comments for this task
    threads = Discussions.query.filter_by(task_id=task_id, parent_id=None).order_by(Discussions.timestamp.asc()).all()
    def serialize_thread(thread):
        return {
            'id': thread.id,
            'message': thread.message,
            'user_id': thread.user_id,
            'timestamp': thread.timestamp.isoformat(),
            'replies': [serialize_thread(reply) for reply in thread.replies]
        }
    return jsonify([serialize_thread(thread) for thread in threads]), 200
