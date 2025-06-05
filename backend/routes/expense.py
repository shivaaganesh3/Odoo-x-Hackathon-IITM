from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from database import db
from models import Expense, ExpenseCategory, Projects, Tasks, TeamMembers
from datetime import datetime

expense_bp = Blueprint('expense', __name__)

# ---------- GET EXPENSE CATEGORIES ----------
@expense_bp.route("/categories", methods=["GET"])
@login_required
def get_categories():
    categories = ExpenseCategory.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "description": c.description
    } for c in categories]), 200

# ---------- CREATE EXPENSE ----------
@expense_bp.route("/", methods=["POST"])
@login_required
def create_expense():
    data = request.get_json()
    amount = data.get("amount")
    date_str = data.get("date")
    notes = data.get("notes")
    receipt_url = data.get("receipt_url")
    project_id = data.get("project_id")
    task_id = data.get("task_id")
    category_id = data.get("category_id")
    
    try:
        if date_str:
            if 'T' in date_str:
                date = datetime.fromisoformat(date_str)
            else:
                date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date = None
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {e}"}), 400

    if not amount or not date or not category_id:
        return jsonify({"error": "Amount, date, and category are required"}), 400

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

    expense = Expense(
        amount=amount,
        date=date,
        notes=notes,
        receipt_url=receipt_url,
        project_id=project_id,
        task_id=task_id,
        category_id=category_id,
        created_by=current_user.id
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({
        "message": "Expense created",
        "expense_id": expense.id
    }), 201

# ---------- GET PROJECT EXPENSES ----------
@expense_bp.route("/project/<int:project_id>", methods=["GET"])
@login_required
def get_project_expenses(project_id):
    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    expenses = Expense.query.filter_by(project_id=project_id).all()
    return jsonify([{
        "id": e.id,
        "amount": e.amount,
        "date": e.date.isoformat(),
        "notes": e.notes,
        "receipt_url": e.receipt_url,
        "category": {
            "id": e.category.id,
            "name": e.category.name
        },
        "created_by": e.creator.name,
        "created_at": e.created_at.isoformat()
    } for e in expenses]), 200

# ---------- GET TASK EXPENSES ----------
@expense_bp.route("/task/<int:task_id>", methods=["GET"])
@login_required
def get_task_expenses(task_id):
    task = Tasks.query.get_or_404(task_id)

    # Verify user is a team member
    team_membership = TeamMembers.query.filter_by(
        project_id=task.project_id,
        user_id=current_user.id
    ).first()
    if not team_membership:
        return jsonify({"error": "Not authorized"}), 403

    expenses = Expense.query.filter_by(task_id=task_id).all()
    return jsonify([{
        "id": e.id,
        "amount": e.amount,
        "date": e.date.isoformat(),
        "notes": e.notes,
        "receipt_url": e.receipt_url,
        "category": {
            "id": e.category.id,
            "name": e.category.name
        },
        "created_by": e.creator.name,
        "created_at": e.created_at.isoformat()
    } for e in expenses]), 200

# ---------- UPDATE EXPENSE ----------
@expense_bp.route("/<int:expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    # Only allow the creator to update
    if expense.created_by != current_user.id:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()
    if "amount" in data:
        expense.amount = data["amount"]
    if "date" in data:
        date_str = data["date"]
        if 'T' in date_str:
            expense.date = datetime.fromisoformat(date_str)
        else:
            expense.date = datetime.strptime(date_str, "%Y-%m-%d")
    if "notes" in data:
        expense.notes = data["notes"]
    if "receipt_url" in data:
        expense.receipt_url = data["receipt_url"]
    if "category_id" in data:
        expense.category_id = data["category_id"]

    db.session.commit()
    return jsonify({"message": "Expense updated"}), 200

# ---------- DELETE EXPENSE ----------
@expense_bp.route("/<int:expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    # Only allow the creator to delete
    if expense.created_by != current_user.id:
        return jsonify({"error": "Not authorized"}), 403

    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted"}), 200 