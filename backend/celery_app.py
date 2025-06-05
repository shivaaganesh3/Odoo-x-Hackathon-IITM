from celery import Celery
from celery.schedules import crontab
from flask import Flask
import logging
import os
from config import Config


def create_celery_app(app=None):
    """
    Create and configure Celery app with Flask integration
    """
    if app is None:
        # Create Flask app for standalone Celery usage
        app = Flask(__name__)
        app.config.from_object(Config)
    
    # Redis configuration for broker and backend
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Create Celery instance
    celery = Celery(
        app.import_name,
        broker=redis_url,
        backend=redis_url,
        include=['scheduled_jobs']  # Include our scheduled jobs module
    )
    
    # Update Celery config
    celery.conf.update(
        # Task serialization
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task routing and scheduling
        task_routes={
            'scheduled_jobs.send_daily_reminders': {'queue': 'scheduled'},
            'scheduled_jobs.send_monthly_reports': {'queue': 'scheduled'},
        },
        
        # Beat schedule for periodic tasks
        beat_schedule={
            'daily-task-reminders': {
                'task': 'scheduled_jobs.send_daily_reminders',
                'schedule': 60.0 * 60.0 * 24.0,  # 24 hours in seconds
                # Uncomment next line to set specific time (8 AM UTC)
                # 'schedule': crontab(hour=8, minute=0),
            },
            'monthly-activity-reports': {
                'task': 'scheduled_jobs.send_monthly_reports',
                'schedule': 60.0 * 60.0 * 24.0 * 30.0,  # 30 days in seconds
                # Uncomment next line to run on 1st of every month at 9 AM UTC
                # 'schedule': crontab(hour=9, minute=0, day_of_month=1),
            },
        },
        
        # Worker configuration
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        
        # Logging
        worker_log_level='INFO',
    )
    
    # Set up Flask app context for Celery tasks
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return celery


# Create the Celery app instance for worker processes
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database with app context
from database import db
db.init_app(app)

# Create Celery instance
celery = create_celery_app(app)


if __name__ == '__main__':
    # Start Celery worker
    celery.start() 