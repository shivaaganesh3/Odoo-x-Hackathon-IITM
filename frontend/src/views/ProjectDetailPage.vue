<template>
  <div class="project-detail">
    <div class="project-header">
      <h1>{{ project.name }}</h1>
      <p class="project-description">{{ project.description }}</p>
    </div>

    <div class="project-tabs">
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'" href="#">Overview</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'tasks' }" @click="activeTab = 'tasks'" href="#">Tasks</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'team' }" @click="activeTab = 'team'" href="#">Team</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'budget' }" @click="activeTab = 'budget'" href="#">Budget</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'expenses' }" @click="activeTab = 'expenses'" href="#">Expenses</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'analytics' }" @click="activeTab = 'analytics'" href="#">Analytics</a>
        </li>
      </ul>
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'overview'" class="tab-pane active">
        <div class="overview-stats">
          <div class="stat-card">
            <h3>Tasks</h3>
            <p>{{ taskStats.total }} Total</p>
            <p>{{ taskStats.completed }} Completed</p>
          </div>
          <div class="stat-card">
            <h3>Team</h3>
            <p>{{ teamStats.members }} Members</p>
          </div>
          <div class="stat-card">
            <h3>Budget</h3>
            <p>${{ formatNumber(budgetStats.total) }}</p>
            <p>${{ formatNumber(budgetStats.remaining) }} Remaining</p>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'tasks'" class="tab-pane active">
        <ProjectTasks :projectId="projectId" />
      </div>

      <div v-if="activeTab === 'team'" class="tab-pane active">
        <ProjectTeam :projectId="projectId" />
      </div>

      <div v-if="activeTab === 'budget'" class="tab-pane active">
        <ProjectBudget :projectId="projectId" />
      </div>

      <div v-if="activeTab === 'expenses'" class="tab-pane active">
        <ProjectExpenses :projectId="projectId" />
      </div>

      <div v-if="activeTab === 'analytics'" class="tab-pane active">
        <AnalyticsDashboard :projectId="projectId" />
      </div>
    </div>
  </div>
</template>

<script>
import ProjectTasks from '../components/ProjectTasks.vue';
import ProjectTeam from '../components/ProjectTeam.vue';
import ProjectBudget from '../components/ProjectBudget.vue';
import ProjectExpenses from '../components/ProjectExpenses.vue';
import AnalyticsDashboard from '../components/AnalyticsDashboard.vue';

export default {
  name: 'ProjectDetailPage',
  components: {
    ProjectTasks,
    ProjectTeam,
    ProjectBudget,
    ProjectExpenses,
    AnalyticsDashboard
  },
  data() {
    return {
      activeTab: 'overview',
      project: {
        name: '',
        description: ''
      },
      taskStats: {
        total: 0,
        completed: 0
      },
      teamStats: {
        members: 0
      },
      budgetStats: {
        total: 0,
        remaining: 0
      },
      loading: true
    };
  },
  computed: {
    projectId() {
      return this.$route.params.id;
    }
  },
  methods: {
    async fetchProjectData() {
      try {
        const response = await this.$http.get(`/api/projects/${this.projectId}`);
        this.project = response.data;
        await this.fetchStats();
      } catch (error) {
        console.error('Error fetching project:', error);
      }
    },
    async fetchStats() {
      try {
        const [tasks, team, budget] = await Promise.all([
          this.$http.get(`/api/projects/${this.projectId}/tasks`),
          this.$http.get(`/api/projects/${this.projectId}/team`),
          this.$http.get(`/api/projects/${this.projectId}/budget`)
        ]);

        this.taskStats = {
          total: tasks.data.length,
          completed: tasks.data.filter(t => t.status === 'Done').length
        };

        this.teamStats = {
          members: team.data.length
        };

        this.budgetStats = {
          total: budget.data.total || 0,
          remaining: budget.data.remaining || 0
        };
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        this.loading = false;
      }
    },
    formatNumber(value) {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    }
  },
  mounted() {
    this.fetchProjectData();
  }
};
</script>

<style scoped>
.project-detail {
  padding: 2rem;
}

.project-header {
  margin-bottom: 2rem;
}

.project-header h1 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.project-description {
  color: #666;
}

.project-tabs {
  margin-bottom: 2rem;
}

.nav-tabs {
  border-bottom: 2px solid #dee2e6;
}

.nav-link {
  color: #6c757d;
  border: none;
  padding: 0.75rem 1rem;
  margin-right: 0.5rem;
  font-weight: 500;
}

.nav-link:hover {
  color: #4ECDC4;
}

.nav-link.active {
  color: #4ECDC4;
  border-bottom: 2px solid #4ECDC4;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.stat-card p {
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 1.1rem;
}

.tab-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-pane {
  padding: 2rem;
}
</style> 