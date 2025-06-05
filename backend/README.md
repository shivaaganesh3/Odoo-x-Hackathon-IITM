# 🔧 SynergySphere Backend API

Flask-based REST API backend for the SynergySphere project management platform with AI-powered analytics, smart task prioritization, and comprehensive budget management.

## 🚀 Features

### 📊 **Analytics Engine**
- **Project Overview API** - Comprehensive analytics with budget vs expenses tracking
- **Deadline Risk Assessment** - AI-powered project risk analysis
- **Task Completion Trends** - 30-day progress tracking
- **Bottleneck Analysis** - Workflow optimization insights
- **Team Productivity Metrics** - Performance analytics

### 🧠 **Smart Task Prioritization**
- **Multi-factor Priority Algorithm** - Urgency, effort, dependencies, impact scoring
- **Priority Insights API** - Detailed score breakdowns
- **Smart Sorting** - Intelligent task ordering
- **Dependency Analysis** - Task relationship mapping

### 💰 **Budget & Expense Management**
- **Budget CRUD Operations** - Project and task-level budgets
- **Expense Tracking** - Categorized expense management
- **Financial Analytics** - Budget vs actual reporting
- **Expense Categories** - 10 default categories with custom support

### 🔔 **Intelligent Notifications**
- **Deadline Warning Engine** - Proactive risk alerts
- **Automated Analysis** - Smart deadline predictions
- **Risk Categorization** - Critical/High/Medium/Low risk levels
- **Context-aware Recommendations** - AI-generated suggestions

### 🔐 **Security & Authentication**
- **Flask-Security** - Role-based access control
- **Team Membership Validation** - Project-level authorization
- **User Management** - Registration, login, role assignment
- **CORS Configuration** - Cross-origin resource sharing

## 🛠️ Technology Stack

- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Security** - Authentication and authorization
- **SQLite** - Database (easily configurable for PostgreSQL/MySQL)
- **Flask-CORS** - Cross-origin request handling
- **Python 3.8+** - Modern Python features

## 🗂️ Database Schema

### Core Models
- **Users** - User authentication and profiles
- **Projects** - Project management
- **Tasks** - Task tracking with custom statuses
- **TeamMembers** - Project team management
- **CustomStatus** - Flexible workflow statuses

### Analytics Models
- **Budget** - Project and task budgets
- **Expense** - Expense tracking with categories
- **ExpenseCategory** - Expense classification
- **Notifications** - System notifications and alerts

### Advanced Features
- **Discussions** - Task-level threaded conversations
- **Priority Scoring** - AI-calculated task priorities
- **Deadline Warnings** - Automated risk assessments

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python create_all_tables.py
   python populate_expense_categories.py
   ```

5. **Start the server**
   ```bash
   python app.py
   ```
   
   Server runs on `http://localhost:5000`

### Database Setup Scripts

- `create_all_tables.py` - Initialize all database tables
- `populate_expense_categories.py` - Add default expense categories
- `create_budget_tables.py` - Create budget/expense tables specifically
- `migrate_discussions_table.py` - Add discussion support to existing DB

## 📋 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
All endpoints require authentication via Flask-Security. Include authentication headers in requests.

### 📊 Analytics Endpoints

#### Get Project Overview
```http
GET /analytics/project/{project_id}/overview
```
**Response:**
```json
{
  "task_stats": {
    "by_status": [{"status": "To Do", "count": 5}]
  },
  "budget_overview": {
    "total_budget": 10000.0,
    "total_expenses": 3500.0,
    "remaining": 6500.0
  },
  "completion_trend": [{"date": "2024-01-15", "count": 3}],
  "bottleneck_analysis": [{"status": "In Progress", "avg_days": 5.2}],
  "team_productivity": [{"assignee_id": 1, "completed_tasks": 8}]
}
```

#### Get Deadline Risk Assessment
```http
GET /analytics/project/{project_id}/deadline-risk
```
**Response:**
```json
{
  "risk_level": "medium",
  "progress_percentage": 65,
  "days_remaining": 5,
  "total_tasks": 20,
  "completed_tasks": 13,
  "earliest_deadline": "2024-01-20"
}
```

### 💰 Budget Management

#### Create Budget
```http
POST /budget/
Content-Type: application/json

{
  "amount": 5000.0,
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "notes": "Q1 Marketing Budget",
  "project_id": 1
}
```

#### Get Project Budgets
```http
GET /budget/project/{project_id}
```

### 💸 Expense Management

#### Create Expense
```http
POST /expenses/
Content-Type: application/json

{
  "amount": 250.0,
  "date": "2024-01-15",
  "notes": "Office supplies",
  "category_id": 7,
  "project_id": 1
}
```

