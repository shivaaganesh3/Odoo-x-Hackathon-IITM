from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Tasks, Projects, CustomStatus, TeamMembers, Users
from datetime import datetime, timedelta
from task_prioritization import TaskPrioritizationEngine
from deadline_warnings import DeadlineWarningEngine
from llm_task_parser import get_task_parser
import logging

task_bp = Blueprint('task', __name__)

# Configure logging
logger = logging.getLogger(__name__)

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
    status_id = data.get("status_id")
    due_date_str = data.get("due_date")
    project_id = data.get("project_id")
    assigned_to = data.get("assigned_to")
    
    # Smart prioritization fields
    effort_score = data.get("effort_score", 3)  # Default: Medium effort
    impact_score = data.get("impact_score", 3)  # Default: Medium impact
    dependency_map = data.get("dependency_map", [])
    blocked_by = data.get("blocked_by", [])

    if not title or not project_id:
        return jsonify({"error": "Task title and project_id required"}), 400

    # Convert due date
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None

    # Check if user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Project not found or user not authorized"}), 403

    project = Projects.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Handle status_id - if not provided, use default status for the project
    if not status_id:
        default_status = CustomStatus.query.filter_by(project_id=project_id, is_default=True).first()
        if default_status:
            status_id = default_status.id
        else:
            # If no default status exists, create default statuses first
            return jsonify({"error": "No status found for project. Please create custom statuses first."}), 400
    else:
        # Validate that the status belongs to this project
        custom_status = CustomStatus.query.filter_by(id=status_id, project_id=project_id).first()
        if not custom_status:
            return jsonify({"error": "Invalid status_id for this project"}), 400

    # Validate assignee if provided
    if assigned_to:
        assignee_membership = TeamMembers.query.filter_by(
            project_id=project_id, 
            user_id=assigned_to
        ).first()
        if not assignee_membership:
            return jsonify({"error": "Assigned user is not a team member of this project"}), 400

    # Validate dependency tasks exist and belong to same project
    if dependency_map:
        for dep_task_id in dependency_map:
            dep_task = Tasks.query.filter_by(id=dep_task_id, project_id=project_id).first()
            if not dep_task:
                return jsonify({"error": f"Dependency task {dep_task_id} not found in project"}), 400
    
    if blocked_by:
        for blocking_task_id in blocked_by:
            blocking_task = Tasks.query.filter_by(id=blocking_task_id, project_id=project_id).first()
            if not blocking_task:
                return jsonify({"error": f"Blocking task {blocking_task_id} not found in project"}), 400

    # Create task with smart prioritization fields
    task = Tasks(
        title=title,
        description=description,
        status_id=status_id,
        due_date=due_date,
        project_id=project_id,
        assigned_to=assigned_to,
        effort_score=effort_score,
        impact_score=impact_score,
        dependency_map=dependency_map,
        blocked_by=blocked_by
    )
    
    db.session.add(task)
    db.session.flush()  # Flush to get task ID for priority calculation
    
    # Calculate smart priority
    priority_label = TaskPrioritizationEngine.update_task_priority(task)
    
    # Update dependency maps for related tasks
    if dependency_map:
        for dep_task_id in dependency_map:
            dep_task = Tasks.query.get(dep_task_id)
            if dep_task:
                if not dep_task.blocked_by:
                    dep_task.blocked_by = []
                dep_task.blocked_by.append(task.id)
                TaskPrioritizationEngine.update_task_priority(dep_task)
    
    if blocked_by:
        for blocking_task_id in blocked_by:
            blocking_task = Tasks.query.get(blocking_task_id)
            if blocking_task:
                if not blocking_task.dependency_map:
                    blocking_task.dependency_map = []
                blocking_task.dependency_map.append(task.id)
                TaskPrioritizationEngine.update_task_priority(blocking_task)
    
    db.session.commit()

    return jsonify({
        "message": "Task created", 
        "task_id": task.id, 
        "priority": task.priority,
        "priority_score": task.priority_score
    }), 201

