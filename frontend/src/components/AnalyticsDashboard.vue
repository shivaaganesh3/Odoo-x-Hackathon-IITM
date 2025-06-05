<template>
  <div class="analytics-dashboard">
    <div class="dashboard-header">
      <h2>Project Analytics Dashboard</h2>
      <div class="refresh-button">
        <button @click="fetchData" class="btn btn-primary">
          <i class="fas fa-sync-alt"></i> Refresh Data
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="dashboard-grid">
      <!-- Task Status Distribution -->
      <div class="dashboard-item">
        <TaskStatusChart :taskStats="taskStats" />
      </div>

      <!-- Budget Overview -->
      <div class="dashboard-item">
        <BudgetChart :budgetData="budgetOverview" />
      </div>

      <!-- Team Workload -->
      <div class="dashboard-item full-width">
        <div class="card">
          <div class="card-header">
            <h3>Team Workload</h3>
          </div>
          <div class="card-body">
            <div class="workload-grid">
              <div v-for="member in teamWorkload" :key="member.name" class="workload-item">
                <h4>{{ member.name }}</h4>
                <div class="task-counts">
                  <div v-for="(count, status) in member.tasks" :key="status" class="task-count">
                    <span class="status">{{ status }}:</span>
                    <span class="count">{{ count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottleneck Analysis -->
      <div class="dashboard-item">
        <div class="card">
          <div class="card-header">
            <h3>Bottleneck Analysis</h3>
          </div>
          <div class="card-body">
            <table class="table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Avg. Days</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in bottleneckAnalysis" :key="item.status">
                  <td>{{ item.status }}</td>
                  <td>{{ item.avg_days.toFixed(1) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Task Completion Trend -->
      <div class="dashboard-item">
        <div class="card">
          <div class="card-header">
            <h3>Task Completion Trend (Last 30 Days)</h3>
          </div>
          <div class="card-body">
            <Line
              v-if="completionTrendData"
              :data="completionTrendData"
              :options="completionTrendOptions"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import TaskStatusChart from './charts/TaskStatusChart.vue';
import BudgetChart from './charts/BudgetChart.vue';
import analyticsService from '../services/analyticsService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default {
  name: 'AnalyticsDashboard',
  components: {
    TaskStatusChart,
    BudgetChart,
    Line
  },
  props: {
    projectId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      taskStats: [],
      budgetOverview: {
        total_budget: 0,
        total_expenses: 0,
        remaining: 0
      },
      teamWorkload: [],
      bottleneckAnalysis: [],
      completionTrend: []
    };
  },
  computed: {
    completionTrendData() {
      return {
        labels: this.completionTrend.map(item => item.date),
        datasets: [{
          label: 'Completed Tasks',
          data: this.completionTrend.map(item => item.count),
          borderColor: '#4ECDC4',
          backgroundColor: 'rgba(78, 205, 196, 0.1)',
          tension: 0.4,
          fill: true
        }]
      };
    },
    completionTrendOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            }
          }
        }
      };
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const overview = await analyticsService.getProjectOverview(this.projectId);
        this.taskStats = overview.task_stats.by_status;
        this.budgetOverview = overview.budget_overview;
        this.bottleneckAnalysis = overview.bottleneck_analysis;
        this.completionTrend = overview.completion_trend;

        const workload = await analyticsService.getTeamWorkload(this.projectId);
        this.teamWorkload = workload;
      } catch (error) {
        console.error('Error fetching analytics data:', error);
        // You might want to show an error message to the user here
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchData();
  }
};
</script>

<style scoped>
.analytics-dashboard {
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

.dashboard-item {
  min-height: 400px;
}

.dashboard-item.full-width {
  grid-column: 1 / -1;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.card {
  height: 100%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.workload-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.workload-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
}

.workload-item h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.task-counts {
  display: grid;
  gap: 0.5rem;
}

.task-count {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
}

.status {
  font-weight: 500;
  color: #6c757d;
}

.count {
  font-weight: bold;
  color: #2c3e50;
}

.table {
  margin: 0;
}

.refresh-button {
  margin-left: 1rem;
}

.btn-primary {
  background-color: #4ECDC4;
  border-color: #45B7D1;
}

.btn-primary:hover {
  background-color: #45B7D1;
  border-color: #45B7D1;
}
</style> 