#### Get Expense Categories
```http
GET /expenses/categories
```

### 🎯 Task Management

#### Get Smart-Sorted Tasks
```http
GET /tasks/my?sort_by=smart
```

#### Get Priority Insights
```http
GET /tasks/priority/insights/{task_id}
```
**Response:**
```json
{
  "title": "Implement user authentication",
  "total_score": 8.2,
  "scores": {
    "urgency": {"value": 8, "weighted": 2.4},
    "effort": {"value": 6, "weighted": 1.2},
    "dependency": {"value": 9, "weighted": 2.7},
    "impact": {"value": 7, "weighted": 1.9}
  },
  "blocking_tasks": 3,
  "blocked_by_tasks": 1
}
```

### 🔔 Notifications

#### Run Deadline Analysis
```http
POST /notifications/deadline-analysis
```

#### Get Notifications
```http
GET /notifications?limit=10&offset=0
```

### 👥 Team Management

#### Add Team Member
```http
POST /team/projects/{project_id}/members
Content-Type: application/json

{
  "email": "user@example.com",
  "role": "member"
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file or modify `config.py`:

```python
# config.py
class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///taskmanager.db'
    SECURITY_PASSWORD_SALT = 'your-password-salt'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
```

### Database Configuration
- **SQLite** (default): `sqlite:///taskmanager.db`
- **PostgreSQL**: `postgresql://user:pass@localhost/dbname`
- **MySQL**: `mysql://user:pass@localhost/dbname`

## 🚀 Deployment

### Production Considerations
1. **Use production WSGI server** (e.g., Gunicorn)
2. **Configure database** (PostgreSQL recommended)
3. **Set environment variables** for secrets
4. **Enable HTTPS** for security
5. **Configure CORS** for production domains

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🧪 Testing

### Run Tests
```bash
python test_system.py
python test_flask_db.py
```

### Test User Creation
```bash
python create_test_user.py
python verify_user.py
```

## 📊 Analytics Features Deep Dive

### Smart Priority Algorithm
The task prioritization system uses a weighted scoring algorithm:

- **Urgency (30%)** - Based on due date proximity
- **Effort (20%)** - Task complexity score (1-10)
- **Dependencies (30%)** - Number of blocking/blocked tasks
- **Impact (20%)** - Business impact score (1-10)

### Deadline Warning Engine
Located in `deadline_warnings.py`, this engine:
- Analyzes all project tasks for deadline risks
- Calculates progress percentages
- Generates AI-powered recommendations
- Categorizes risks as Critical/High/Medium/Low

### Budget Analytics
- Real-time budget vs expenses calculations
- Expense category breakdowns
- Trend analysis and forecasting
- Budget utilization percentages

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**
   ```bash
   python create_all_tables.py
   ```

2. **Missing expense categories**
   ```bash
   python populate_expense_categories.py
   ```

3. **Authentication errors**
   ```bash
   python fix_auth.py
   ```

4. **Database migration issues**
   ```bash
   python migrate_discussions_table.py
   ```

### Debug Commands
- `python debug_db.py` - Database inspection
- `python check_users.py` - User verification
- `python debug_user_lookup.py` - User lookup debugging

## 📁 File Structure

```
backend/
├── app.py                          # Flask application factory
├── config.py                       # Configuration settings
├── database.py                     # Database initialization
├── models.py                       # SQLAlchemy models
├── requirements.txt                # Python dependencies
├── routes/                         # API route blueprints
│   ├── analytics.py               # Analytics endpoints
│   ├── auth.py                    # Authentication
│   ├── budget.py                  # Budget management
│   ├── expense.py                 # Expense tracking
│   ├── project.py                 # Project management
│   ├── task.py                    # Task management
│   ├── team.py                    # Team management
│   ├── discussion.py              # Task discussions
│   ├── custom_status.py           # Workflow statuses
│   └── notifications.py           # Notification system
├── deadline_warnings.py           # AI deadline analysis
├── task_prioritization.py         # Smart priority algorithms
├── migrations/                     # Database migrations
└── utils/                          # Utility functions
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow PEP 8** coding standards
4. **Add tests** for new features
5. **Update documentation**
6. **Submit pull request**

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for functions
- Include type hints where appropriate

## 📝 API Rate Limiting

Currently no rate limiting is implemented. For production:
- Implement Flask-Limiter
- Add per-user/IP rate limits
- Consider API authentication tokens

## 🔒 Security Considerations

- All endpoints require authentication
- Team membership validation for project access
- Input validation and sanitization
- SQL injection protection via SQLAlchemy
- CORS configured for specific origins

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Flask Backend API for SynergySphere Project Management Platform** 