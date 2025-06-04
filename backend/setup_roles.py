from app import create_app
from database import db
from models import Roles
from flask_security import SQLAlchemyUserDatastore
from models import Users, Roles

app = create_app()
app.app_context().push()

# Create admin role
if not Roles.query.filter_by(name="admin").first():
    role = Roles(name="admin", description="Platform admin")
    db.session.add(role)
    db.session.commit()
    print("✅ Admin role created.")
else:
    print("⚠️ Admin role already exists.")