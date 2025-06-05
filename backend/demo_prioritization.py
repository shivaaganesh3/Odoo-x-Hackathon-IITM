#!/usr/bin/env python3
"""
Demo Script for Smart Task Prioritization Engine
Creates sample tasks with different priority factors to showcase the engine.
"""

from datetime import datetime, date, timedelta
import json
from app import create_app
from database import db
from models import Tasks, Projects, Users, CustomStatus, TeamMembers
from task_prioritization import TaskPrioritizationEngine

def create_demo_data():
    """Create sample data to demonstrate the prioritization engine"""
    app = create_app()
    with app.app_context():
        print("🎯 Smart Task Prioritization Engine Demo")
        print("=" * 50)
        
        # Get or create a demo project
        demo_project = Projects.query.filter_by(name='Smart Priority Demo').first()
        if not demo_project:
            # Get the first user as project creator
            user = Users.query.first()
            if not user:
                print("❌ No users found. Please create a user first.")
                return
            
            demo_project = Projects(
                name='Smart Priority Demo',
                description='Demonstration project for Smart Task Prioritization Engine',
                created_by=user.id
            )
            db.session.add(demo_project)
            db.session.flush()
            
            # Create default statuses
            statuses = [
                {'name': 'To Do', 'color': '#6b7280', 'position': 0, 'is_default': True},
                {'name': 'In Progress', 'color': '#3b82f6', 'position': 1, 'is_default': False},
                {'name': 'Review', 'color': '#f59e0b', 'position': 2, 'is_default': False},
                {'name': 'Done', 'color': '#10b981', 'position': 3, 'is_default': False}
            ]
            
            for status_data in statuses:
                status = CustomStatus(
                    name=status_data['name'],
                    color=status_data['color'],
                    position=status_data['position'],
                    is_default=status_data.get('is_default', False),
                    project_id=demo_project.id
                )
                db.session.add(status)
            
            # Add user as team member
            team_member = TeamMembers(
                user_id=user.id,
                project_id=demo_project.id
            )
            db.session.add(team_member)
            
            db.session.commit()
            print(f"✅ Created demo project: {demo_project.name}")
        
        # Get default status
        default_status = CustomStatus.query.filter_by(
            project_id=demo_project.id, 
            is_default=True
        ).first()
        
        # Create sample tasks with varying priority factors
        sample_tasks = [
            {
                'title': '🚨 Critical Bug in Production',
                'description': 'Payment system is down, affecting all customers',
                'due_date': date.today(),  # Due today - maximum urgency
                'effort_score': 2,  # Easy fix
                'impact_score': 5,  # Critical impact
                'dependency_map': [],
                'blocked_by': []
            },
            {
                'title': '🔧 Refactor Legacy Authentication System',
                'description': 'Modernize the auth system for better security',
                'due_date': date.today() + timedelta(days=30),  # Due in a month
                'effort_score': 5,  # Very hard
                'impact_score': 4,  # High impact
                'dependency_map': [],
                'blocked_by': []
            },
            {
                'title': '📊 Generate Weekly Reports',
                'description': 'Create automated weekly performance reports',
                'due_date': date.today() + timedelta(days=2),  # Due in 2 days
                'effort_score': 1,  # Very easy
                'impact_score': 2,  # Low impact
                'dependency_map': [],
                'blocked_by': []
            },
            {
                'title': '🎨 UI Design for New Feature',
                'description': 'Design user interface for the new dashboard',
                'due_date': date.today() + timedelta(days=7),  # Due in a week
                'effort_score': 3,  # Medium effort
                'impact_score': 3,  # Medium impact
                'dependency_map': [],  # Will be updated after creation
                'blocked_by': []
            },
            {
                'title': '⚙️ Implement New Dashboard Backend',
                'description': 'Build API endpoints for the new dashboard',
                'due_date': date.today() + timedelta(days=14),  # Due in 2 weeks
                'effort_score': 4,  # Hard
                'impact_score': 3,  # Medium impact
                'dependency_map': [],
                'blocked_by': []  # Will be updated to be blocked by UI Design
            },
            {
                'title': '📝 Update Documentation',
                'description': 'Update API documentation with latest changes',
                'due_date': date.today() + timedelta(days=21),  # Due in 3 weeks
                'effort_score': 2,  # Easy
                'impact_score': 1,  # Low impact
                'dependency_map': [],
                'blocked_by': []
            },
            {
                'title': '🧪 Write Unit Tests',
                'description': 'Add comprehensive unit tests for new features',
                'due_date': date.today() + timedelta(days=10),  # Due in 10 days
                'effort_score': 3,  # Medium effort
                'impact_score': 2,  # Medium-low impact
                'dependency_map': [],
                'blocked_by': []  # Will be blocked by backend implementation
            }
        ]
        
        # Get or create user for assignment
        user = Users.query.first()
        created_tasks = []
        
        # Clear existing demo tasks
        existing_tasks = Tasks.query.filter_by(project_id=demo_project.id).all()
        for task in existing_tasks:
            db.session.delete(task)
        db.session.commit()
        
        print(f"\n📝 Creating {len(sample_tasks)} sample tasks...")
        
        # Create tasks
        for task_data in sample_tasks:
            task = Tasks(
                title=task_data['title'],
                description=task_data['description'],
                due_date=task_data['due_date'],
                effort_score=task_data['effort_score'],
                impact_score=task_data['impact_score'],
                dependency_map=task_data['dependency_map'],
                blocked_by=task_data['blocked_by'],
                project_id=demo_project.id,
                status_id=default_status.id,
                assigned_to=user.id
            )
            db.session.add(task)
            created_tasks.append(task)
        
        db.session.flush()  # Get task IDs
        
        # Set up dependencies after all tasks are created
        ui_design_task = next(t for t in created_tasks if 'UI Design' in t.title)
        backend_task = next(t for t in created_tasks if 'Backend' in t.title)
        test_task = next(t for t in created_tasks if 'Unit Tests' in t.title)
        
        # UI Design blocks Backend Implementation
        ui_design_task.dependency_map = [backend_task.id]
        backend_task.blocked_by = [ui_design_task.id]
        
        # Backend Implementation blocks Unit Tests
        backend_task.dependency_map = [test_task.id]
        test_task.blocked_by = [backend_task.id]
        
        db.session.commit()
        
        print("✅ Sample tasks created successfully!")
        
        # Calculate priorities for all tasks
        print("\n🧠 Calculating smart priorities...")
        updated_tasks = TaskPrioritizationEngine.update_project_task_priorities(demo_project.id)
        
        print(f"✅ Updated priorities for {len(updated_tasks)} tasks")
        
        # Display results
        print("\n📊 Smart Priority Results:")
        print("-" * 70)
        
        # Get tasks sorted by priority
        sorted_tasks = Tasks.query.filter_by(project_id=demo_project.id).order_by(
            Tasks.priority_score.desc()
        ).all()
        
        for i, task in enumerate(sorted_tasks, 1):
            # Get priority insights
            insights = TaskPrioritizationEngine.get_priority_insights(task)
            
            print(f"\n{i}. {task.title}")
            print(f"   🎯 Priority: {task.priority} (Score: {task.priority_score}/10)")
            print(f"   📅 Due: {task.due_date}")
            print(f"   💪 Effort: {task.effort_score}/5 | 🚀 Impact: {task.impact_score}/5")
            
            if task.dependency_map:
                print(f"   🚫 Blocks {len(task.dependency_map)} task(s)")
            if task.blocked_by:
                print(f"   ⏸️  Blocked by {len(task.blocked_by)} task(s)")
            
            # Show detailed scoring
            scores = insights['scores']
            print(f"   🔍 Factors: U:{scores['urgency']['value']:.1f} "
                  f"E:{scores['effort']['value']:.1f} "
                  f"D:{scores['dependency']['value']:.1f} "
                  f"I:{scores['impact']['value']:.1f}")
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\nKey Insights:")
        print("• Tasks are ranked by multi-factor priority score")
        print("• Urgency (35%), Dependencies (25%), Effort (20%), Impact (20%)")
        print("• Overdue/immediate tasks get highest urgency scores")
        print("• Tasks blocking others get higher dependency scores")
        print("• Easier tasks (lower effort) get higher priority")
        print("• Higher impact tasks get higher priority")
        
        return demo_project.id

if __name__ == "__main__":
    create_demo_data() 