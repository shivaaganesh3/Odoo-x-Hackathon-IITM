# Synergy Sphere - Project Management Platform
## Odoo × IITM Hackathon Submission

A modern, full-stack project management application built with Vue.js frontend and Flask backend. Synergy Sphere enables teams to collaborate efficiently through project management, task tracking, team coordination, and real-time discussions.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure registration, login, and role-based access control
- **Project Management**: Create, update, delete, and organize projects with deadlines and priority levels
- **Task Management**: Full CRUD operations for tasks with status tracking, priority levels, and due dates
- **Team Collaboration**: Add team members to projects and assign tasks
- **Discussion Forums**: Project-based discussions with threaded conversations
- **Smart Task Prioritization**: Intelligent priority scoring system for task management
- **Tag System**: Organize projects and tasks with customizable tags
- **Image Upload**: Add images to projects and tasks for better visualization

### User Roles
- **Regular Users**: Can create projects, manage tasks, and participate in discussions
- **Admin Users**: Additional privileges for system-wide project oversight

## 🏗️ Architecture

### Frontend (`synergy-sphere-frontend/`)
- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite for fast development and optimized builds
- **State Management**: Pinia for reactive state management
- **Routing**: Vue Router for SPA navigation
- **HTTP Client**: Axios for API communication
- **Styling**: Custom CSS with modern design principles

### Backend (`backend/`)
- **Framework**: Flask with modular blueprint architecture
- **Database**: SQLAlchemy ORM with SQLite (development)
- **Authentication**: Flask-Security-Too for user management and role-based access
- **API Design**: RESTful endpoints with JSON responses
- **CORS**: Configured for cross-origin requests from frontend

## 📊 Database Schema

### Core Models
- **Users**: User accounts with authentication and profile information
- **Roles**: Role-based access control (user, admin)
- **Projects**: Project containers with metadata and ownership
- **Tasks**: Task items with status, priority, assignments, and due dates
- **TeamMembers**: Many-to-many relationship between users and projects
- **Discussions**: Threaded discussion system for project communication

## 🛠️ Installation & Setup

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Git**

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/shivaaganesh3/Odoo-x-Hackathon-IITM.git
   cd Odoo-x-Hackathon-IITM
   ```

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python setup_db.py
   python setup_roles.py
   ```

5. **Run the backend server**
   ```bash
   python app.py
   ```
   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd synergy-sphere-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## 📋 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `GET /me` - Get current user info
- `GET /whoami` - User identity verification

### Projects (`/api/projects`)
- `GET /` - List user's projects
- `POST /` - Create new project
- `PUT /:id` - Update project
- `DELETE /:id` - Delete project
- `GET /admin/projects` - Admin: List all projects

### Tasks (`/api/tasks`)
- `GET /` - List user's tasks
- `POST /` - Create new task
- `PUT /:id` - Update task
- `DELETE /:id` - Delete task
- Task status management (To-Do, In Progress, Done)
- Priority scoring and assignment features

### Team Management (`/api/team`)
- Team member assignment and management
- Project-based team coordination

### Discussions (`/api/discussions`)
- Project-based discussion threads
- Real-time communication features

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)
- Database connection settings
- Flask-Security configuration
- CORS settings
- Environment-specific configurations

### Frontend Configuration
- API base URL configuration in `axios.js`
- Vite configuration for build optimization
- Environment variables for different deployment stages

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Security session handling
- **CORS Protection**: Configured cross-origin request handling
- **Input Validation**: Server-side validation for all endpoints
- **Role-based Access**: Granular permissions system

## 🚀 Deployment

### Backend Deployment
1. Set environment variables for production
2. Configure production database
3. Update CORS settings for production domain
4. Deploy using WSGI server (Gunicorn recommended)

### Frontend Deployment
1. Build production assets: `npm run build`
2. Deploy `dist/` folder to web server
3. Configure environment variables for production API

## 📸 Screenshots

The application includes visual documentation with project and task views:
- Project management interface
- Task tracking dashboard
- Team collaboration features

## 🤝 Contributing

This project was developed for the Odoo × IITM Hackathon. For contributions or questions, please create an issue or pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

Developed for the Odoo × IITM Hackathon by the Synergy Sphere team.

---

**Repository**: [https://github.com/shivaaganesh3/Odoo-x-Hackathon-IITM](https://github.com/shivaaganesh3/Odoo-x-Hackathon-IITM)
