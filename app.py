from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import User, Base, Project, Tag, Task, PriorityEnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

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
    return render_template('dashboard.html', user_name=session['user_name'], projects=projects)

@app.route('/project/create', methods=['GET', 'POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d') if request.form['deadline'] else None
        priority = request.form['priority']
        tags = [tag.strip() for tag in request.form['tags'].split(',') if tag.strip()]
        
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
            flash('An error occurred while creating the project.', 'error')
    
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
        # Create new task
        task = Task(
            name=request.form['name'],
            description=request.form.get('description'),
            deadline=datetime.strptime(request.form['deadline'], '%Y-%m-%d') if request.form.get('deadline') else None,
            priority=PriorityEnum[request.form['priority']],
            project_id=project_id,
            assignee_id=assignee_id
        )

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join('static', 'uploads', filename))
                task.image = f'/static/uploads/{filename}'

        db_session.add(task)
        db_session.commit()
        flash('Task created successfully!', 'success')
        flash('Task added successfully!', 'success')
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)