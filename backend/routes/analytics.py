from flask import Blueprint, jsonify
from flask_security import login_required, current_user
from database import db
from models import Projects, Tasks, Budget, Expense, TeamMembers, CustomStatus, Users
from datetime import datetime, timedelta
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/project/<int:project_id>/overview", methods=["GET"])
@login_required
def get_project_overview(project_id):
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # Get task statistics
    task_stats = db.session.query(
        CustomStatus.name.label('status'),
        func.count(Tasks.id).label('count')
    ).join(Tasks.custom_status).filter(
        Tasks.project_id == project_id
    ).group_by(CustomStatus.name).all()

    # Get budget vs expenses
    total_budget = db.session.query(func.sum(Budget.amount)).filter_by(project_id=project_id).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(project_id=project_id).scalar() or 0

    # Get expense breakdown by category
    expense_by_category = db.session.query(
        Expense.category_id,
        func.sum(Expense.amount).label('total')
    ).filter_by(project_id=project_id).group_by(Expense.category_id).all()

    # Get task completion trend (last 30 days) - using updated_at as proxy for completion
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    completion_trend = db.session.query(
        func.date(Tasks.updated_at).label('date'),
        func.count(Tasks.id).label('count')
    ).join(Tasks.custom_status).filter(
        Tasks.project_id == project_id,
        CustomStatus.name == 'Done',
        Tasks.updated_at >= thirty_days_ago
    ).group_by(func.date(Tasks.updated_at)).all()

    # Get task priority distribution
    priority_stats = db.session.query(
        Tasks.priority,
        func.count(Tasks.id).label('count')
    ).filter_by(project_id=project_id).group_by(Tasks.priority).all()

    # Get bottleneck analysis (tasks stuck in status for long time)
    bottleneck_analysis = db.session.query(
        CustomStatus.name.label('status'),
        func.avg(
            func.julianday('now') - func.julianday(Tasks.updated_at)
        ).label('avg_days')
    ).join(Tasks.custom_status).filter(
        Tasks.project_id == project_id
    ).group_by(CustomStatus.name).all()

    # Get team productivity (tasks completed per team member)
    team_productivity = db.session.query(
        Tasks.assigned_to.label('assignee_id'),
        func.count(Tasks.id).label('completed_tasks')
    ).join(Tasks.custom_status).filter(
        Tasks.project_id == project_id,
        CustomStatus.name == 'Done'
    ).group_by(Tasks.assigned_to).all()

    return jsonify({
        "task_stats": {
            "by_status": [{
                "status": stat.status,
                "count": stat.count
            } for stat in task_stats]
        },
        "budget_overview": {
            "total_budget": total_budget,
            "total_expenses": total_expenses,
            "remaining": total_budget - total_expenses
        },
        "expense_breakdown": [{
            "category_id": cat.category_id,
            "total": float(cat.total)
        } for cat in expense_by_category],
        "completion_trend": [{
            "date": str(trend.date),
            "count": trend.count
        } for trend in completion_trend],
        "priority_distribution": [{
            "priority": stat.priority,
            "count": stat.count
        } for stat in priority_stats],
        "bottleneck_analysis": [{
            "status": stat.status,
            "avg_days": float(stat.avg_days) if stat.avg_days else 0
        } for stat in bottleneck_analysis],
        "team_productivity": [{
            "assignee_id": prod.assignee_id,
            "completed_tasks": prod.completed_tasks
        } for prod in team_productivity]
    }), 200

@analytics_bp.route("/project/<int:project_id>/timeline", methods=["GET"])
@login_required
def get_project_timeline(project_id):
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # Get task timeline data
    tasks = Tasks.query.filter_by(project_id=project_id).all()
    timeline_data = []

    for task in tasks:
        assignee_name = task.assignee.name if task.assignee else "Unassigned"
        status_name = task.custom_status.name if task.custom_status else "No Status"
        
        timeline_data.append({
            "id": task.id,
            "title": task.title,
            "start_date": task.created_at.isoformat() if task.created_at else None,
            "end_date": task.updated_at.isoformat() if task.updated_at and status_name == 'Done' else None,
            "status": status_name,
            "assignee": assignee_name
        })

    return jsonify(timeline_data), 200

