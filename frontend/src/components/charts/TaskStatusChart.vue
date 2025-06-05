<template>
  <div class="chart-container">
    <h3>Task Status Distribution</h3>
    <Doughnut
      v-if="chartData"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script>
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default {
  name: 'TaskStatusChart',
  components: { Doughnut },
  props: {
    taskStats: {
      type: Array,
      required: true
    }
  },
  computed: {
    chartData() {
      const statusColors = {
        'To Do': '#FF6B6B',
        'In Progress': '#4ECDC4',
        'Done': '#45B7D1',
        'Blocked': '#96CEB4'
      };

      return {
        labels: this.taskStats.map(stat => stat.status),
        datasets: [{
          data: this.taskStats.map(stat => stat.count),
          backgroundColor: this.taskStats.map(stat => statusColors[stat.status] || '#999'),
          borderWidth: 1
        }]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      };
    }
  }
};
</script>

<style scoped>
.chart-container {
  height: 300px;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h3 {
  margin-bottom: 1rem;
  text-align: center;
  color: #2c3e50;
}
</style> 