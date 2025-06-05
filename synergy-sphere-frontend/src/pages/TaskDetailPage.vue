<template>
  <!-- Add budget and expense management -->
  <div class="task-finances">
    <FundsUsageTracker :task-id="taskId" :project-id="projectId" />
    <BudgetManager :task-id="taskId" :project-id="projectId" />
    <ExpenseManager :task-id="taskId" :project-id="projectId" />
  </div>

  <!-- Task discussions -->
  <TaskDiscussions :task-id="taskId" :project-id="projectId" :current-user-id="currentUser.id" />
</template>

<script>
import TaskDiscussions from '../components/TaskDiscussions.vue'
import FundsUsageTracker from '../components/FundsUsageTracker.vue'
import BudgetManager from '../components/BudgetManager.vue'
import ExpenseManager from '../components/ExpenseManager.vue'

export default {
  components: {
    TaskDiscussions,
    FundsUsageTracker,
    BudgetManager,
    ExpenseManager
  },
  data() {
    return {
      taskId: this.$route.params.taskId,
      projectId: this.$route.params.projectId,
      currentUser: this.$store.state.user
    }
  }
}
</script>

<style>
  /* Add your styles here */
</style> 