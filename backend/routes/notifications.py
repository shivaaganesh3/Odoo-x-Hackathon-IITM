from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Notifications, Tasks, Projects, TeamMembers
from deadline_warnings import DeadlineWarningEngine
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__)

# ---------- GET USER NOTIFICATIONS ----------
@notifications_bp.route("/", methods=["GET"])
@login_required
def get_user_notifications():
    """Get notifications for the current user with filtering options"""
    
    # Query parameters for filtering
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    notification_type = request.args.get("type")  # deadline_warning, task_overdue, general
    priority = request.args.get("priority")  # low, medium, high, critical
    project_id = request.args.get("project_id")
    limit = min(int(request.args.get("limit", 50)), 100)  # Cap at 100
    offset = int(request.args.get("offset", 0))

    # Base query
    query = Notifications.query.filter_by(user_id=current_user.id)

    # Apply filters
    if unread_only:
        query = query.filter(Notifications.is_read == False)
    
    if notification_type:
        query = query.filter(Notifications.type == notification_type)
    
    if priority:
        query = query.filter(Notifications.priority == priority)
    
    if project_id:
        try:
            project_id_int = int(project_id)
            # Verify user has access to this project
            team_membership = TeamMembers.query.filter_by(
                project_id=project_id_int, 
                user_id=current_user.id
            ).first()
            if team_membership:
                query = query.filter(Notifications.project_id == project_id_int)
            else:
                return jsonify({"error": "Project not found or user not authorized"}), 403
        except ValueError:
            return jsonify({"error": "Invalid project_id"}), 400

    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination and ordering
    notifications = query.order_by(
        Notifications.created_at.desc()
    ).offset(offset).limit(limit).all()

    # Format response
    notification_data = []
    for notification in notifications:
        data = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "priority": notification.priority,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
            "task_id": notification.task_id,
            "project_id": notification.project_id
        }
        
        # Add related task/project info if available
        if notification.task:
            data["task_title"] = notification.task.title
            data["task_status"] = notification.task.custom_status.name if notification.task.custom_status else None
        
        if notification.project:
            data["project_name"] = notification.project.name
            
        notification_data.append(data)

    return jsonify({
        "notifications": notification_data,
        "total_count": total_count,
        "unread_count": Notifications.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count(),
        "has_more": offset + limit < total_count
    }), 200


# ---------- MARK NOTIFICATION AS READ ----------
@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    
    notification = Notifications.query.filter_by(
        id=notification_id, 
        user_id=current_user.id
    ).first()
    
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({"message": "Notification marked as read"}), 200


# ---------- MARK ALL NOTIFICATIONS AS READ ----------
@notifications_bp.route("/read-all", methods=["PUT"])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    
    notification_type = request.args.get("type")  # Optional: only mark specific type as read
    
    query = Notifications.query.filter_by(user_id=current_user.id, is_read=False)
    
    if notification_type:
        query = query.filter(Notifications.type == notification_type)
    
    updated_count = query.update({"is_read": True})
    db.session.commit()
    
    return jsonify({
        "message": f"Marked {updated_count} notifications as read"
    }), 200


# ---------- DELETE NOTIFICATION ----------
@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
@login_required
def delete_notification(notification_id):
    """Delete a specific notification"""
    
    notification = Notifications.query.filter_by(
        id=notification_id, 
        user_id=current_user.id
    ).first()
    
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({"message": "Notification deleted"}), 200


# ---------- DEADLINE WARNING ANALYSIS ----------
@notifications_bp.route("/deadline-analysis", methods=["POST"])
@login_required
def run_deadline_analysis():
    """Trigger deadline warning analysis for all projects the user has access to"""
    
    # Get all projects user is a member of
    user_projects = db.session.query(Projects).join(TeamMembers).filter(
        TeamMembers.user_id == current_user.id
    ).all()
    
    if not user_projects:
        return jsonify({"message": "No projects found for user"}), 200
    
    # Run analysis
    try:
        analysis_summary = DeadlineWarningEngine.analyze_all_tasks()
        
        return jsonify({
            "message": "Deadline analysis completed",
            "summary": analysis_summary,
            "analyzed_projects": len(user_projects)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


# ---------- TASK DEADLINE INSIGHTS ----------
@notifications_bp.route("/task-insights/<int:task_id>", methods=["GET"])
@login_required
def get_task_deadline_insights(task_id):
    """Get detailed deadline insights for a specific task"""
    
    # Verify user has access to the task
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Check if user is a team member of the project
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id, 
        user_id=current_user.id
    ).first()
    
    if not team_membership:
        return jsonify({"error": "Task not found or user not authorized"}), 403
    
    try:
        insights = DeadlineWarningEngine.get_task_deadline_insights(task_id)
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get insights: {str(e)}"}), 500


# ---------- NOTIFICATION PREFERENCES ----------
@notifications_bp.route("/preferences", methods=["GET"])
@login_required
def get_notification_preferences():
    """Get notification preferences for the current user"""
    # This is a placeholder for future user preference customization
    # For now, return default preferences
    
    default_preferences = {
        "deadline_warnings": {
            "enabled": True,
            "frequency": {
                "critical": 6,  # hours
                "high": 12,
                "medium": 24
            }
        },
        "email_notifications": False,  # Future feature
        "push_notifications": True    # Future feature
    }
    
    return jsonify(default_preferences), 200


# ---------- NOTIFICATION STATISTICS ----------
@notifications_bp.route("/stats", methods=["GET"])
@login_required
def get_notification_stats():
    """Get notification statistics for the current user"""
    
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        "total_notifications": Notifications.query.filter_by(user_id=current_user.id).count(),
        "unread_notifications": Notifications.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count(),
        "this_week": Notifications.query.filter(
            Notifications.user_id == current_user.id,
            Notifications.created_at >= week_ago
        ).count(),
        "this_month": Notifications.query.filter(
            Notifications.user_id == current_user.id,
            Notifications.created_at >= month_ago
        ).count(),
        "by_type": {},
        "by_priority": {}
    }
    
    # Get breakdown by type
    type_counts = db.session.query(
        Notifications.type, 
        db.func.count(Notifications.id)
    ).filter_by(user_id=current_user.id).group_by(Notifications.type).all()
    
    for notification_type, count in type_counts:
        stats["by_type"][notification_type] = count
    
    # Get breakdown by priority
    priority_counts = db.session.query(
        Notifications.priority, 
        db.func.count(Notifications.id)
    ).filter_by(user_id=current_user.id).group_by(Notifications.priority).all()
    
    for priority, count in priority_counts:
        stats["by_priority"][priority] = count
    
    return jsonify(stats), 200 