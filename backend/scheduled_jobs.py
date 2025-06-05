from celery_app import celery
from database import db
from models import Users, Tasks, Projects, CustomStatus, TeamMembers
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
import logging
import smtplib
import base64
import io
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Set up logging
logger = logging.getLogger(__name__)

# Email configuration (add these to your .env file)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)


def send_email(to_email, subject, html_content, attachments=None):
    """
    Send HTML email using SMTP
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email

        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                msg.attach(attachment)

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def get_task_summary_for_user(user_id):
    """
    Get task summary for a user: due today, overdue, upcoming
    """
    today = date.today()
    three_days_from_now = today + timedelta(days=3)
    
    # Get user's assigned tasks
    base_query = Tasks.query.filter_by(assigned_to=user_id)
    
    # Tasks due today
    due_today = base_query.filter(Tasks.due_date == today).all()
    
    # Overdue tasks
    overdue = base_query.filter(Tasks.due_date < today).all()
    
    # Upcoming tasks (next 3 days, excluding today)
    upcoming = base_query.filter(
        and_(Tasks.due_date > today, Tasks.due_date <= three_days_from_now)
    ).all()
    
    return {
        'due_today': due_today,
        'overdue': overdue,
        'upcoming': upcoming,
        'total_count': len(due_today) + len(overdue) + len(upcoming)
    }


def render_daily_reminder_email(user, task_summary):
    """
    Render HTML email template for daily task reminders
    """
    due_today = task_summary['due_today']
    overdue = task_summary['overdue']
    upcoming = task_summary['upcoming']
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3B82F6; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #f8f9fa; padding: 20px; }}
            .section {{ margin-bottom: 25px; }}
            .task-list {{ background-color: white; border-radius: 6px; padding: 15px; margin-top: 10px; }}
            .task-item {{ padding: 10px; border-left: 4px solid #e5e7eb; margin-bottom: 8px; background-color: #f9fafb; }}
            .overdue {{ border-left-color: #ef4444; }}
            .due-today {{ border-left-color: #f59e0b; }}
            .upcoming {{ border-left-color: #10b981; }}
            .task-title {{ font-weight: bold; color: #1f2937; }}
            .task-meta {{ font-size: 12px; color: #6b7280; margin-top: 5px; }}
            .footer {{ background-color: #374151; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-item {{ text-align: center; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #3B82F6; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📋 Daily Task Summary</h1>
            <p>Good morning, {user.name or user.email}! Here's your task overview for today.</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(overdue)}</div>
                    <div>Overdue</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(due_today)}</div>
                    <div>Due Today</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(upcoming)}</div>
                    <div>Upcoming</div>
                </div>
            </div>
    """
    
    # Overdue tasks section
    if overdue:
        html_template += """
            <div class="section">
                <h2 style="color: #ef4444;">🚨 Overdue Tasks</h2>
                <div class="task-list">
        """
        for task in overdue:
            html_template += f"""
                <div class="task-item overdue">
                    <div class="task-title">{task.title}</div>
                    <div class="task-meta">
                        Due: {task.due_date.strftime('%B %d, %Y')} • 
                        Project: {task.project.name} • 
                        Priority: {task.priority}
                    </div>
                </div>
            """
        html_template += "</div></div>"
    
    # Due today section
    if due_today:
        html_template += """
            <div class="section">
                <h2 style="color: #f59e0b;">⏰ Due Today</h2>
                <div class="task-list">
        """
        for task in due_today:
            html_template += f"""
                <div class="task-item due-today">
                    <div class="task-title">{task.title}</div>
                    <div class="task-meta">
                        Project: {task.project.name} • 
                        Priority: {task.priority}
                    </div>
                </div>
            """
        html_template += "</div></div>"
    
    # Upcoming tasks section
    if upcoming:
        html_template += """
            <div class="section">
                <h2 style="color: #10b981;">📅 Upcoming (Next 3 Days)</h2>
                <div class="task-list">
        """
        for task in upcoming:
            html_template += f"""
                <div class="task-item upcoming">
                    <div class="task-title">{task.title}</div>
                    <div class="task-meta">
                        Due: {task.due_date.strftime('%B %d, %Y')} • 
                        Project: {task.project.name} • 
                        Priority: {task.priority}
                    </div>
                </div>
            """
        html_template += "</div></div>"
    
    html_template += """
        </div>
        
        <div class="footer">
            <p>📧 SynergySphere Team Collaboration Platform</p>
            <p>Stay organized, stay productive!</p>
        </div>
    </body>
    </html>
    """
    
    return html_template