# ---------- NATURAL LANGUAGE TASK PARSING ----------
@task_bp.route("/parse-nl-task", methods=["POST"])
@login_required
def parse_natural_language_task():
    """
    Parse natural language task input using Gemini + LangChain
    
    Expected input:
    {
        "text": "Remind John to finalize the pitch deck by Friday",
        "project_id": 2
    }
    
    Returns:
    {
        "title": "Finalize the pitch deck",
        "assigned_to": 5,  # User ID
        "due_date": "2024-01-26",
        "status_id": 1,  # Default status ID
        "project_id": 2,
        "priority": "Medium",
        "effort_score": 3,
        "impact_score": 3,
        "parsing_info": {
            "confidence": "high",
            "assignee_name": "John",
            "extracted_info": {...}
        }
    }
    """
    try:
        data = request.get_json()
        text = data.get("text")
        project_id = data.get("project_id")
        
        if not text:
            return jsonify({"error": "Text input required"}), 400
        
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        logger.info(f"Parsing natural language task: '{text}' for project {project_id}")
        
        # Validate user is a team member of the project
        team_membership = TeamMembers.query.filter_by(
            project_id=project_id, 
            user_id=current_user.id
        ).first()
        if not team_membership:
            return jsonify({"error": "Project not found or user not authorized"}), 403

        # Validate project exists
        project = Projects.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Get the task parser instance
        parser = get_task_parser()
        
        # Parse the natural language input
        parsed_result = parser.parse_natural_language_task(text, project_id)
        
        logger.info(f"Parsed result: {parsed_result}")
        
        # Get default status for the project
        default_status = CustomStatus.query.filter_by(
            project_id=project_id, 
            is_default=True
        ).first()
        
        if not default_status:
            # If no default status exists, get the first status for the project
            default_status = CustomStatus.query.filter_by(project_id=project_id).first()
            
        if not default_status:
            return jsonify({
                "error": "No status found for project. Please create custom statuses first."
            }), 400
        
        # Prepare structured task data for response
        task_data = {
            "title": parsed_result.get("title", "").strip(),
            "description": parsed_result.get("description"),
            "assigned_to": parsed_result.get("assigned_to"),
            "due_date": parsed_result.get("due_date"),
            "status_id": default_status.id,
            "project_id": project_id,
            "priority": parsed_result.get("priority", "Medium"),
            "effort_score": parsed_result.get("effort_score", 3),
            "impact_score": parsed_result.get("impact_score", 3)
        }
        
        # Additional parsing information for debugging/transparency
        parsing_info = {
            "confidence": parsed_result.get("extracted_info", {}).get("confidence", "unknown"),
            "assignee_name": parsed_result.get("assignee_name"),
            "date_context": parsed_result.get("extracted_info", {}).get("date_context"),
            "assignee_context": parsed_result.get("extracted_info", {}).get("assignee_context"),
            "original_text": text,
            "extracted_info": parsed_result.get("extracted_info", {})
        }
        
        # Include assignee information if found
        if task_data["assigned_to"]:
            assignee = Users.query.get(task_data["assigned_to"])
            if assignee:
                parsing_info["resolved_assignee"] = {
                    "id": assignee.id,
                    "name": assignee.name,
                    "email": assignee.email
                }
        
        # Warnings for missing or uncertain information
        warnings = []
        if not task_data["title"]:
            warnings.append("Could not extract clear task title")
        if parsed_result.get("assignee_name") and not task_data["assigned_to"]:
            warnings.append(f"Could not find team member '{parsed_result.get('assignee_name')}' in project")
        if parsing_info["confidence"] == "low":
            warnings.append("Low confidence in parsing results - please review")
            
        response = {
            **task_data,
            "parsing_info": parsing_info,
            "default_status": {
                "id": default_status.id,
                "name": default_status.name,
                "color": default_status.color
            }
        }
        
        if warnings:
            response["warnings"] = warnings
        
        logger.info(f"Returning parsed task data: {response}")
        return jsonify(response), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error parsing natural language task: {e}")
        return jsonify({
            "error": "Failed to parse natural language task",
            "details": str(e)
        }), 500

