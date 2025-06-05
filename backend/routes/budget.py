from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Budget, Projects, Tasks, TeamMembers
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

# ---------- CREATE BUDGET ----------
@budget_bp.route("/", methods=["POST"])
@login_required
def create_budget():
    data = request.get_json()
    print(f"DEBUG: Received data: {data}")
    
    amount = data.get("amount")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    notes = data.get("notes")
    project_id = data.get("project_id")
    task_id = data.get("task_id")
    
    print(f"DEBUG: start_date_str: '{start_date_str}', end_date_str: '{end_date_str}'")
    
    try:
        # Handle both ISO format and date-only format (YYYY-MM-DD)
        if start_date_str:
            if 'T' in start_date_str:
                start_date = datetime.fromisoformat(start_date_str)
            else:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        else:
            start_date = None
            
        if end_date_str:
            if 'T' in end_date_str:
                end_date = datetime.fromisoformat(end_date_str)
            else:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            end_date = None
    except ValueError as e:
        print(f"DEBUG: Date parsing error: {e}")
        return jsonify({"error": f"Invalid date format: {e}"}), 400

    if not amount or not start_date or not end_date:
        return jsonify({"error": "Amount, start date, and end date are required"}), 400

    if not project_id and not task_id:
        return jsonify({"error": "Either project_id or task_id is required"}), 400

    # Verify user is a team member
    if project_id:
        team_membership = TeamMembers.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        if not team_membership:
            return jsonify({"error": "Not authorized"}), 403
    elif task_id:
        task = Tasks.query.get_or_404(task_id)
        team_membership = TeamMembers.query.filter_by(
            project_id=task.project_id,
            user_id=current_user.id
        ).first()
        if not team_membership:
            return jsonify({"error": "Not authorized"}), 403

    budget = Budget(
        amount=amount,
        start_date=start_date,
        end_date=end_date,
        notes=notes,
        project_id=project_id,
        task_id=task_id,
        created_by=current_user.id
    )

    db.session.add(budget)
    db.session.commit()

    return jsonify({
        "message": "Budget created",
        "budget_id": budget.id
    }), 201

# ---------- GET PROJECT BUDGETS ----------
@budget_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_project_budgets(project_id):
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    budgets = Budget.query.filter_by(project_id=project_id).all()
    return jsonify([{
        "id": b.id,
        "amount": b.amount,
        "start_date": b.start_date.isoformat(),
        "end_date": b.end_date.isoformat(),
        "notes": b.notes,
        "created_by": b.creator.name,
        "created_at": b.created_at.isoformat()
    } for b in budgets]), 200

# ---------- GET TASK BUDGETS ----------
@budget_bp.route("/task/<int:task_id>", methods=["GET"])
@login_required
def get_task_budgets(task_id):
    task = Tasks.query.get_or_404(task_id)

    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    budgets = Budget.query.filter_by(task_id=task_id).all()
    return jsonify([{
        "id": b.id,
        "amount": b.amount,
        "start_date": b.start_date.isoformat(),
        "end_date": b.end_date.isoformat(),
        "notes": b.notes,
        "created_by": b.creator.name,
        "created_at": b.created_at.isoformat()
    } for b in budgets]), 200

# ---------- UPDATE BUDGET ----------
@budget_bp.route("/<int:budget_id>", methods=["PUT"])
@login_required
def update_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)

    # Verify user is a team member
    project_id = budget.project_id or budget.task.project_id
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()
    if "amount" in data:
        budget.amount = data["amount"]
    if "start_date" in data:
        date_str = data["start_date"]
        if 'T' in date_str:
            budget.start_date = datetime.fromisoformat(date_str)
        else:
            budget.start_date = datetime.strptime(date_str, "%Y-%m-%d")
    if "end_date" in data:
        date_str = data["end_date"]
        if 'T' in date_str:
            budget.end_date = datetime.fromisoformat(date_str)
        else:
            budget.end_date = datetime.strptime(date_str, "%Y-%m-%d")
    if "notes" in data:
        budget.notes = data["notes"]

    db.session.commit()
    return jsonify({"message": "Budget updated"}), 200

# ---------- DELETE BUDGET ----------
@budget_bp.route("/<int:budget_id>", methods=["DELETE"])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)

    # Verify user is a team member
    project_id = budget.project_id or budget.task.project_id
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    db.session.delete(budget)
    db.session.commit()
    return jsonify({"message": "Budget deleted"}), 200