@celery.task(bind=True)
def send_daily_reminders(self):
    """
    Send daily task reminders to all users
    Scheduled to run every day at 8 AM
    """
    logger.info("Starting daily task reminders job")
    
    try:
        # Get all active users
        users = Users.query.filter_by(active=True).all()
        
        sent_count = 0
        skipped_count = 0
        
        for user in users:
            try:
                # Get task summary for this user
                task_summary = get_task_summary_for_user(user.id)
                
                # Skip if user has no tasks
                if task_summary['total_count'] == 0:
                    logger.info(f"Skipping user {user.email} - no tasks found")
                    skipped_count += 1
                    continue
                
                # Render email template
                html_content = render_daily_reminder_email(user, task_summary)
                
                # Send email
                subject = f"📋 Daily Task Summary - {task_summary['total_count']} tasks need attention"
                
                if send_email(user.email, subject, html_content):
                    sent_count += 1
                else:
                    logger.error(f"Failed to send daily reminder to {user.email}")
                    
            except Exception as e:
                logger.error(f"Error processing daily reminder for user {user.email}: {str(e)}")
        
        result_message = f"Daily reminders job completed. Sent: {sent_count}, Skipped: {skipped_count}"
        logger.info(result_message)
        return result_message
        
    except Exception as e:
        error_message = f"Daily reminders job failed: {str(e)}"
        logger.error(error_message)
        raise self.retry(countdown=300, max_retries=3)  # Retry after 5 minutes


def generate_user_activity_data(user_id):
    """
    Generate monthly activity data for a user
    """
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get user's projects
    user_projects = db.session.query(Projects).join(TeamMembers).filter(
        TeamMembers.user_id == user_id
    ).all()
    
    project_names = [p.name for p in user_projects]
    
    # Get tasks for this user in the date range
    user_tasks = Tasks.query.filter(
        and_(
            Tasks.assigned_to == user_id,
            Tasks.created_at >= start_date
        )
    ).all()
    
    # Calculate completion metrics
    completed_tasks = [t for t in user_tasks if t.custom_status and 'done' in t.custom_status.name.lower()]
    total_tasks = len(user_tasks)
    
    # Calculate average completion time for completed tasks
    completion_times = []
    for task in completed_tasks:
        if task.created_at and task.updated_at:
            time_diff = (task.updated_at - task.created_at).days
            completion_times.append(max(1, time_diff))  # Minimum 1 day
    
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Status breakdown
    status_counts = {}
    for task in user_tasks:
        status_name = task.custom_status.name if task.custom_status else 'No Status'
        status_counts[status_name] = status_counts.get(status_name, 0) + 1
    
    return {
        'completed_tasks_count': len(completed_tasks),
        'total_tasks_count': total_tasks,
        'avg_completion_time': round(avg_completion_time, 1),
        'active_projects': project_names,
        'status_breakdown': status_counts,
        'date_range': f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    }