# ---------- GET TASKS BY PROJECT ----------
@task_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_tasks_for_project(project_id):
    # Validate user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Project not found or user not authorized"}), 403

    project = Projects.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Read optional filters
    status_id = request.args.get("status_id")  # Changed from status to status_id
    due_date = request.args.get("due_date")
    assigned_to = request.args.get("assigned_to")

    # Base query with joins to get status information
    query = Tasks.query.filter_by(project_id=project_id)

    # Apply filters if provided
    if status_id:
        try:
            query = query.filter(Tasks.status_id == int(status_id))
        except ValueError:
            return jsonify({"error": "Invalid status_id"}), 400
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            query = query.filter(Tasks.due_date == parsed_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if assigned_to:
        try:
            assigned_to_int = int(assigned_to)
            if assigned_to_int == 0:
                # Filter for unassigned tasks
                query = query.filter(Tasks.assigned_to.is_(None))
            else:
                query = query.filter(Tasks.assigned_to == assigned_to_int)
        except ValueError:
            return jsonify({"error": "Invalid assigned_to value"}), 400

    # Smart sorting: order by priority score (highest first), then by due date
    sort_by = request.args.get("sort_by", "smart")  # smart, due_date, priority, created_at
    
    if sort_by == "smart":
        tasks = query.order_by(Tasks.priority_score.desc(), Tasks.due_date.asc()).all()
    elif sort_by == "due_date":
        tasks = query.order_by(Tasks.due_date.asc()).all()
    elif sort_by == "priority":
        priority_order = {"Urgent": 4, "High": 3, "Medium": 2, "Low": 1}
        tasks = query.all()
        tasks.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=True)
    else:
        tasks = query.order_by(Tasks.created_at.desc()).all()

    results = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": {
            "id": t.custom_status.id if t.custom_status else None,
            "name": t.custom_status.name if t.custom_status else "No Status",
            "color": t.custom_status.color if t.custom_status else "#6B7280"
        },
        "due_date": str(t.due_date) if t.due_date else None,
        "priority": t.priority,
        "priority_score": t.priority_score,
        "effort_score": t.effort_score,
        "impact_score": t.impact_score,
        "dependency_map": t.dependency_map or [],
        "blocked_by": t.blocked_by or [],
        "assigned_to": t.assigned_to,
        "assignee_name": t.assignee.name if t.assignee else None,
        "is_blocked": len(t.blocked_by or []) > 0,
        "blocks_others": len(t.dependency_map or []) > 0
    } for t in tasks]

    return jsonify(results), 200

