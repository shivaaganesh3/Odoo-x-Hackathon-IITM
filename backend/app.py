from flask import Flask
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore

from database import db
from models import Users, Roles
from routes.auth import auth_bp
from routes.project import project_bp
from routes.task import task_bp
from routes.team import team_bp
from routes.discussion import discussion_bp
from routes.custom_status import custom_status_bp
from routes.notifications import notifications_bp
from routes.analytics import analytics_bp
from routes.budget import budget_bp
from routes.expense import expense_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app, 
         supports_credentials=True, 
         origins=["http://localhost:5173", "http://localhost:5174"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


    db.init_app(app)

    # Flask-Security setup
    user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
    security = Security(app, user_datastore)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(project_bp, url_prefix='/api/projects')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(team_bp, url_prefix='/api/team')
    app.register_blueprint(discussion_bp, url_prefix='/api/discussions')
    app.register_blueprint(custom_status_bp, url_prefix='/api/custom-status')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(budget_bp, url_prefix='/api/budget')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
