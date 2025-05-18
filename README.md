# Odoo-x-Hackathon-IITM
# Task Manager - Odoo × IITM Hackathon

A task management web application built with Flask that allows users to create projects, assign tasks, collaborate with team members, and track progress efficiently.

## Features

- **User Authentication**: Register, login, and secure password management
- **Project Management**: Create, edit, and organize projects with deadlines and priority levels
- **Task Tracking**: Create tasks within projects with assignees, deadlines, and priorities
- **Collaboration**: Add team members to projects for seamless collaboration
- **Tag System**: Organize projects and tasks with customizable tags
- **Image Upload**: Add images to projects and tasks for better visualization

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML, CSS (templates)
- **Authentication**: Werkzeug security for password hashing

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/shivaaganesh3/Odoo-x-Hackathon-IITM.git
   cd Odoo-x-Hackathon-IITM
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install flask sqlalchemy werkzeug
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

- **app.py**: Main application file with all routes and controllers
- **database.py**: Database models and schema definitions
- **templates/**: HTML templates for the web interface
- **static/**: Static files (CSS, JavaScript, uploaded images)
- **taskmanager.db**: SQLite database file

## Demo Video

View the demonstration of this project: [Task Manager Demo](https://drive.google.com/file/d/1kkq_DmeGMrK-oWWQUt6Joj2P5Uga8gtB/view?usp=sharing)

## Usage

1. Register a new account or login
2. Create a new project with details, deadline and priority
3. Add tasks to your project
4. Invite collaborators to your project
5. Track progress and manage your tasks efficiently