def create_pie_chart(status_data):
    """
    Create a pie chart for task status breakdown
    Returns base64 encoded image
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        if not status_data:
            return None
        
        labels = list(status_data.keys())
        sizes = list(status_data.values())
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
        
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(labels)], 
                                         autopct='%1.1f%%', startangle=90)
        
        ax.set_title('Task Status Breakdown', fontsize=16, fontweight='bold')
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_data
        
    except ImportError:
        logger.warning("matplotlib not available, skipping chart generation")
        return None
    except Exception as e:
        logger.error(f"Error creating pie chart: {str(e)}")
        return None


def render_monthly_report_email(user, activity_data):
    """
    Render HTML email template for monthly activity report
    """
    chart_data = create_pie_chart(activity_data['status_breakdown'])
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3B82F6, #1E40AF); color: white; padding: 25px; border-radius: 12px 12px 0 0; }}
            .content {{ background-color: #f8f9fa; padding: 25px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
            .metric-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric-number {{ font-size: 28px; font-weight: bold; color: #3B82F6; }}
            .metric-label {{ color: #6b7280; font-size: 14px; margin-top: 5px; }}
            .section {{ margin: 25px 0; background: white; padding: 20px; border-radius: 8px; }}
            .projects-list {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
            .project-tag {{ background: #e0f2fe; color: #0277bd; padding: 6px 12px; border-radius: 20px; font-size: 12px; }}
            .chart-container {{ text-align: center; margin: 20px 0; }}
            .footer {{ background-color: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 12px 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Monthly Activity Report</h1>
            <p>Hello {user.name or user.email}! Here's your productivity summary for {activity_data['date_range']}.</p>
        </div>
        
        <div class="content">
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-number">{activity_data['completed_tasks_count']}</div>
                    <div class="metric-label">Tasks Completed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{activity_data['total_tasks_count']}</div>
                    <div class="metric-label">Total Tasks</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{activity_data['avg_completion_time']}</div>
                    <div class="metric-label">Avg. Days to Complete</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{len(activity_data['active_projects'])}</div>
                    <div class="metric-label">Active Projects</div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Active Projects</h2>
                <div class="projects-list">
    """
    
    for project in activity_data['active_projects']:
        html_template += f'<span class="project-tag">{project}</span>'
    
    html_template += """
                </div>
            </div>
    """
    
    # Add chart if available
    if chart_data:
        html_template += f"""
            <div class="section">
                <h2>📈 Task Status Breakdown</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,{chart_data}" alt="Task Status Chart" style="max-width: 100%; height: auto;">
                </div>
            </div>
        """
    else:
        # Fallback text-based status breakdown
        html_template += """
            <div class="section">
                <h2>📈 Task Status Breakdown</h2>
                <div style="margin-top: 15px;">
        """
        for status, count in activity_data['status_breakdown'].items():
            html_template += f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                    <span>{status}</span>
                    <span style="font-weight: bold; color: #3B82F6;">{count}</span>
                </div>
            """
        html_template += "</div></div>"
    
    html_template += """
        </div>
        
        <div class="footer">
            <p>🌟 Keep up the great work!</p>
            <p>SynergySphere Team Collaboration Platform</p>
        </div>
    </body>
    </html>
    """
    
    return html_template


@celery.task(bind=True)
def send_monthly_reports(self):
    """
    Send monthly activity reports to all users
    Scheduled to run on the 1st of each month
    """
    logger.info("Starting monthly activity reports job")
    
    try:
        # Get all active users
        users = Users.query.filter_by(active=True).all()
        
        sent_count = 0
        skipped_count = 0
        
        for user in users:
            try:
                # Generate activity data for this user
                activity_data = generate_user_activity_data(user.id)
                
                # Skip if user has no activity
                if activity_data['total_tasks_count'] == 0:
                    logger.info(f"Skipping user {user.email} - no activity found")
                    skipped_count += 1
                    continue
                
                # Render email template
                html_content = render_monthly_report_email(user, activity_data)
                
                # Send email
                subject = f"📊 Monthly Activity Report - {activity_data['completed_tasks_count']} tasks completed"
                
                if send_email(user.email, subject, html_content):
                    sent_count += 1
                else:
                    logger.error(f"Failed to send monthly report to {user.email}")
                    
            except Exception as e:
                logger.error(f"Error processing monthly report for user {user.email}: {str(e)}")
        
        result_message = f"Monthly reports job completed. Sent: {sent_count}, Skipped: {skipped_count}"
        logger.info(result_message)
        return result_message
        
    except Exception as e:
        error_message = f"Monthly reports job failed: {str(e)}"
        logger.error(error_message)
        raise self.retry(countdown=600, max_retries=3)  # Retry after 10 minutes


# Manual trigger functions for testing
@celery.task
def test_daily_reminders():
    """Test function to manually trigger daily reminders"""
    return send_daily_reminders()


@celery.task  
def test_monthly_reports():
    """Test function to manually trigger monthly reports"""
    return send_monthly_reports() 