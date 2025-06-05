<template>
  <div class="chart-container">
    <h3>Budget Overview</h3>
    <Bar
      v-if="chartData"
      :data="chartData"
      :options="chartOptions"
    />
    <div class="budget-summary">
      <div class="summary-item">
        <span class="label">Total Budget:</span>
        <span class="value">${{ formatNumber(budgetData.total_budget) }}</span>
      </div>
      <div class="summary-item">
        <span class="label">Total Expenses:</span>
        <span class="value">${{ formatNumber(budgetData.total_expenses) }}</span>
      </div>
      <div class="summary-item">
        <span class="label">Remaining:</span>
        <span class="value" :class="{ 'text-danger': budgetData.remaining < 0 }">
          ${{ formatNumber(budgetData.remaining) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default {
  name: 'BudgetChart',
  components: { Bar },
  props: {
    budgetData: {
      type: Object,
      required: true
    }
  },
  computed: {
    chartData() {
      return {
        labels: ['Budget Overview'],
        datasets: [
          {
            label: 'Total Budget',
            data: [this.budgetData.total_budget],
            backgroundColor: '#4ECDC4',
            borderColor: '#45B7D1',
            borderWidth: 1
          },
          {
            label: 'Total Expenses',
            data: [this.budgetData.total_expenses],
            backgroundColor: '#FF6B6B',
            borderColor: '#FF6B6B',
            borderWidth: 1
          }
        ]
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
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: value => `$${this.formatNumber(value)}`
            }
          }
        }
      };
    }
  },
  methods: {
    formatNumber(value) {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    }
  }
};
</script>

<style scoped>
.chart-container {
  height: 400px;
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

.budget-summary {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.label {
  font-weight: bold;
  color: #2c3e50;
}

.value {
  font-family: monospace;
}

.text-danger {
  color: #FF6B6B;
}
</style> 