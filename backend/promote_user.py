from app import create_app
from database import db
from models import Users, Roles
from flask_security import SQLAlchemyUserDatastore

app = create_app()
app.app_context().push()

# Setup datastore
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)

# Replace this with the email of the user you want to promote
email_to_promote = "admin@example.com"

# Fetch user and role
user = Users.query.filter_by(email=email_to_promote).first()
admin_role = Roles.query.filter_by(name="admin").first()

if not user:
    print("❌ User not found.")
elif not admin_role:
    print("❌ Admin role not found.")
else:
    user_datastore.add_role_to_user(user, admin_role)
    db.session.commit()
    print(f"✅ User {email_to_promote} promoted to admin.")