@analytics_bp.route("/project/<int:project_id>/workload", methods=["GET"])
@login_required
def get_team_workload(project_id):
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # Get workload per team member
    workload = db.session.query(
        Tasks.assigned_to.label('assignee_id'),
        Users.name.label('assignee_name'),
        CustomStatus.name.label('status'),
        func.count(Tasks.id).label('task_count')
    ).join(Users, Tasks.assigned_to == Users.id).join(
        CustomStatus, Tasks.status_id == CustomStatus.id
    ).filter(
        Tasks.project_id == project_id
    ).group_by(
        Tasks.assigned_to,
        Users.name,
        CustomStatus.name
    ).all()

    # Format data by team member
    workload_by_member = {}
    for item in workload:
        if item.assignee_id not in workload_by_member:
            workload_by_member[item.assignee_id] = {
                "name": item.assignee_name,
                "tasks": {}
            }
        workload_by_member[item.assignee_id]["tasks"][item.status] = item.task_count

    return jsonify(list(workload_by_member.values())), 200

# ---------- PROJECT DEADLINE RISK ANALYSIS ----------
@analytics_bp.route("/project/<int:project_id>/deadline-risk", methods=["GET"])
@login_required
def get_project_deadline_risk(project_id):
    try:
        # Verify user is a team member
        team_membership = TeamMembers.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        if not team_membership:
            return jsonify({"error": "Not authorized"}), 403

        # Get project tasks
        tasks = Tasks.query.filter_by(project_id=project_id).all()
        
        if not tasks:
            return jsonify({
                "risk_level": "low",
                "progress_percentage": 0,
                "days_remaining": 999,
                "total_tasks": 0,
                "completed_tasks": 0
            }), 200

        # Calculate progress
        completed_statuses = CustomStatus.query.filter(
            CustomStatus.project_id == project_id,
            CustomStatus.name.in_(["Done", "Completed", "Finished"])
        ).all()
        completed_status_ids = [s.id for s in completed_statuses]
        
        completed_tasks = [t for t in tasks if t.status_id in completed_status_ids]
        progress_percentage = round((len(completed_tasks) / len(tasks)) * 100) if tasks else 0

        # Find earliest deadline
        upcoming_tasks = [t for t in tasks if t.due_date and t.status_id not in completed_status_ids]
        
        if not upcoming_tasks:
            return jsonify({
                "risk_level": "low",
                "progress_percentage": progress_percentage,
                "days_remaining": 999,
                "total_tasks": len(tasks),
                "completed_tasks": len(completed_tasks)
            }), 200

        # Get the earliest deadline
        earliest_deadline = min(upcoming_tasks, key=lambda t: t.due_date).due_date
        today = datetime.now().date()
        days_remaining = (earliest_deadline - today).days

        # Determine risk level based on progress and time remaining
        risk_level = "low"
        
        if days_remaining < 0:  # Overdue
            risk_level = "critical"
        elif days_remaining <= 1:  # Due today/tomorrow
            if progress_percentage < 80:
                risk_level = "critical"
            elif progress_percentage < 90:
                risk_level = "high"
            else:
                risk_level = "medium"
        elif days_remaining <= 3:  # Due in 2-3 days
            if progress_percentage < 60:
                risk_level = "high"
            elif progress_percentage < 80:
                risk_level = "medium"
            else:
                risk_level = "low"
        elif days_remaining <= 7:  # Due in a week
            if progress_percentage < 40:
                risk_level = "medium"
            else:
                risk_level = "low"
        else:  # More than a week
            if progress_percentage < 20 and days_remaining <= 14:
                risk_level = "medium"
            else:
                risk_level = "low"

        return jsonify({
            "risk_level": risk_level,
            "progress_percentage": progress_percentage,
            "days_remaining": days_remaining,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "earliest_deadline": earliest_deadline.isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500 