from flask import Blueprint, request, jsonify
from flask_security.utils import hash_password, verify_password, login_user
from flask_security import current_user
from models import Users
from database import db
from flask_security import SQLAlchemyUserDatastore
from models import Users, Roles
from flask_security import login_required, current_user

auth_bp = Blueprint('auth', __name__)

# Setup UserDatastore
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)

# ---------- REGISTER ----------
@auth_bp.route('/register', methods=['POST'])
def register_user():
    from uuid import uuid4  # Add this at the top of your file if not already

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        name=name,
        fs_uniquifier=str(uuid4())  # required
    )
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201



# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = Users.query.filter_by(email=email).first()

    if user and verify_password(password, user.password):
        login_user(user)
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }), 200

    return jsonify({"error": "Invalid email or password"}), 401

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }), 200
@auth_bp.route("/whoami", methods=["GET"])
@login_required
def whoami():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    })

