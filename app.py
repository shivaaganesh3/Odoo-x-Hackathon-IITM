from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from database import User, Base, Project, Tag, Task, PriorityEnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Enable CORS for all routes
CORS(app, supports_credentials=True)

# Database setup
engine = create_engine('sqlite:///taskmanager.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db_session.query(User).filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if db_session.query(User).filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db_session.add(new_user)
            db_session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except:
            db_session.rollback()
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db_session.query(User).get(session['user_id'])
    projects = user.projects + user.collaborations
    return render_template('dashboard.html', user_name=session['user_name'], projects=projects, user=user)

@app.route('/project/create', methods=['GET', 'POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        print("=== CREATE PROJECT DEBUG ===")
        print(f"Form data: {dict(request.form)}")
        print(f"Files: {dict(request.files)}")
        
        name = request.form['name']
        description = request.form['description']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d') if request.form['deadline'] else None
        priority = request.form['priority']
        tags = [tag.strip() for tag in request.form['tags'].split(',') if tag.strip()]
        
        print(f"Processed tags: {tags}")
        print(f"Priority: {priority}")
        print(f"Project name: {name}")
        
        project = Project(
            name=name,
            description=description,
            deadline=deadline,
            priority=PriorityEnum[priority],
            owner_id=session['user_id']
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join('static', 'uploads', filename))
                project.image = f'/static/uploads/{filename}'
        
        # Handle tags
        for tag_name in tags:
            tag = db_session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db_session.add(tag)
            project.tags.append(tag)
        
        try:
            db_session.add(project)
            db_session.commit()
            flash('Project created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db_session.rollback()
            flash(f'An error occurred while creating the project: {str(e)}', 'error')
            print(f"ERROR CREATING PROJECT: {str(e)}")  # Debug output
    
    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
def view_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    project = db_session.query(Project).get(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('view_project.html', project=project)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    project = db_session.query(Project).get(project_id)
    if not project or project.owner_id != session['user_id']:
        flash('You do not have permission to edit this project.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        project.name = request.form['name']
        project.description = request.form['description']
        project.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d') if request.form['deadline'] else None
        project.priority = PriorityEnum[request.form['priority']]
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join('static', 'uploads', filename))
                project.image = f'/static/uploads/{filename}'
        
        # Update tags
        new_tags = [tag.strip() for tag in request.form['tags'].split(',') if tag.strip()]
        project.tags.clear()
        for tag_name in new_tags:
            tag = db_session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db_session.add(tag)
            project.tags.append(tag)
        
        try:
            db_session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('view_project', project_id=project.id))
        except:
            db_session.rollback()
            flash('An error occurred while updating the project.', 'error')
    
    return render_template('edit_project.html', project=project)

@app.route('/project/<int:project_id>/add_task', methods=['POST'])
def add_task(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    project = db_session.query(Project).get(project_id)
    if not project or project.owner_id != session['user_id']:
        flash('You do not have permission to add tasks to this project.', 'error')
        return redirect(url_for('dashboard'))
    
    # Validate required fields
    name = request.form.get('name')
    if not name:
        flash('Task name is required.', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Validate assignee is either owner or collaborator
    assignee_id = request.form.get('assignee_id')
    if not assignee_id:
        flash('Assignee is required.', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    assignee = db_session.query(User).get(assignee_id)
    if not assignee or (assignee.id != project.owner_id and assignee not in project.collaborators):
        flash('Invalid assignee selected.', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    try:
        # Process deadline
        deadline = None
        if request.form.get('deadline'):
            try:
                deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
            except ValueError:
                flash('Invalid deadline format.', 'error')
                return redirect(url_for('view_project', project_id=project_id))
        
        # Create new task
        task = Task(
            name=name,
            description=request.form.get('description', ''),
            deadline=deadline,
            priority=PriorityEnum[request.form.get('priority', 'medium')],
            project_id=project_id,
            assignee_id=assignee_id
        )

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                try:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join('static', 'uploads', filename))
                    task.image = f'/static/uploads/{filename}'
                except Exception as e:
                    flash('Error uploading image. Task will be created without an image.', 'warning')

        db_session.add(task)
        db_session.commit()
        flash('Task created successfully!', 'success')
    except Exception as e:
        db_session.rollback()
        flash('An error occurred while adding the task.', 'error')
    
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/project/<int:project_id>/add_collaborator', methods=['POST'])
def add_collaborator(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    project = db_session.query(Project).get(project_id)
    if not project or project.owner_id != session['user_id']:
        flash('You do not have permission to add collaborators to this project.', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    try:
        email = request.form['email']
        user = db_session.query(User).filter_by(email=email).first()
        
        if not user:
            flash('User with this email does not exist.', 'error')
            return redirect(url_for('view_project', project_id=project_id))
        
        if user.id == project.owner_id:
            flash('Project owner cannot be added as a collaborator.', 'error')
            return redirect(url_for('view_project', project_id=project_id))
        
        if user in project.collaborators:
            flash('User is already a collaborator.', 'error')
            return redirect(url_for('view_project', project_id=project_id))
        
        project.collaborators.append(user)
        db_session.commit()
        flash('Collaborator added successfully!', 'success')
    except Exception as e:
        db_session.rollback()
        flash('An error occurred while adding the collaborator.', 'error')
    
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/new_task', methods=['POST'])
def new_task():
    # print("--------------------new task-----------------")
    # print(request.form)
    project_id = request.form.get('project_id')
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    # print("--------------------PROJECT ID-----------------")
    # print("PROJECT ID : ", project_id)

    project = db_session.query(Project).get(project_id)
    # print("--------------------CHECKING-----------------")
    user = db_session.query(User).get(session['user_id'])
    # user = User.query.get(session['user_id'])

    # Check if user is project owner or collaborator
    if user.id != project.owner_id and user not in project.collaborators:
        flash('You do not have permission to create tasks in this project.', 'error')
        return redirect(url_for('dashboard'))

    try:
        # Process form data
        name = request.form.get('name')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        deadline = request.form.get('deadline')
                # Create new task
        new_task = Task(
            name=name,
            description=description,
            priority=PriorityEnum[priority],
            deadline=datetime.strptime(deadline, '%Y-%m-%d') if deadline else None,
            project_id=project_id,
            assignee_id=user.id
        )
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                try:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join('static', 'uploads', filename))
                    new_task.image = f'/static/uploads/{filename}'
                except Exception as e:
                    flash('Error uploading image. Task will be created without an image.', 'warning')



        db_session.add(new_task)
        db_session.commit()
        flash('Task created successfully!', 'success')

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while creating the task.', 'error')

    return redirect(url_for('dashboard'))

# API Routes for Vue Frontend
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    print(f"=== REGISTRATION ATTEMPT ===")
    print(f"Name: {name}")
    print(f"Email: {email}")
    
    # Validate required fields
    if not name or not email or not password:
        return {'error': 'All fields are required'}, 400
    
    # Check if user already exists
    existing_user = db_session.query(User).filter_by(email=email).first()
    if existing_user:
        print(f"User already exists with email: {email}")
        return {'error': 'Email already registered'}, 400
    
    try:
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db_session.add(new_user)
        db_session.commit()
        
        print(f"User created successfully: {name} ({email})")
        return {
            'message': 'Registration successful',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }, 201
        
    except Exception as e:
        db_session.rollback()
        print(f"Registration failed: {str(e)}")
        return {'error': f'Registration failed: {str(e)}'}, 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    print(f"=== LOGIN ATTEMPT ===")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password) if password else 'None'}")
    
    user = db_session.query(User).filter_by(email=email).first()
    print(f"User found: {user is not None}")
    
    if user:
        print(f"User ID: {user.id}, Name: {user.name}")
        password_valid = check_password_hash(user.password_hash, password)
        print(f"Password valid: {password_valid}")
        
        if password_valid:
            session['user_id'] = user.id
            session['user_name'] = user.name
            print(f"Login successful for user: {user.name}")
            return {
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            }, 200
    
    print("Login failed: Invalid email or password")
    return {'error': 'Invalid email or password'}, 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return {'message': 'Logged out successfully'}, 200
@app.route('/api/projects', methods=['POST'])
def api_create_project():
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    data = request.get_json()
    print("=== API CREATE PROJECT DEBUG ===")
    print(f"JSON data: {data}")
    
    try:
        name = data.get('name')
        description = data.get('description', '')
        priority = data.get('priority', 'MEDIUM').lower()
        deadline = None
        if data.get('deadline'):
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
        
        # Handle tags from frontend - could be string or list
        tags_input = data.get('tags', '')
        if isinstance(tags_input, list):
            tags = tags_input
        else:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        print(f"Processed data - name: {name}, priority: {priority}, tags: {tags}")
        
        project = Project(
            name=name,
            description=description,
            deadline=deadline,
            priority=PriorityEnum[priority],
            owner_id=session['user_id']
        )
        
        # Handle tags
        for tag_name in tags:
            tag = db_session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db_session.add(tag)
            project.tags.append(tag)
        
        db_session.add(project)
        db_session.commit()
        
        return {'message': 'Project created successfully', 'id': project.id}, 201
        
    except Exception as e:
        db_session.rollback()
        print(f"ERROR CREATING PROJECT: {str(e)}")
        return {'error': f'Failed to create project: {str(e)}'}, 500

@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    try:
        user = db_session.query(User).get(session['user_id'])
        projects = user.projects + user.collaborations
        
        project_list = []
        for project in projects:
            project_data = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'priority': project.priority.value if project.priority else 'Medium',
                'deadline': project.deadline.strftime('%Y-%m-%d') if project.deadline else None,
                'image': project.image,
                'tags': [tag.name for tag in project.tags],
                'owner_id': project.owner_id,
                'created_at': project.id  # Placeholder, add created_at field to model if needed
            }
            project_list.append(project_data)
        
        return project_list, 200
        
    except Exception as e:
        print(f"ERROR FETCHING PROJECTS: {str(e)}")
        return {'error': f'Failed to fetch projects: {str(e)}'}, 500

@app.route('/api/auth/dashboard-stats', methods=['GET'])
def api_dashboard_stats():
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    try:
        user = db_session.query(User).get(session['user_id'])
        projects = user.projects + user.collaborations
        
        total_projects = len(projects)
        total_tasks = sum(len(project.tasks) for project in projects)
        active_tasks = total_tasks  # Simplified - all tasks are active
        overdue_tasks = 0  # Simplified
        team_members = len(set([project.owner_id for project in projects] + 
                              [collab.id for project in projects for collab in project.collaborators]))
        
        return {
            'total_projects': total_projects,
            'active_tasks': active_tasks,
            'team_members': team_members,
            'overdue_tasks': overdue_tasks
        }, 200
        
    except Exception as e:
        print(f"ERROR FETCHING DASHBOARD STATS: {str(e)}")
        return {'error': f'Failed to fetch stats: {str(e)}'}, 500

@app.route('/api/auth/recent-projects', methods=['GET'])
def api_recent_projects():
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    try:
        user = db_session.query(User).get(session['user_id'])
        projects = (user.projects + user.collaborations)[:5]  # Get first 5 projects
        
        project_list = []
        for project in projects:
            project_data = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'priority': project.priority.value if project.priority else 'Medium',
                'image': project.image,
                'created_at': f"2024-{project.id:02d}-01"  # Placeholder date
            }
            project_list.append(project_data)
        
        return project_list, 200
        
    except Exception as e:
        print(f"ERROR FETCHING RECENT PROJECTS: {str(e)}")
        return {'error': f'Failed to fetch recent projects: {str(e)}'}, 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)