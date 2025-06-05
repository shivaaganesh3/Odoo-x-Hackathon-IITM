# 🎯 Synergy Sphere - Smart Project Management System

A comprehensive project management platform with intelligent task prioritization, team collaboration, budget tracking, and advanced analytics.

## ✨ Key Features

### 🧠 Smart Task Prioritization Engine
- **Multi-Factor Scoring**: Combines urgency, effort, dependencies, and impact
- **Dynamic Calculation**: Real-time priority updates based on changing conditions
- **Dependency Management**: Smart handling of task blocking relationships
- **Visual Feedback**: Color-coded priority badges and detailed insights
- **Natural Language Processing**: Smart task parsing and understanding

### 👥 Team Collaboration
- **User Management**: Role-based access control with Flask-Security
- **Team Members**: Project-based team assignment and management
- **Discussions**: Thread-based discussions for projects and tasks
- **Notifications**: Real-time notifications with deadline warnings
- **Custom Statuses**: Project-specific task status workflows

### 💰 Budget & Expense Tracking
- **Budget Management**: Project and task-level budget allocation
- **Expense Tracking**: Categorized expense recording with receipts
- **Financial Analytics**: Budget vs actual spending analysis
- **Expense Categories**: Customizable expense categorization
- **Fund Management**: Track and manage project funds

### 📊 Advanced Analytics
- **Project Analytics**: Comprehensive project performance metrics
- **Task Analytics**: Priority distribution and completion tracking
- **Calendar View**: Visual timeline of tasks and deadlines
- **Smart Dashboard**: Overview of priorities, metrics, and insights
- **Scheduled Reports**: Automated analytics and insights

### 🎨 Modern UI/UX
- **Vue.js 3 Frontend**: Responsive and interactive user interface
- **Tailwind CSS**: Modern, utility-first styling
- **Component Library**: HeadlessUI and Heroicons integration
- **Real-time Updates**: Live data synchronization with Pinia state management

### 🔧 Technical Stack
- **Backend**: 
  - Flask 3.0.3
  - SQLAlchemy for ORM
  - Flask-Security-Too for authentication
  - Celery for background tasks
  - Natural Language Processing for task parsing
- **Frontend**: 
  - Vue.js 3
  - Tailwind CSS
  - Vite
  - Pinia for state management
- **Database**: SQLite with comprehensive schema design
- **API**: RESTful endpoints with CORS support

## 🌟 Celery Background Tasks

### Overview
The system uses Celery for handling background tasks and scheduled jobs, providing reliable asynchronous processing and task scheduling.

### Key Features
- **Task Scheduling**: Automated task prioritization updates
- **Deadline Monitoring**: Real-time deadline warnings and notifications
- **Analytics Generation**: Scheduled report generation
- **Email Notifications**: Asynchronous email delivery
- **Task Queue Management**: Distributed task processing

### Configuration
1. **Prerequisites**
   ```bash
   # Install Redis (required for Celery)
   # Windows: Download from https://github.com/microsoftarchive/redis/releases
   # Linux:
   sudo apt-get install redis-server
   # macOS:
   brew install redis
   ```

2. **Celery Setup**
   ```bash
   cd backend
   # Start Redis server (if not running)
   redis-server
   
   # Start Celery worker
   python start_celery.py
   ```

### Available Tasks
- **Priority Updates**: `task_prioritization.update_priorities()`
- **Deadline Warnings**: `deadline_warnings.check_deadlines()`
- **Analytics Reports**: `scheduled_jobs.generate_analytics()`
- **Email Notifications**: `notifications.send_notification()`

### Monitoring Tasks
```bash
# View active tasks
celery -A celery_app inspect active

# View scheduled tasks
celery -A celery_app inspect scheduled

# View task statistics
celery -A celery_app inspect stats
```

### Development
- Use `test_scheduled_jobs.py` for testing background tasks
- Configure task schedules in `celery_app.py`
- Monitor task execution in Celery logs

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Redis (for Celery tasks)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd synergy-sphere
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   python create_all_tables.py  # Initialize database
   python app.py  # Start Flask server
   ```

3. **Start Celery Workers** (in a new terminal)
   ```bash
   cd backend
   python start_celery.py
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

### Development Scripts

**Frontend:**
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

**Backend:**
```bash
python app.py                           # Start Flask development server
python demo_prioritization.py          # Run priority algorithm demo
python create_all_tables.py           # Initialize database tables
python start_celery.py                # Start Celery workers
```

