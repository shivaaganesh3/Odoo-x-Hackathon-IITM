<template>
  <div class="budget-manager">
    <div class="budget-header">
      <h3>💰 Budget Management</h3>
      <button @click="showNewBudgetForm = true" class="new-budget-btn">
        ➕ Add Budget
      </button>
    </div>

    <!-- New Budget Form -->
    <div v-if="showNewBudgetForm" class="budget-form">
      <div class="form-group">
        <label>Amount</label>
        <input 
          v-model.number="newBudget.amount" 
          type="number" 
          step="0.01" 
          min="0"
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label>Start Date</label>
        <input 
          v-model="newBudget.start_date" 
          type="date" 
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label>End Date</label>
        <input 
          v-model="newBudget.end_date" 
          type="date" 
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label>Notes</label>
        <textarea 
          v-model="newBudget.notes" 
          rows="3"
          class="form-input"
        ></textarea>
      </div>

      <div class="form-actions">
        <button 
          @click="createBudget" 
          class="submit-btn"
          :disabled="!isValidBudget"
        >
          Save Budget
        </button>
        <button @click="showNewBudgetForm = false" class="cancel-btn">
          Cancel
        </button>
      </div>
    </div>

    <!-- Budgets List -->
    <div v-if="budgets.length > 0" class="budgets-list">
      <div v-for="budget in budgets" :key="budget.id" class="budget-item">
        <div class="budget-info">
          <div class="budget-amount">
            💵 {{ formatCurrency(budget.amount) }}
          </div>
          <div class="budget-dates">
            📅 {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
          </div>
          <div class="budget-meta">
            Created by {{ budget.created_by }} on {{ formatDate(budget.created_at) }}
          </div>
          <div v-if="budget.notes" class="budget-notes">
            📝 {{ budget.notes }}
          </div>
        </div>

        <div class="budget-actions">
          <button 
            @click="startEdit(budget)"
            class="action-btn"
          >
            ✏️ Edit
          </button>
          <button 
            @click="deleteBudget(budget.id)"
            class="action-btn delete"
          >
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>

    <p v-else class="no-budgets">
      No budgets allocated yet.
    </p>

    <!-- Edit Budget Modal -->
    <div v-if="editingBudget" class="modal">
      <div class="modal-content">
        <h3>Edit Budget</h3>
        
        <div class="form-group">
          <label>Amount</label>
          <input 
            v-model.number="editForm.amount" 
            type="number" 
            step="0.01" 
            min="0"
            class="form-input"
          >
        </div>

        <div class="form-group">
          <label>Start Date</label>
          <input 
            v-model="editForm.start_date" 
            type="date" 
            class="form-input"
          >
        </div>

        <div class="form-group">
          <label>End Date</label>
          <input 
            v-model="editForm.end_date" 
            type="date" 
            class="form-input"
          >
        </div>

        <div class="form-group">
          <label>Notes</label>
          <textarea 
            v-model="editForm.notes" 
            rows="3"
            class="form-input"
          ></textarea>
        </div>

        <div class="form-actions">
          <button 
            @click="updateBudget" 
            class="submit-btn"
            :disabled="!isValidEditForm"
          >
            Update Budget
          </button>
          <button @click="cancelEdit" class="cancel-btn">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from '../axios'

const props = defineProps({
  projectId: {
    type: Number,
    required: false,
    default: null
  },
  taskId: {
    type: Number,
    required: false,
    default: null
  }
})

// State
const budgets = ref([])
const showNewBudgetForm = ref(false)
const editingBudget = ref(null)
const newBudget = ref({
  amount: null,
  start_date: '',
  end_date: '',
  notes: ''
})
const editForm = ref({
  amount: null,
  start_date: '',
  end_date: '',
  notes: ''
})

// Computed
const isValidBudget = computed(() => {
  return newBudget.value.amount > 0 &&
         newBudget.value.start_date &&
         newBudget.value.end_date &&
         new Date(newBudget.value.start_date) <= new Date(newBudget.value.end_date)
})

const isValidEditForm = computed(() => {
  return editForm.value.amount > 0 &&
         editForm.value.start_date &&
         editForm.value.end_date &&
         new Date(editForm.value.start_date) <= new Date(editForm.value.end_date)
})

// Methods
const fetchBudgets = async () => {
  try {
    const endpoint = props.taskId 
      ? `/budget/task/${props.taskId}`
      : `/budget/project/${props.projectId}`
    
    const response = await axios.get(endpoint)
    budgets.value = response.data
  } catch (error) {
    console.error('Failed to fetch budgets:', error)
  }
}

const createBudget = async () => {
  try {
    await axios.post('/budget/', {
      ...newBudget.value,
      project_id: props.projectId,
      task_id: props.taskId
    })
    
    newBudget.value = {
      amount: null,
      start_date: '',
      end_date: '',
      notes: ''
    }
    showNewBudgetForm.value = false
    await fetchBudgets()
  } catch (error) {
    console.error('Failed to create budget:', error)
  }
}

const startEdit = (budget) => {
  editingBudget.value = budget.id
  editForm.value = {
    amount: budget.amount,
    start_date: budget.start_date.split('T')[0],
    end_date: budget.end_date.split('T')[0],
    notes: budget.notes
  }
}

const cancelEdit = () => {
  editingBudget.value = null
  editForm.value = {
    amount: null,
    start_date: '',
    end_date: '',
    notes: ''
  }
}

const updateBudget = async () => {
  try {
    await axios.put(`/budget/${editingBudget.value}`, editForm.value)
    editingBudget.value = null
    await fetchBudgets()
  } catch (error) {
    console.error('Failed to update budget:', error)
  }
}

const deleteBudget = async (budgetId) => {
  if (!confirm('Are you sure you want to delete this budget?')) return

  try {
    await axios.delete(`/budget/${budgetId}`)
    await fetchBudgets()
  } catch (error) {
    console.error('Failed to delete budget:', error)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Initial load
fetchBudgets()
</script>

<style scoped>
.budget-manager {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.new-budget-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.new-budget-btn:hover {
  background: #2563eb;
}

.budget-form {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #4b5563;
}

.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-family: inherit;
}

textarea.form-input {
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.submit-btn, .cancel-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.submit-btn {
  background: #3b82f6;
  color: white;
  border: none;
}

.submit-btn:hover {
  background: #2563eb;
}

.submit-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.cancel-btn {
  background: white;
  border: 1px solid #d1d5db;
  color: #4b5563;
}

.cancel-btn:hover {
  background: #f3f4f6;
}

.budgets-list {
  margin-top: 1rem;
}

.budget-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.budget-amount {
  font-size: 1.25rem;
  font-weight: 600;
  color: #059669;
  margin-bottom: 0.5rem;
}

.budget-dates {
  color: #4b5563;
  margin-bottom: 0.25rem;
}

.budget-meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.budget-notes {
  color: #4b5563;
  font-style: italic;
}

.budget-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  color: #4b5563;
  font-size: 0.875rem;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn.delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

.no-budgets {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 2rem;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}
</style> 