# ---------- UPDATE TASK ----------
@task_bp.route("/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Ensure the current user is a team member of the project
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    
    # Validate assignee if provided
    assigned_to = data.get("assigned_to")
    if assigned_to is not None:
        if assigned_to:  # If not None and not empty
            assignee_membership = TeamMembers.query.filter_by(
                project_id=task.project_id, 
                user_id=assigned_to
            ).first()
            if not assignee_membership:
                return jsonify({"error": "Assigned user is not a team member of this project"}), 400
    
    # Update basic fields
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.assigned_to = data.get("assigned_to", task.assigned_to)
    
    # Update smart prioritization fields
    task.effort_score = data.get("effort_score", task.effort_score)
    task.impact_score = data.get("impact_score", task.impact_score)
    
    # Handle dependency changes
    new_dependency_map = data.get("dependency_map")
    new_blocked_by = data.get("blocked_by")
    
    if new_dependency_map is not None:
        # Validate dependency tasks exist and belong to same project
        for dep_task_id in new_dependency_map:
            dep_task = Tasks.query.filter_by(id=dep_task_id, project_id=task.project_id).first()
            if not dep_task:
                return jsonify({"error": f"Dependency task {dep_task_id} not found in project"}), 400
        
        # Update reverse dependencies
        old_dependencies = task.dependency_map or []
        for old_dep in old_dependencies:
            if old_dep not in new_dependency_map:
                # Remove from blocked_by list of the old dependency
                old_dep_task = Tasks.query.get(old_dep)
                if old_dep_task and old_dep_task.blocked_by:
                    old_dep_task.blocked_by = [x for x in old_dep_task.blocked_by if x != task.id]
                    TaskPrioritizationEngine.update_task_priority(old_dep_task)
        
        for new_dep in new_dependency_map:
            if new_dep not in old_dependencies:
                # Add to blocked_by list of the new dependency
                new_dep_task = Tasks.query.get(new_dep)
                if new_dep_task:
                    if not new_dep_task.blocked_by:
                        new_dep_task.blocked_by = []
                    new_dep_task.blocked_by.append(task.id)
                    TaskPrioritizationEngine.update_task_priority(new_dep_task)
        
        task.dependency_map = new_dependency_map
    
    if new_blocked_by is not None:
        # Validate blocking tasks exist and belong to same project
        for blocking_task_id in new_blocked_by:
            blocking_task = Tasks.query.filter_by(id=blocking_task_id, project_id=task.project_id).first()
            if not blocking_task:
                return jsonify({"error": f"Blocking task {blocking_task_id} not found in project"}), 400
        
        # Update reverse dependencies
        old_blocked_by = task.blocked_by or []
        for old_blocker in old_blocked_by:
            if old_blocker not in new_blocked_by:
                # Remove from dependency_map list of the old blocker
                old_blocker_task = Tasks.query.get(old_blocker)
                if old_blocker_task and old_blocker_task.dependency_map:
                    old_blocker_task.dependency_map = [x for x in old_blocker_task.dependency_map if x != task.id]
                    TaskPrioritizationEngine.update_task_priority(old_blocker_task)
        
        for new_blocker in new_blocked_by:
            if new_blocker not in old_blocked_by:
                # Add to dependency_map list of the new blocker
                new_blocker_task = Tasks.query.get(new_blocker)
                if new_blocker_task:
                    if not new_blocker_task.dependency_map:
                        new_blocker_task.dependency_map = []
                    new_blocker_task.dependency_map.append(task.id)
                    TaskPrioritizationEngine.update_task_priority(new_blocker_task)
        
        task.blocked_by = new_blocked_by
    
    # Handle due date
    due_date_str = data.get("due_date")
    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Handle status update
    status_id = data.get("status_id")
    if status_id is not None:
        # Validate that the status belongs to this project
        custom_status = CustomStatus.query.filter_by(id=status_id, project_id=task.project_id).first()
        if not custom_status:
            return jsonify({"error": "Invalid status_id for this project"}), 400
        task.status_id = status_id

    # Recalculate smart priority after all updates
    TaskPrioritizationEngine.update_task_priority(task)
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Check for deadline risk and create notification if needed
    deadline_warning = None
    if task.due_date:
        try:
            risk_score, risk_level = DeadlineWarningEngine.calculate_deadline_risk(task)
            if risk_level in ['medium', 'high', 'critical']:
                notifications = DeadlineWarningEngine.create_deadline_notification(task, risk_score, risk_level)
                if notifications:
                    db.session.commit()  # Commit notifications
                    deadline_warning = {
                        "risk_level": risk_level,
                        "risk_score": risk_score,
                        "notifications_created": len(notifications)
                    }
        except Exception as e:
            print(f"Warning: Failed to create deadline notification: {e}")
    
    response = {
        "message": "Task updated",
        "priority": task.priority,
        "priority_score": task.priority_score
    }
    
    if deadline_warning:
        response["deadline_warning"] = deadline_warning
    
    return jsonify(response), 200

# ---------- DELETE TASK ----------
@task_bp.route("/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Ensure the current user is a team member of the project
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

# ---------- GET MY TASKS ----------
@task_bp.route("/my", methods=["GET"])
@login_required
def get_my_tasks():
    # Filters
    status_id = request.args.get("status_id")  # Changed from status to status_id
    due_date = request.args.get("due_date")

    query = Tasks.query.filter_by(assigned_to=current_user.id)

    if status_id:
        try:
            query = query.filter(Tasks.status_id == int(status_id))
        except ValueError:
            return jsonify({"error": "Invalid status_id"}), 400
    
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            query = query.filter(Tasks.due_date == parsed_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Smart sorting for my tasks too
    sort_by = request.args.get("sort_by", "smart")
    
    if sort_by == "smart":
        tasks = query.order_by(Tasks.priority_score.desc(), Tasks.due_date.asc()).all()
    elif sort_by == "due_date":
        tasks = query.order_by(Tasks.due_date.asc()).all()
    elif sort_by == "priority":
        priority_order = {"Urgent": 4, "High": 3, "Medium": 2, "Low": 1}
        tasks = query.all()
        tasks.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=True)
    else:
        tasks = query.order_by(Tasks.created_at.desc()).all()

    results = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": {
            "id": t.custom_status.id if t.custom_status else None,
            "name": t.custom_status.name if t.custom_status else "No Status",
            "color": t.custom_status.color if t.custom_status else "#6B7280"
        },
        "due_date": str(t.due_date) if t.due_date else None,
        "priority": t.priority,
        "priority_score": t.priority_score,
        "effort_score": t.effort_score,
        "impact_score": t.impact_score,
        "dependency_map": t.dependency_map or [],
        "blocked_by": t.blocked_by or [],
        "project_id": t.project_id,
        "project_name": t.project.name,
        "is_blocked": len(t.blocked_by or []) > 0,
        "blocks_others": len(t.dependency_map or []) > 0
    } for t in tasks]

    return jsonify(results), 200