## 📺 Demo Video

Watch our comprehensive demo video to see Synergy Sphere in action:
- [Synergy Sphere Demo](https://drive.google.com/file/d/1eajvghUzrsSUsNzheuc7qhWI-Fr8QT_G/view?usp=sharing)

The demo showcases:
- Smart task prioritization in action
- Team collaboration features
- Budget tracking and analytics
- Real-time notifications
- Background task processing
- Natural language task parsing

## 📊 Priority Scoring Algorithm

The system uses a sophisticated multi-factor scoring algorithm:

### Scoring Factors
- **Urgency (35%)**: Exponential decay based on deadline proximity
- **Dependencies (25%)**: Higher priority for tasks blocking others
- **Effort (20%)**: Easier tasks get higher priority (inverted scoring)
- **Impact (20%)**: Project criticality and business value

### Priority Scale
- **0-4**: Low Priority 🔵
- **4-6.5**: Medium Priority 🟡
- **6.5-8**: High Priority 🟠
- **8-10**: Urgent Priority 🔴

## 🏗️ Project Structure

```
├── backend/                          # Flask API server
│   ├── app.py                       # Main Flask application
│   ├── models.py                    # SQLAlchemy database models
│   ├── task_prioritization.py      # Smart priority algorithm
│   ├── llm_task_parser.py         # Natural language task parsing
│   ├── scheduled_jobs.py          # Background tasks
│   ├── celery_app.py              # Celery configuration
│   ├── routes/                     # API route blueprints
│   │   ├── auth.py                 # Authentication routes
│   │   ├── project.py              # Project management
│   │   ├── task.py                 # Task operations
│   │   ├── team.py                 # Team management
│   │   ├── discussion.py           # Discussion threads
│   │   ├── notifications.py        # Notification system
│   │   ├── analytics.py            # Analytics endpoints
│   │   ├── budget.py               # Budget management
│   │   └── expense.py              # Expense tracking
│   ├── migrations/                 # Database migration scripts
│   └── requirements.txt            # Python dependencies
├── frontend/                        # Vue.js application
│   ├── src/
│   │   ├── pages/                  # Vue page components
│   │   ├── components/             # Reusable Vue components
│   │   ├── router/                 # Vue Router configuration
│   │   ├── store/                  # Pinia state management
│   │   └── assets/                 # Static assets
│   ├── package.json               # Node.js dependencies
│   └── vite.config.js             # Vite configuration
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### Project Management
- `GET /api/projects` - List user projects
- `POST /api/projects` - Create new project
- `GET /api/projects/<id>` - Get project details
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### Task Management
- `GET /api/tasks/project/<id>` - Get tasks with smart sorting
- `POST /api/tasks` - Create task with priority factors
- `PUT /api/tasks/<id>` - Update task and recalculate priorities
- `DELETE /api/tasks/<id>` - Delete task
- `POST /api/tasks/recalculate-priorities` - Bulk priority update
- `POST /api/tasks/parse` - Parse natural language task description

### Advanced Features
- `GET /api/tasks/<id>/insights` - Detailed priority breakdown
- `GET /api/notifications` - User notifications
- `GET /api/analytics/project/<id>` - Project analytics
- `GET /api/budget/project/<id>` - Budget information
- `POST /api/expenses` - Record expenses

## 🧪 Testing & Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest test_*.py

# Frontend tests
cd frontend
npm run test
```

### Key Development Files
- `backend/test_nl_task_parser.py` - Natural language parsing tests
- `backend/test_scheduled_jobs.py` - Background task tests
- `backend/test_registration.py` - Authentication tests
- `backend/FRONTEND_INTEGRATION_GUIDE.md` - Frontend integration documentation

## 🔐 Security Features

- **Authentication**: Flask-Security-Too with role-based access
- **Password Hashing**: Secure password storage
- **API Security**: CORS and rate limiting
- **Input Validation**: Comprehensive input sanitization
- **Session Management**: Secure session handling

## 📈 Monitoring & Maintenance

### Database Management
- Use `create_all_tables.py` for fresh database setup
- `migrate_*.py` scripts for schema updates
- `debug_db.py` for database inspection

### Background Tasks
- Celery workers for scheduled jobs
- Task prioritization updates
- Deadline warnings
- Analytics generation


## 🙏 Acknowledgments

- Built with Flask and Vue.js ecosystems
- Powered by modern web development best practices
- Designed for scalability and maintainability

---

**Synergy Sphere** - Intelligent project management for modern teams! 🚀
