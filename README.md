# 🎯 Synergy Sphere - Smart Project Management System

A comprehensive project management platform with intelligent task prioritization, team collaboration, budget tracking, and advanced analytics.

## ✨ Key Features

### 🧠 Smart Task Prioritization Engine
- **Multi-Factor Scoring**: Combines urgency, effort, dependencies, and impact
- **Dynamic Calculation**: Real-time priority updates based on changing conditions
- **Dependency Management**: Smart handling of task blocking relationships
- **Visual Feedback**: Color-coded priority badges and detailed insights

### 👥 Team Collaboration
- **User Management**: Role-based access control with Flask-Security
- **Team Members**: Project-based team assignment and management
- **Discussions**: Thread-based discussions for projects and tasks
- **Notifications**: Real-time notifications with deadline warnings

### 💰 Budget & Expense Tracking
- **Budget Management**: Project and task-level budget allocation
- **Expense Tracking**: Categorized expense recording with receipts
- **Financial Analytics**: Budget vs actual spending analysis
- **Expense Categories**: Customizable expense categorization

### 📊 Advanced Analytics
- **Project Analytics**: Comprehensive project performance metrics
- **Task Analytics**: Priority distribution and completion tracking
- **Calendar View**: Visual timeline of tasks and deadlines
- **Smart Dashboard**: Overview of priorities, metrics, and insights

### 🎨 Modern UI/UX
- **Vue.js 3 Frontend**: Responsive and interactive user interface
- **Tailwind CSS**: Modern, utility-first styling
- **Component Library**: HeadlessUI and Heroicons integration
- **Real-time Updates**: Live data synchronization with Pinia state management

### 🔧 Technical Stack
- **Backend**: Flask 3.0.3, SQLAlchemy, Flask-Security-Too
- **Frontend**: Vue.js 3, Tailwind CSS, Vite
- **Database**: SQLite with comprehensive schema design
- **API**: RESTful endpoints with CORS support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

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
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   cd synergy-sphere-frontend
   npm install
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

### Development Scripts

**Frontend (synergy-sphere-frontend directory):**
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

**Backend (backend directory):**
```bash
python app.py                           # Start Flask development server
python demo_prioritization.py          # Run priority algorithm demo
python create_all_tables.py           # Initialize database tables
```

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

### Algorithm Details
```python
Priority Score = (Urgency × 0.35) + (Dependencies × 0.25) + (Effort × 0.20) + (Impact × 0.20)
```

## 🏗️ Project Structure

```
├── backend/                          # Flask API server
│   ├── app.py                       # Main Flask application
│   ├── models.py                    # SQLAlchemy database models
│   ├── task_prioritization.py      # Smart priority algorithm
│   ├── database.py                 # Database configuration
│   ├── config.py                   # Flask configuration
│   ├── routes/                     # API route blueprints
│   │   ├── auth.py                 # Authentication routes
│   │   ├── project.py              # Project management
│   │   ├── task.py                 # Task operations
│   │   ├── team.py                 # Team management
│   │   ├── discussion.py           # Discussion threads
│   │   ├── notifications.py        # Notification system
│   │   ├── analytics.py            # Analytics endpoints
│   │   ├── budget.py               # Budget management
│   │   ├── expense.py              # Expense tracking
│   │   └── custom_status.py        # Custom status management
│   ├── migrations/                 # Database migration scripts
│   └── requirements.txt            # Python dependencies
├── synergy-sphere-frontend/         # Vue.js application
│   ├── src/
│   │   ├── pages/                  # Vue page components
│   │   │   ├── ProjectTasks.vue    # Enhanced task management
│   │   │   ├── SmartDashboard.vue  # Priority dashboard
│   │   │   ├── CalendarPage.vue    # Calendar view
│   │   │   ├── ProjectsPage.vue    # Project overview
│   │   │   ├── NotificationsPage.vue # Notification center
│   │   │   └── TeamPage.vue        # Team management
│   │   ├── components/             # Reusable Vue components
│   │   ├── router/                 # Vue Router configuration
│   │   ├── store/                  # Pinia state management
│   │   └── assets/                 # Static assets
│   ├── package.json               # Node.js dependencies
│   └── vite.config.js             # Vite configuration
├── package.json                    # Root dependencies (Chart.js)
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

### Advanced Features
- `GET /api/tasks/<id>/insights` - Detailed priority breakdown
- `GET /api/notifications` - User notifications
- `GET /api/analytics/project/<id>` - Project analytics
- `GET /api/budget/project/<id>` - Budget information
- `POST /api/expenses` - Record expenses

## 💾 Database Schema

### Core Models
- **Users**: User authentication and profiles with Flask-Security
- **Projects**: Project containers with team management
- **Tasks**: Enhanced with priority scoring fields
- **CustomStatus**: Project-specific task statuses
- **TeamMembers**: Project team assignments
- **Discussions**: Threaded conversations
- **Notifications**: Real-time notification system
- **Budget**: Financial planning and tracking
- **Expenses**: Expense recording with categorization

### Enhanced Task Model
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    priority_score FLOAT DEFAULT 0.0,
    effort_score INTEGER DEFAULT 3,    -- 1-5 scale
    impact_score INTEGER DEFAULT 3,    -- 1-5 scale
    dependency_map JSON DEFAULT '[]',  -- Task IDs this blocks
    blocked_by JSON DEFAULT '[]',      -- Task IDs blocking this
    due_date DATE,
    status_id INTEGER,                 -- References custom_status
    project_id INTEGER,
    assigned_to INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);
```

## 🧪 Testing & Demo

### Demo Script
Run the comprehensive demo to see the prioritization system:
```bash
cd backend
python demo_prioritization.py
```

### Key Features Demonstrated
- Smart priority calculation across multiple factors
- Dependency chain handling
- Real-time score updates
- Priority insights and breakdowns

## 🛠️ Development Setup

### Environment Configuration
1. **Backend Environment Variables** (create `.env` in backend/):
   ```
   SECRET_KEY=your-secret-key-here
   SECURITY_PASSWORD_SALT=your-salt-here
   ```

2. **Frontend Development**:
   - Hot reload enabled with Vite
   - Tailwind CSS with custom configuration
   - ESLint and Prettier recommended

### Database Initialization
```bash
cd backend
python create_all_tables.py    # Create all tables
python setup_roles.py          # Initialize user roles
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing 'dev' script error**:
   - Run `npm run dev` from `synergy-sphere-frontend/` directory, not root
   - Root `package.json` only contains Chart.js dependencies

2. **Database Issues**:
   - Run `python create_all_tables.py` to initialize
   - Check `taskmanager.db` file permissions

3. **CORS Issues**:
   - Frontend configured for ports 5173/5174
   - Backend CORS allows localhost origins

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding standards in user rules
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask and Vue.js ecosystems
- Powered by modern web development best practices
- Designed for scalability and maintainability

---

**Synergy Sphere** - Intelligent project management for modern teams! 🚀
