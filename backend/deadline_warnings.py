from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from models import Tasks, Notifications, Users, CustomStatus, Projects, TeamMembers
from database import db
from task_prioritization import TaskPrioritizationEngine
import json

class DeadlineWarningEngine:
    """
    Proactive Deadline Warning System
    
    Analyzes task progress vs remaining time to predict deadline risks
    and generates smart notifications for users and team members.
    """
    
    # Risk thresholds for deadline warnings
    RISK_THRESHOLDS = {
        'critical': 0.8,  # 80%+ risk of missing deadline
        'high': 0.6,      # 60%+ risk of missing deadline  
        'medium': 0.4,    # 40%+ risk of missing deadline
        'low': 0.2        # 20%+ risk of missing deadline
    }
    
    # Notification frequency limits (hours between notifications)
    NOTIFICATION_FREQUENCY = {
        'critical': 6,    # Every 6 hours
        'high': 12,       # Every 12 hours
        'medium': 24,     # Daily
        'low': 48         # Every 2 days
    }
    
    @staticmethod
    def calculate_progress_score(task: Tasks) -> float:
        """
        Calculate task progress based on status transitions
        
        Returns:
            float: Progress score from 0.0 to 1.0 (1.0 = completed)
        """
        if not task.custom_status:
            return 0.1  # Default low progress if no status
        
        status_name = task.custom_status.name.lower()
        
        # Standard progress mapping based on common status patterns
        progress_mapping = {
            'to-do': 0.0,
            'todo': 0.0,
            'backlog': 0.0,
            'planned': 0.1,
            'in progress': 0.5,
            'in-progress': 0.5,
            'working': 0.5,
            'active': 0.5,
            'development': 0.4,
            'testing': 0.7,
            'review': 0.8,
            'qa': 0.7,
            'done': 1.0,
            'completed': 1.0,
            'finished': 1.0,
            'closed': 1.0,
            'deployed': 1.0
        }
        
        # Check for exact matches first
        if status_name in progress_mapping:
            return progress_mapping[status_name]
        
        # Check for partial matches
        for status_key, progress in progress_mapping.items():
            if status_key in status_name:
                return progress
        
        # Default progress for unknown statuses
        return 0.2
    
    @staticmethod
    def calculate_deadline_risk(task: Tasks) -> Tuple[float, str]:
        """
        Calculate deadline risk based on progress vs time remaining
        
        Returns:
            Tuple[float, str]: (risk_score, risk_level)
                risk_score: 0.0 to 1.0 (1.0 = highest risk)
                risk_level: 'low', 'medium', 'high', 'critical'
        """
        if not task.due_date:
            return 0.0, 'low'  # No deadline = no risk
        
        today = datetime.utcnow().date()
        days_remaining = (task.due_date - today).days
        
        # If overdue, maximum risk
        if days_remaining < 0:
            return 1.0, 'critical'
        
        # If due today/tomorrow with low progress, high risk
        if days_remaining <= 1:
            progress = DeadlineWarningEngine.calculate_progress_score(task)
            if progress < 0.8:
                return 0.9, 'critical'
            else:
                return 0.3, 'medium'
        
        # Calculate expected progress based on time elapsed
        if hasattr(task, 'created_at') and task.created_at:
            total_days = (task.due_date - task.created_at.date()).days
            elapsed_days = (today - task.created_at.date()).days
            
            if total_days > 0:
                expected_progress = min(elapsed_days / total_days, 0.9)  # Cap at 90%
            else:
                expected_progress = 0.5  # Default for same-day tasks
        else:
            # Fallback: assume linear progress expectation
            if days_remaining <= 3:
                expected_progress = 0.7
            elif days_remaining <= 7:
                expected_progress = 0.5
            else:
                expected_progress = 0.3
        
        actual_progress = DeadlineWarningEngine.calculate_progress_score(task)
        progress_gap = expected_progress - actual_progress
        
        # Risk factors
        time_pressure = max(0, (7 - days_remaining) / 7)  # Higher risk as deadline approaches
        progress_risk = max(0, progress_gap)  # Higher risk if behind expected progress
        effort_risk = (task.effort_score or 3) / 5.0  # Higher risk for complex tasks
        
        # Weighted risk calculation
        risk_score = (
            time_pressure * 0.4 +      # 40% weight for time pressure
            progress_risk * 0.4 +      # 40% weight for progress gap
            effort_risk * 0.2          # 20% weight for task complexity
        )
        
        # Determine risk level
        if risk_score >= DeadlineWarningEngine.RISK_THRESHOLDS['critical']:
            risk_level = 'critical'
        elif risk_score >= DeadlineWarningEngine.RISK_THRESHOLDS['high']:
            risk_level = 'high'
        elif risk_score >= DeadlineWarningEngine.RISK_THRESHOLDS['medium']:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return round(risk_score, 2), risk_level
    
    @staticmethod
    def should_send_notification(task: Tasks, risk_level: str) -> bool:
        """
        Check if we should send a notification based on frequency limits
        
        Returns:
            bool: True if notification should be sent
        """
        if risk_level == 'low':
            return False  # Don't notify for low risk
        
        # Check if there's a recent notification for this task
        frequency_hours = DeadlineWarningEngine.NOTIFICATION_FREQUENCY[risk_level]
        cutoff_time = datetime.utcnow() - timedelta(hours=frequency_hours)
        
        recent_notification = Notifications.query.filter(
            Notifications.task_id == task.id,
            Notifications.type == 'deadline_warning',
            Notifications.created_at >= cutoff_time
        ).first()
        
        return recent_notification is None
    
    @staticmethod
    def create_deadline_notification(task: Tasks, risk_score: float, risk_level: str) -> Optional[Notifications]:
        """
        Create a deadline warning notification
        
        Returns:
            Notifications: Created notification object or None
        """
        if not DeadlineWarningEngine.should_send_notification(task, risk_level):
            return None
        
        # Determine recipients (assignee and/or team members)
        recipients = []
        if task.assigned_to:
            recipients.append(task.assigned_to)
        else:
            # If unassigned, notify all team members
            team_members = TeamMembers.query.filter_by(project_id=task.project_id).all()
            recipients.extend([member.user_id for member in team_members])
        
        # Remove duplicates
        recipients = list(set(recipients))
        
        # Generate notification content based on risk level
        risk_messages = {
            'critical': "🚨 URGENT: Task deadline at critical risk!",
            'high': "⚠️ HIGH RISK: Task may miss deadline",
            'medium': "⚡ ATTENTION: Task progress behind schedule"
        }
        
        title = risk_messages.get(risk_level, "Task deadline reminder")
        
        progress = DeadlineWarningEngine.calculate_progress_score(task)
        days_remaining = (task.due_date - datetime.utcnow().date()).days if task.due_date else 0
        
        if days_remaining < 0:
            time_text = f"overdue by {abs(days_remaining)} day(s)"
        elif days_remaining == 0:
            time_text = "due today"
        elif days_remaining == 1:
            time_text = "due tomorrow"
        else:
            time_text = f"due in {days_remaining} day(s)"
        
        message = f"""
Task "{task.title}" is at {risk_level} risk of missing its deadline.

📊 Current Progress: {int(progress * 100)}%
📅 Deadline: {time_text}
🎯 Risk Score: {risk_score * 100:.0f}%
📈 Priority: {task.priority}

Project: {task.project.name if task.project else 'Unknown'}
        """.strip()
        
        # Create notifications for all recipients
        notifications = []
        for user_id in recipients:
            notification = Notifications(
                user_id=user_id,
                title=title,
                message=message,
                type='deadline_warning',
                task_id=task.id,
                project_id=task.project_id,
                priority=risk_level,
                next_reminder_at=datetime.utcnow() + timedelta(
                    hours=DeadlineWarningEngine.NOTIFICATION_FREQUENCY[risk_level]
                )
            )
            db.session.add(notification)
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def analyze_all_tasks(cls) -> Dict:
        """
        Analyze all active tasks for deadline risks and create notifications
        
        Returns:
            Dict: Analysis summary
        """
        # Get all tasks with deadlines that are not completed
        completed_statuses = ['done', 'completed', 'finished', 'closed', 'deployed']
        
        active_tasks = db.session.query(Tasks).join(CustomStatus).filter(
            Tasks.due_date.isnot(None),
            ~CustomStatus.name.ilike('%done%'),
            ~CustomStatus.name.ilike('%completed%'),
            ~CustomStatus.name.ilike('%finished%'),
            ~CustomStatus.name.ilike('%closed%'),
            ~CustomStatus.name.ilike('%deployed%')
        ).all()
        
        analysis_summary = {
            'total_tasks_analyzed': len(active_tasks),
            'risk_breakdown': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'notifications_created': 0,
            'overdue_tasks': 0
        }
        
        for task in active_tasks:
            risk_score, risk_level = cls.calculate_deadline_risk(task)
            analysis_summary['risk_breakdown'][risk_level] += 1
            
            if task.due_date and task.due_date < datetime.utcnow().date():
                analysis_summary['overdue_tasks'] += 1
            
            # Create notifications for medium+ risk tasks
            if risk_level in ['medium', 'high', 'critical']:
                notifications = cls.create_deadline_notification(task, risk_score, risk_level)
                if notifications:
                    analysis_summary['notifications_created'] += len(notifications)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating deadline notifications: {e}")
        
        return analysis_summary
    
    @classmethod
    def get_task_deadline_insights(cls, task_id: int) -> Dict:
        """
        Get detailed deadline insights for a specific task
        
        Returns:
            Dict: Detailed task deadline analysis
        """
        task = Tasks.query.get(task_id)
        if not task:
            return {'error': 'Task not found'}
        
        risk_score, risk_level = cls.calculate_deadline_risk(task)
        progress = cls.calculate_progress_score(task)
        
        today = datetime.utcnow().date()
        days_remaining = (task.due_date - today).days if task.due_date else None
        
        insights = {
            'task_id': task.id,
            'title': task.title,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'progress_score': progress,
            'days_remaining': days_remaining,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'current_status': task.custom_status.name if task.custom_status else None,
            'priority': task.priority,
            'effort_score': task.effort_score,
            'recommendations': cls._generate_recommendations(task, risk_score, risk_level, progress)
        }
        
        return insights
    
    @staticmethod
    def _generate_recommendations(task: Tasks, risk_score: float, risk_level: str, progress: float) -> List[str]:
        """Generate actionable recommendations based on deadline analysis"""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.append("🚨 Immediate action required - consider escalating or reassigning")
            recommendations.append("📞 Schedule urgent team discussion about this task")
            
        if progress < 0.3 and task.due_date:
            days_remaining = (task.due_date - datetime.utcnow().date()).days
            if days_remaining <= 3:
                recommendations.append("⚡ Break task into smaller, actionable subtasks")
                recommendations.append("🤝 Consider pair programming or additional resources")
        
        if task.effort_score and task.effort_score >= 4:
            recommendations.append("🧩 Complex task - ensure clear requirements and milestones")
            
        if not task.assigned_to:
            recommendations.append("👤 Assign task to a specific team member for accountability")
            
        if task.blocked_by:
            recommendations.append("🔓 Review and resolve blocking dependencies first")
            
        if risk_level in ['high', 'critical'] and progress < 0.5:
            recommendations.append("📊 Consider updating task status to reflect current progress")
            recommendations.append("💬 Add progress update to project discussions")
        
        return recommendations 