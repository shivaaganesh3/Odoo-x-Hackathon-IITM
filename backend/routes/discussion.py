from flask import Blueprint

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/test-discussion')
def test_discussion():
    return {"message": "Discussion route working!"}
