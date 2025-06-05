<template>
  <div class="expense-manager">
    <div class="expense-header">
      <h3>📊 Expense Tracking</h3>
      <button @click="showNewExpenseForm = true" class="new-expense-btn">
        ➕ Add Expense
      </button>
    </div>

    <!-- New Expense Form -->
    <div v-if="showNewExpenseForm" class="expense-form">
      <div class="form-group">
        <label>Amount</label>
        <input 
          v-model.number="newExpense.amount" 
          type="number" 
          step="0.01" 
          min="0"
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label>Date</label>
        <input 
          v-model="newExpense.date" 
          type="date" 
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label>Category</label>
        <select v-model="newExpense.category_id" class="form-input">
          <option value="">Select a category</option>
          <option 
            v-for="category in categories" 
            :key="category.id" 
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>Notes</label>
        <textarea 
          v-model="newExpense.notes" 
          rows="3"
          class="form-input"
        ></textarea>
      </div>

      <div class="form-group">
        <label>Receipt URL (optional)</label>
        <input 
          v-model="newExpense.receipt_url" 
          type="url" 
          placeholder="https://"
          class="form-input"
        >
      </div>

      <div class="form-actions">
        <button 
          @click="createExpense" 
          class="submit-btn"
          :disabled="!isValidExpense"
        >
          Save Expense
        </button>
        <button @click="showNewExpenseForm = false" class="cancel-btn">
          Cancel
        </button>
      </div>
    </div>

    <!-- Expenses Summary -->
    <div v-if="expenses.length > 0" class="expenses-summary">
      <div class="summary-item">
        <span class="summary-label">Total Expenses:</span>
        <span class="summary-value">{{ formatCurrency(totalExpenses) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">By Category:</span>
        <div class="category-breakdown">
          <div 
            v-for="(amount, category) in expensesByCategory" 
            :key="category"
            class="category-item"
          >
            {{ category }}: {{ formatCurrency(amount) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Expenses List -->
    <div v-if="expenses.length > 0" class="expenses-list">
      <div v-for="expense in expenses" :key="expense.id" class="expense-item">
        <div class="expense-info">
          <div class="expense-amount">
            💵 {{ formatCurrency(expense.amount) }}
          </div>
          <div class="expense-category">
            📁 {{ expense.category.name }}
          </div>
          <div class="expense-date">
            📅 {{ formatDate(expense.date) }}
          </div>
          <div class="expense-meta">
            Created by {{ expense.created_by }} on {{ formatDate(expense.created_at) }}
          </div>
          <div v-if="expense.notes" class="expense-notes">
            📝 {{ expense.notes }}
          </div>
          <div v-if="expense.receipt_url" class="expense-receipt">
            <a :href="expense.receipt_url" target="_blank" rel="noopener noreferrer">
              🧾 View Receipt
            </a>
          </div>
        </div>

        <div class="expense-actions">
          <button 
            @click="startEdit(expense)"
            class="action-btn"
          >
            ✏️ Edit
          </button>
          <button 
            @click="deleteExpense(expense.id)"
            class="action-btn delete"
          >
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>

    <p v-else class="no-expenses">
      No expenses recorded yet.
    </p>

    <!-- Edit Expense Modal -->
    <div v-if="editingExpense" class="modal">
      <div class="modal-content">
        <h3>Edit Expense</h3>
        
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
          <label>Date</label>
          <input 
            v-model="editForm.date" 
            type="date" 
            class="form-input"
          >
        </div>

        <div class="form-group">
          <label>Category</label>
          <select v-model="editForm.category_id" class="form-input">
            <option value="">Select a category</option>
            <option 
              v-for="category in categories" 
              :key="category.id" 
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Notes</label>
          <textarea 
            v-model="editForm.notes" 
            rows="3"
            class="form-input"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Receipt URL (optional)</label>
          <input 
            v-model="editForm.receipt_url" 
            type="url" 
            placeholder="https://"
            class="form-input"
          >
        </div>

        <div class="form-actions">
          <button 
            @click="updateExpense" 
            class="submit-btn"
            :disabled="!isValidEditForm"
          >
            Update Expense
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
import { ref, computed, onMounted } from 'vue'
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
const expenses = ref([])
const categories = ref([])
const showNewExpenseForm = ref(false)
const editingExpense = ref(null)
const newExpense = ref({
  amount: null,
  date: '',
  category_id: '',
  notes: '',
  receipt_url: ''
})
const editForm = ref({
  amount: null,
  date: '',
  category_id: '',
  notes: '',
  receipt_url: ''
})

// Computed
const isValidExpense = computed(() => {
  return newExpense.value.amount > 0 &&
         newExpense.value.date &&
         newExpense.value.category_id
})

const isValidEditForm = computed(() => {
  return editForm.value.amount > 0 &&
         editForm.value.date &&
         editForm.value.category_id
})

const totalExpenses = computed(() => {
  return expenses.value.reduce((sum, expense) => sum + expense.amount, 0)
})

const expensesByCategory = computed(() => {
  return expenses.value.reduce((acc, expense) => {
    const categoryName = expense.category.name
    acc[categoryName] = (acc[categoryName] || 0) + expense.amount
    return acc
  }, {})
})

// Methods
const fetchExpenses = async () => {
  try {
    const endpoint = props.taskId 
      ? `/expenses/task/${props.taskId}`
      : `/expenses/project/${props.projectId}`
    
    const response = await axios.get(endpoint)
    expenses.value = response.data
  } catch (error) {
    console.error('Failed to fetch expenses:', error)
  }
}

const fetchCategories = async () => {
  try {
    const response = await axios.get('/expenses/categories')
    categories.value = response.data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const createExpense = async () => {
  try {
    await axios.post('/expenses/', {
      ...newExpense.value,
      project_id: props.projectId,
      task_id: props.taskId
    })
    
    newExpense.value = {
      amount: null,
      date: '',
      category_id: '',
      notes: '',
      receipt_url: ''
    }
    showNewExpenseForm.value = false
    await fetchExpenses()
  } catch (error) {
    console.error('Failed to create expense:', error)
  }
}

const startEdit = (expense) => {
  editingExpense.value = expense.id
  editForm.value = {
    amount: expense.amount,
    date: expense.date.split('T')[0],
    category_id: expense.category.id,
    notes: expense.notes,
    receipt_url: expense.receipt_url
  }
}

const cancelEdit = () => {
  editingExpense.value = null
  editForm.value = {
    amount: null,
    date: '',
    category_id: '',
    notes: '',
    receipt_url: ''
  }
}

const updateExpense = async () => {
  try {
    await axios.put(`/expenses/${editingExpense.value}`, editForm.value)
    editingExpense.value = null
    await fetchExpenses()
  } catch (error) {
    console.error('Failed to update expense:', error)
  }
}

const deleteExpense = async (expenseId) => {
  if (!confirm('Are you sure you want to delete this expense?')) return

  try {
    await axios.delete(`/expenses/${expenseId}`)
    await fetchExpenses()
  } catch (error) {
    console.error('Failed to delete expense:', error)
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
onMounted(() => {
  fetchCategories()
  fetchExpenses()
})
</script>

<style scoped>
.expense-manager {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.expense-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.new-expense-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.new-expense-btn:hover {
  background: #2563eb;
}

.expense-form {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.expenses-summary {
  background: #f3f4f6;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.summary-item {
  margin-bottom: 0.5rem;
}

.summary-label {
  font-weight: 500;
  color: #4b5563;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #059669;
  margin-left: 0.5rem;
}

.category-breakdown {
  margin-top: 0.5rem;
  padding-left: 1rem;
}

.category-item {
  color: #4b5563;
  margin-bottom: 0.25rem;
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

.expenses-list {
  margin-top: 1rem;
}

.expense-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.expense-amount {
  font-size: 1.25rem;
  font-weight: 600;
  color: #059669;
  margin-bottom: 0.5rem;
}

.expense-category {
  color: #4b5563;
  margin-bottom: 0.25rem;
}

.expense-date {
  color: #4b5563;
  margin-bottom: 0.25rem;
}

.expense-meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.expense-notes {
  color: #4b5563;
  font-style: italic;
  margin-bottom: 0.25rem;
}

.expense-receipt a {
  color: #3b82f6;
  text-decoration: none;
}

.expense-receipt a:hover {
  text-decoration: underline;
}

.expense-actions {
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

.no-expenses {
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