# ---------- GET FUNDS USAGE ANALYSIS ----------
@budget_bp.route("/funds-usage/project/<int:project_id>", methods=["GET"])
@login_required
def get_project_funds_usage(project_id):
    """
    Calculate and return funds usage analysis for a project.
    Combines budget and expense data to show how much funds have been used.
    """
    print(f"DEBUG: Funds usage API called for project {project_id}")
    from models import Expense
    
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    # Get all budgets for the project
    budgets = Budget.query.filter_by(project_id=project_id).all()
    
    # Get all expenses for the project
    expenses = Expense.query.filter_by(project_id=project_id).all()
    
    # Calculate totals
    total_budget = sum(b.amount for b in budgets)
    total_expenses = sum(e.amount for e in expenses)
    remaining_funds = total_budget - total_expenses
    usage_percentage = (total_expenses / total_budget * 100) if total_budget > 0 else 0
    
    # Calculate budget utilization over time (monthly breakdown)
    from collections import defaultdict
    monthly_breakdown = defaultdict(lambda: {"budget": 0, "expenses": 0})
    
    for budget in budgets:
        month_key = budget.start_date.strftime("%Y-%m")
        monthly_breakdown[month_key]["budget"] += budget.amount
    
    for expense in expenses:
        month_key = expense.date.strftime("%Y-%m")
        monthly_breakdown[month_key]["expenses"] += expense.amount
    
    # Sort monthly data
    monthly_data = []
    for month in sorted(monthly_breakdown.keys()):
        data = monthly_breakdown[month]
        monthly_data.append({
            "month": month,
            "budget": data["budget"],
            "expenses": data["expenses"],
            "remaining": data["budget"] - data["expenses"]
        })
    
    # Calculate category-wise expense breakdown
    category_breakdown = defaultdict(float)
    for expense in expenses:
        category_breakdown[expense.category.name] += expense.amount
    
    # Determine status based on usage
    if usage_percentage >= 90:
        status = "critical"
        status_message = "Budget critically low"
    elif usage_percentage >= 75:
        status = "warning"
        status_message = "Budget usage high"
    elif usage_percentage >= 50:
        status = "moderate"
        status_message = "Budget usage moderate"
    else:
        status = "healthy"
        status_message = "Budget usage healthy"
    
    return jsonify({
        "project_id": project_id,
        "total_budget": total_budget,
        "total_expenses": total_expenses,
        "remaining_funds": remaining_funds,
        "usage_percentage": round(usage_percentage, 2),
        "status": status,
        "status_message": status_message,
        "monthly_breakdown": monthly_data,
        "category_breakdown": dict(category_breakdown),
        "budget_count": len(budgets),
        "expense_count": len(expenses)
    }), 200

# ---------- GET FUNDS USAGE FOR TASK ----------
@budget_bp.route("/funds-usage/task/<int:task_id>", methods=["GET"])
@login_required  
def get_task_funds_usage(task_id):
    """
    Calculate and return funds usage analysis for a specific task.
    """
    from models import Expense
    
    task = Tasks.query.get_or_404(task_id)
    
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403
    
    # Get all budgets for the task
    budgets = Budget.query.filter_by(task_id=task_id).all()
    
    # Get all expenses for the task  
    expenses = Expense.query.filter_by(task_id=task_id).all()
    
    # Calculate totals
    total_budget = sum(b.amount for b in budgets)
    total_expenses = sum(e.amount for e in expenses)
    remaining_funds = total_budget - total_expenses
    usage_percentage = (total_expenses / total_budget * 100) if total_budget > 0 else 0
    
    # Calculate category-wise expense breakdown
    category_breakdown = defaultdict(float)
    for expense in expenses:
        category_breakdown[expense.category.name] += expense.amount
    
    # Determine status based on usage
    if usage_percentage >= 90:
        status = "critical"
        status_message = "Task budget critically low"
    elif usage_percentage >= 75:
        status = "warning" 
        status_message = "Task budget usage high"
    elif usage_percentage >= 50:
        status = "moderate"
        status_message = "Task budget usage moderate"
    else:
        status = "healthy"
        status_message = "Task budget usage healthy"
    
    return jsonify({
        "task_id": task_id,
        "task_title": task.title,
        "total_budget": total_budget,
        "total_expenses": total_expenses,
        "remaining_funds": remaining_funds,
        "usage_percentage": round(usage_percentage, 2),
        "status": status,
        "status_message": status_message,
        "category_breakdown": dict(category_breakdown),
        "budget_count": len(budgets),
        "expense_count": len(expenses)
    }), 200 