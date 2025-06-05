from datetime import datetime, date
from typing import List, Dict, Optional
from models import Tasks, Projects
from database import db
import json

class TaskPrioritizationEngine:
    """
    Smart Task Prioritization Engine
    
    Multi-factor scoring system that calculates task priority based on:
    1. Urgency Score: Days until deadline (weighted)
    2. Effort Score: Task complexity estimation  
    3. Dependency Score: Number of blocked tasks
    4. Impact Score: Project criticality
    """
    
    # Configuration weights for different factors
    WEIGHTS = {
        'urgency': 0.35,    # 35% weight for deadline urgency
        'effort': 0.20,     # 20% weight for effort (inverse - easier tasks get higher priority)
        'dependency': 0.25, # 25% weight for tasks blocking others
        'impact': 0.20      # 20% weight for project impact
    }
    
    @staticmethod
    def calculate_urgency_score(due_date: Optional[date]) -> float:
        """
        Calculate urgency score based on days until deadline
        
        Returns:
            float: Score from 0-10 (10 = most urgent)
        """
        if not due_date:
            return 2.0  # No deadline = low urgency
        
        today = datetime.utcnow().date()
        days_until_deadline = (due_date - today).days
        
        if days_until_deadline < 0:
            return 10.0  # Overdue = maximum urgency
        elif days_until_deadline == 0:
            return 9.5   # Due today
        elif days_until_deadline == 1:
            return 9.0   # Due tomorrow
        elif days_until_deadline <= 3:
            return 8.0   # Due within 3 days
        elif days_until_deadline <= 7:
            return 6.0   # Due within a week
        elif days_until_deadline <= 14:
            return 4.0   # Due within 2 weeks
        elif days_until_deadline <= 30:
            return 2.5   # Due within a month
        else:
            return 1.0   # Due far in the future
    
    @staticmethod
    def calculate_effort_score(effort_level: int) -> float:
        """
        Calculate effort score (inverse - easier tasks get higher priority)
        
        Args:
            effort_level: 1=Very Easy, 2=Easy, 3=Medium, 4=Hard, 5=Very Hard
            
        Returns:
            float: Score from 0-10 (10 = easiest/highest priority)
        """
        effort_mapping = {
            1: 10.0,  # Very Easy
            2: 8.0,   # Easy  
            3: 6.0,   # Medium
            4: 4.0,   # Hard
            5: 2.0    # Very Hard
        }
        return effort_mapping.get(effort_level, 6.0)
    
    @staticmethod
    def calculate_dependency_score(task_id: int, dependency_map: List[int]) -> float:
        """
        Calculate dependency score based on number of tasks blocked by this task
        
        Args:
            task_id: Current task ID
            dependency_map: List of task IDs that depend on this task
            
        Returns:
            float: Score from 0-10 (10 = blocks many tasks)
        """
        if not dependency_map:
            return 1.0  # No dependencies
        
        blocked_count = len(dependency_map)
        
        if blocked_count >= 5:
            return 10.0
        elif blocked_count >= 3:
            return 8.0
        elif blocked_count >= 2:
            return 6.0
        elif blocked_count == 1:
            return 4.0
        else:
            return 1.0
    
    @staticmethod
    def calculate_impact_score(impact_level: int) -> float:
        """
        Calculate impact score based on project criticality
        
        Args:
            impact_level: 1=Low, 2=Medium-Low, 3=Medium, 4=High, 5=Critical
            
        Returns:
            float: Score from 0-10
        """
        impact_mapping = {
            1: 2.0,   # Low impact
            2: 4.0,   # Medium-Low impact
            3: 6.0,   # Medium impact
            4: 8.0,   # High impact
            5: 10.0   # Critical impact
        }
        return impact_mapping.get(impact_level, 6.0)
    
    @classmethod
    def calculate_priority_score(cls, task: Tasks) -> float:
        """
        Calculate comprehensive priority score for a task
        
        Args:
            task: Task object
            
        Returns:
            float: Priority score (higher = more important)
        """
        urgency_score = cls.calculate_urgency_score(task.due_date)
        effort_score = cls.calculate_effort_score(task.effort_score or 3)
        dependency_score = cls.calculate_dependency_score(task.id, task.dependency_map or [])
        impact_score = cls.calculate_impact_score(task.impact_score or 3)
        
        # Calculate weighted priority score
        priority_score = (
            urgency_score * cls.WEIGHTS['urgency'] +
            effort_score * cls.WEIGHTS['effort'] +
            dependency_score * cls.WEIGHTS['dependency'] +
            impact_score * cls.WEIGHTS['impact']
        )
        
        return round(priority_score, 2)
    
    @classmethod
    def update_task_priority(cls, task: Tasks) -> str:
        """
        Update task priority score and priority label
        
        Args:
            task: Task object to update
            
        Returns:
            str: Priority label (Low, Medium, High, Urgent)
        """
        priority_score = cls.calculate_priority_score(task)
        task.priority_score = priority_score
        
        # Determine priority label based on score
        if priority_score >= 8.0:
            priority_label = "Urgent"
        elif priority_score >= 6.5:
            priority_label = "High"
        elif priority_score >= 4.0:
            priority_label = "Medium"
        else:
            priority_label = "Low"
        
        task.priority = priority_label
        return priority_label
    
    @classmethod
    def update_project_task_priorities(cls, project_id: int) -> List[Dict]:
        """
        Update priority scores for all tasks in a project
        
        Args:
            project_id: Project ID
            
        Returns:
            List[Dict]: Updated task priority information
        """
        tasks = Tasks.query.filter_by(project_id=project_id).all()
        updated_tasks = []
        
        for task in tasks:
            old_priority = task.priority
            old_score = task.priority_score
            
            new_priority = cls.update_task_priority(task)
            
            updated_tasks.append({
                'task_id': task.id,
                'title': task.title,
                'old_priority': old_priority,
                'new_priority': new_priority,
                'old_score': old_score,
                'new_score': task.priority_score
            })
        
        db.session.commit()
        return updated_tasks
    
    @classmethod
    def get_priority_insights(cls, task: Tasks) -> Dict:
        """
        Get detailed priority calculation breakdown for a task
        
        Args:
            task: Task object
            
        Returns:
            Dict: Priority calculation breakdown
        """
        urgency_score = cls.calculate_urgency_score(task.due_date)
        effort_score = cls.calculate_effort_score(task.effort_score or 3)
        dependency_score = cls.calculate_dependency_score(task.id, task.dependency_map or [])
        impact_score = cls.calculate_impact_score(task.impact_score or 3)
        
        return {
            'task_id': task.id,
            'title': task.title,
            'scores': {
                'urgency': {
                    'value': urgency_score,
                    'weight': cls.WEIGHTS['urgency'],
                    'weighted': urgency_score * cls.WEIGHTS['urgency']
                },
                'effort': {
                    'value': effort_score,
                    'weight': cls.WEIGHTS['effort'],
                    'weighted': effort_score * cls.WEIGHTS['effort']
                },
                'dependency': {
                    'value': dependency_score,
                    'weight': cls.WEIGHTS['dependency'],
                    'weighted': dependency_score * cls.WEIGHTS['dependency']
                },
                'impact': {
                    'value': impact_score,
                    'weight': cls.WEIGHTS['impact'],
                    'weighted': impact_score * cls.WEIGHTS['impact']
                }
            },
            'total_score': task.priority_score,
            'priority_label': task.priority,
            'blocking_tasks': len(task.dependency_map or []),
            'blocked_by_tasks': len(task.blocked_by or [])
        } 