# ---------- SMART PRIORITIZATION ENDPOINTS ----------

@task_bp.route("/priority/recalculate/<int:project_id>", methods=["POST"])
@login_required
def recalculate_project_priorities(project_id):
    """Recalculate priority scores for all tasks in a project"""
    # Validate user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Project not found or user not authorized"}), 403

    try:
        updated_tasks = TaskPrioritizationEngine.update_project_task_priorities(project_id)
        return jsonify({
            "message": f"Recalculated priorities for {len(updated_tasks)} tasks",
            "updated_tasks": updated_tasks
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/priority/insights/<int:task_id>", methods=["GET"])
@login_required  
def get_task_priority_insights(task_id):
    """Get detailed priority calculation breakdown for a task"""
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Ensure the current user is a team member of the project
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        insights = TaskPrioritizationEngine.get_priority_insights(task)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/priority/weights", methods=["GET"])
@login_required
def get_priority_weights():
    """Get current priority calculation weights"""
    return jsonify({
        "weights": TaskPrioritizationEngine.WEIGHTS,
        "description": {
            "urgency": "Days until deadline (weighted)",
            "effort": "Task complexity estimation (inverse)",
            "dependency": "Number of blocked tasks",
            "impact": "Project criticality"
        }
    }), 200

@task_bp.route("/dependencies/<int:project_id>", methods=["GET"])
@login_required
def get_project_dependencies(project_id):
    """Get task dependency graph for a project"""
    # Validate user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id, 
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Project not found or user not authorized"}), 403

    tasks = Tasks.query.filter_by(project_id=project_id).all()
    
    dependency_graph = []
    for task in tasks:
        if task.dependency_map or task.blocked_by:
            dependency_graph.append({
                "task_id": task.id,
                "title": task.title,
                "depends_on": task.blocked_by or [],  # Tasks that block this task
                "blocks": task.dependency_map or [],  # Tasks that this task blocks
                "priority_score": task.priority_score,
                "priority": task.priority
            })
    
    return jsonify({
        "project_id": project_id,
        "dependency_graph": dependency_graph
    }), 200

@task_bp.route("/blocked", methods=["GET"])
@login_required
def get_blocked_tasks():
    """Get all blocked tasks for the current user"""
    # Get user's projects
    user_projects = db.session.query(TeamMembers.project_id).filter_by(user_id=current_user.id).subquery()
    
    # Find tasks assigned to user that are blocked
    blocked_tasks = Tasks.query.filter(
        Tasks.assigned_to == current_user.id,
        Tasks.project_id.in_(user_projects),
        Tasks.blocked_by.isnot(None)
    ).all()
    
    # Filter to only tasks that actually have blocking tasks
    truly_blocked = [task for task in blocked_tasks if task.blocked_by and len(task.blocked_by) > 0]
    
    results = []
    for task in truly_blocked:
        blocking_tasks = Tasks.query.filter(Tasks.id.in_(task.blocked_by)).all()
        results.append({
            "id": task.id,
            "title": task.title,
            "project_name": task.project.name,
            "priority": task.priority,
            "priority_score": task.priority_score,
            "blocked_by_count": len(task.blocked_by),
            "blocking_tasks": [{
                "id": bt.id,
                "title": bt.title,
                "status": bt.custom_status.name if bt.custom_status else "No Status",
                "assignee": bt.assignee.name if bt.assignee else "Unassigned"
            } for bt in blocking_tasks]
        })
    
    return jsonify(results), 200
