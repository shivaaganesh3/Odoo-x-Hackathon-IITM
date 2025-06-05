# 🎯 Smart Task Prioritization Engine

A comprehensive project management system with intelligent task prioritization powered by multi-factor scoring algorithms.

## ✨ Key Features

### 🧠 Smart Prioritization Algorithm
- **Multi-Factor Scoring**: Combines urgency, effort, dependencies, and impact
- **Dynamic Calculation**: Real-time priority updates based on changing conditions
- **Dependency Management**: Smart handling of task blocking relationships
- **Visual Feedback**: Color-coded priority badges and insights

### 🎨 Modern UI/UX
- **Vue.js Frontend**: Responsive and interactive user interface
- **Priority Dashboard**: Overview of project metrics and top priority tasks
- **Task Management**: Drag-and-drop, filtering, and smart sorting
- **Real-time Updates**: Live priority recalculation and status updates

### 🔧 Technical Stack
- **Backend**: Flask, SQLAlchemy, Python
- **Frontend**: Vue.js 3, Tailwind CSS, Vite
- **Database**: SQLite with advanced schema design
- **API**: RESTful endpoints with smart sorting and filtering

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-task-prioritization-engine
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   cd synergy-sphere-frontend
   npm install
   npm run dev
   ```

4. **Demo Data (Optional)**
   ```bash
   cd backend
   python demo_prioritization.py
   ```

## 📊 Priority Scoring Algorithm

The system uses a sophisticated multi-factor scoring algorithm:

### Scoring Factors
- **Urgency (35%)**: Exponential decay based on deadline proximity
- **Dependencies (25%)**: Higher priority for tasks blocking others
- **Effort (20%)**: Easier tasks get higher priority (inverted scoring)
- **Impact (20%)**: Project criticality and business value

### Formula
```
Priority Score = (Urgency × 0.35) + (Dependencies × 0.25) + (Effort × 0.20) + (Impact × 0.20)
```

### Scale
- **0-3**: Low Priority (🔵)
- **4-6**: Medium Priority (🟡)
- **7-10**: High Priority (🔴)

## 🎯 Demo Results

The system successfully handles complex task prioritization scenarios:

```
1. 🚨 Critical Bug in Production - Score: 7.17/10 (High)
   Due today, easy fix, critical impact

2. 📊 Generate Weekly Reports - Score: 5.85/10 (Medium)
   Due in 2 days, very easy, low impact

3. 🎨 UI Design for New Feature - Score: 5.5/10 (Medium)
   Due in 1 week, medium effort, blocks other tasks
```

## 🏗️ Project Structure

```
├── backend/                          # Flask API server
│   ├── models.py                     # Database models
│   ├── task_prioritization.py       # Priority algorithm
│   ├── routes/                       # API endpoints
│   ├── migrate_smart_prioritization.py  # Database migration
│   └── demo_prioritization.py       # Demo script
├── synergy-sphere-frontend/          # Vue.js application
│   ├── src/
│   │   ├── pages/ProjectTasks.vue    # Enhanced task management
│   │   ├── pages/SmartDashboard.vue  # Priority dashboard
│   │   └── router/index.js           # Route configuration
│   └── package.json
└── README.md
```

## 🔌 API Endpoints

### Task Management
- `GET /api/tasks/project/<id>` - Get tasks with smart sorting
- `POST /api/tasks` - Create task with priority factors
- `PUT /api/tasks/<id>` - Update task and recalculate priorities
- `POST /api/tasks/recalculate-priorities` - Bulk priority update

### Priority Features
- `GET /api/tasks/<id>/insights` - Detailed priority breakdown
- `GET /api/tasks/<id>/dependency-graph` - Dependency visualization
- `GET /api/tasks/blocked` - List of blocked tasks

## 🎨 UI Components

### Priority Features
- **Smart Priority Badges**: Color-coded with animations
- **Priority Insights Modal**: Detailed factor breakdown
- **Dependency Visualization**: Task blocking relationships
- **Smart Dashboard**: Metrics and top priority tasks
- **Enhanced Task Forms**: Effort/Impact selectors

### Smart Controls
- **Priority Recalculation**: One-click update button
- **Smart Sorting**: Multiple sorting options
- **Dependency Management**: Visual dependency picker
- **Real-time Updates**: Live priority score updates

## 🔄 Database Schema

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
    project_id INTEGER,
    status_id INTEGER,
    assigned_to INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);
```

## 🧪 Testing

### Demo Script
Run the comprehensive demo to see the system in action:
```bash
cd backend
python demo_prioritization.py
```

### Test Features
- Creates 7 sample tasks with varying priority factors
- Demonstrates dependency chains
- Shows priority calculation results
- Validates algorithm accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by agile project management principles
- Designed for scalability and performance

---

**Smart Task Prioritization Engine** - Making project management intelligent and efficient! 🚀
