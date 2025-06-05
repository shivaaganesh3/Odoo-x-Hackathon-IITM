# 🚀 SynergySphere - Advanced Project Management System

A comprehensive project management platform with AI-powered task prioritization, real-time analytics, and intelligent deadline management.

## ✨ Key Features

### 📊 **Analytics Dashboard**
- **Budget vs Expenses Tracking** - Real-time financial monitoring with visual charts
- **Task Status Distribution** - Doughnut charts showing project progress
- **Team Workload Analysis** - Task distribution across team members
- **Bottleneck Analysis** - Identify workflow slowdowns and inefficiencies
- **Completion Trends** - 30-day task completion tracking
- **Project Deadline Risk Assessment** - AI-powered risk level indicators

### 🧠 **Smart Task Prioritization**
- **Multi-factor Priority Scoring** - Urgency, effort, dependencies, impact analysis
- **AI-powered Recommendations** - Context-aware suggestions for task management
- **Priority Insights Dashboard** - Detailed score breakdowns with visual indicators
- **Smart Sorting** - Intelligent task ordering based on priority algorithms

### 💰 **Budget & Expense Management**
- **Project-level Budgets** - Comprehensive financial planning
- **Task-level Expenses** - Granular expense tracking
- **Expense Categories** - Organized spending classification (Labor, Materials, Equipment, etc.)
- **Budget vs Actual Visualization** - Real-time budget monitoring with alerts
- **Financial Reports** - Detailed expense breakdowns and analytics

### 🔔 **Intelligent Notifications**
- **Deadline Warning Engine** - Proactive alerts for at-risk tasks
- **Progress Monitoring** - Automated project health assessments
- **Risk Analysis** - Critical/High/Medium/Low risk categorization
- **Real-time Updates** - Instant notifications for project changes

### 👥 **Team Collaboration**
- **Task Discussions** - Threaded conversations on individual tasks
- **Team Member Management** - Role-based access control
- **Assignment Tracking** - Clear ownership and responsibility
- **Activity Feeds** - Real-time project activity monitoring

### ⚙️ **Customizable Workflows**
- **Custom Status Management** - Create project-specific workflows
- **Status Positioning** - Define logical workflow sequences
- **Progress Calculation** - Flexible progress measurement options
- **Workflow Analytics** - Track status transition times and bottlenecks

## 🛠️ Technology Stack

### Frontend
- **Vue.js 3** - Modern reactive framework with Composition API
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Tailwind CSS** - Utility-first styling
- **Chart.js & vue-chartjs** - Interactive data visualizations
- **Axios** - HTTP client for API communication
- **Vite** - Fast build tool and development server

### UI Components
- **Heroicons** - Beautiful SVG icons
- **Custom Components** - Reusable analytics dashboards, charts, and forms
- **Responsive Design** - Mobile-first responsive layouts

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+ (for backend)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd round2
   ```

2. **Frontend Setup**
   ```bash
   cd synergy-sphere-frontend
   npm install
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Backend Setup**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   python app.py
   ```
   Backend API will run on `http://localhost:5000`

### Environment Setup
- Frontend: Configure API base URL in `src/axios.js`
- Backend: Set up database and Flask configuration in `config.py`

## 📋 Available Scripts

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Backend
- `python app.py` - Start Flask development server
- `python create_all_tables.py` - Initialize database tables
- `python populate_expense_categories.py` - Add default expense categories

## 🗂️ Project Structure

```
synergy-sphere-frontend/
├── src/
│   ├── components/           # Reusable Vue components
│   │   ├── charts/          # Chart components (BudgetChart, TaskStatusChart)
│   │   ├── AnalyticsDashboard.vue
│   │   ├── ProjectDeadlineRisk.vue
│   │   └── ...
│   ├── pages/               # Page components
│   │   ├── ProjectsPage.vue
│   │   ├── SmartDashboard.vue
│   │   ├── DashboardPage.vue
│   │   └── ...
│   ├── store/               # Pinia stores
│   ├── services/            # API service layers
│   │   └── analyticsService.js
│   └── axios.js             # HTTP client configuration
└── ...

backend/
├── routes/                  # API blueprint routes
│   ├── analytics.py         # Analytics endpoints
│   ├── budget.py           # Budget management
│   ├── expense.py          # Expense tracking
│   └── ...
├── models.py               # SQLAlchemy database models
├── deadline_warnings.py    # AI deadline analysis engine
├── task_prioritization.py  # Smart priority algorithms
└── ...
```

## 📊 Analytics Dashboard Usage

### Accessing Analytics
1. Navigate to any project
2. Click the **"Analytics"** tab
3. View real-time charts and metrics

### Budget vs Expenses Chart
- **Green bars** = Total Budget
- **Red bars** = Total Expenses  
- **Summary section** shows remaining budget
- **Red indicator** if over budget

### Key Metrics
- **Task Progress** - Visual progress tracking
- **Team Workload** - Task distribution analysis
- **Deadline Risks** - AI-powered risk assessment
- **Financial Health** - Budget vs actual spending

## 🔧 API Endpoints

### Analytics
- `GET /api/analytics/project/{id}/overview` - Comprehensive project analytics
- `GET /api/analytics/project/{id}/deadline-risk` - Risk assessment

### Budget & Expenses
- `POST /api/budget/` - Create budget
- `GET /api/budget/project/{id}` - Get project budgets
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/project/{id}` - Get project expenses

### Tasks & Projects
- `GET /api/tasks/my?sort_by=smart` - Smart-sorted tasks
- `GET /api/tasks/priority/insights/{id}` - Priority insights
- `POST /api/notifications/deadline-analysis` - Run deadline analysis

## 🎯 Key Features Walkthrough

### 1. Smart Task Prioritization
- Multi-factor scoring based on urgency, effort, dependencies, and impact
- AI-generated recommendations for task management
- Visual priority insights with detailed breakdowns

### 2. Budget Management
- Create project and task-level budgets
- Track expenses with categorization
- Real-time budget vs actual monitoring
- Visual alerts for budget overruns

### 3. Analytics Dashboard
- Comprehensive project health monitoring
- Visual charts for all key metrics
- Real-time data updates
- Exportable insights and reports

### 4. Deadline Management
- Proactive deadline warning system
- Risk level assessment (Critical/High/Medium/Low)
- Automated recommendations for at-risk projects
- Progress-based deadline predictions

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@synergyphere.com or join our Slack channel.

---

**Built with ❤️ using Vue.js, Flask, and modern web technologies**
