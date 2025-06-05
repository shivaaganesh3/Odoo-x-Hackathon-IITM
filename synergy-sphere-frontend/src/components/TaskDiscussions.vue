<template>
  <div class="task-discussions">
    <div class="discussions-header">
      <h3>💬 Task Discussions</h3>
      <button @click="showNewDiscussionForm = true" class="new-discussion-btn">
        ➕ New Discussion
      </button>
    </div>

    <!-- New Discussion Form -->
    <div v-if="showNewDiscussionForm" class="new-discussion-form">
      <textarea 
        v-model="newMessage" 
        placeholder="Start a new discussion..."
        rows="3"
        class="discussion-input"
      ></textarea>
      <div class="form-actions">
        <button @click="createDiscussion" class="submit-btn" :disabled="!newMessage.trim()">
          Post
        </button>
        <button @click="showNewDiscussionForm = false" class="cancel-btn">
          Cancel
        </button>
      </div>
    </div>

    <!-- Discussions List -->
    <div v-if="discussions.length > 0" class="discussions-list">
      <div v-for="discussion in discussions" :key="discussion.id" class="discussion-item">
        <div class="discussion-header">
          <span class="author">{{ discussion.author_name }}</span>
          <span class="timestamp">{{ formatDate(discussion.timestamp) }}</span>
        </div>
        
        <div class="discussion-content">
          <p v-if="!editingDiscussion[discussion.id]">{{ discussion.message }}</p>
          <div v-else class="edit-form">
            <textarea 
              v-model="editMessage[discussion.id]" 
              rows="3"
              class="discussion-input"
            ></textarea>
            <div class="form-actions">
              <button @click="updateDiscussion(discussion.id)" class="submit-btn">
                Save
              </button>
              <button @click="cancelEdit(discussion.id)" class="cancel-btn">
                Cancel
              </button>
            </div>
          </div>
        </div>

        <div class="discussion-actions">
          <button 
            v-if="discussion.user_id === currentUserId" 
            @click="startEdit(discussion)"
            class="action-btn"
          >
            ✏️ Edit
          </button>
          <button 
            v-if="discussion.user_id === currentUserId"
            @click="deleteDiscussion(discussion.id)"
            class="action-btn delete"
          >
            🗑️ Delete
          </button>
          <button 
            @click="showReplyForm[discussion.id] = !showReplyForm[discussion.id]"
            class="action-btn"
          >
            ↩️ Reply
          </button>
          <button 
            v-if="discussion.replies_count > 0"
            @click="loadReplies(discussion.id)"
            class="action-btn"
          >
            {{ showReplies[discussion.id] ? '⬆️ Hide' : `⬇️ Show ${discussion.replies_count} ${discussion.replies_count === 1 ? 'reply' : 'replies'}` }}
          </button>
        </div>

        <!-- Reply Form -->
        <div v-if="showReplyForm[discussion.id]" class="reply-form">
          <textarea 
            v-model="replyMessage[discussion.id]" 
            placeholder="Write a reply..."
            rows="2"
            class="discussion-input"
          ></textarea>
          <div class="form-actions">
            <button 
              @click="createReply(discussion.id)" 
              class="submit-btn"
              :disabled="!replyMessage[discussion.id]?.trim()"
            >
              Reply
            </button>
            <button @click="showReplyForm[discussion.id] = false" class="cancel-btn">
              Cancel
            </button>
          </div>
        </div>

        <!-- Replies -->
        <div v-if="showReplies[discussion.id] && replies[discussion.id]" class="replies-list">
          <div v-for="reply in replies[discussion.id]" :key="reply.id" class="reply-item">
            <div class="discussion-header">
              <span class="author">{{ reply.author_name }}</span>
              <span class="timestamp">{{ formatDate(reply.timestamp) }}</span>
            </div>
            <p>{{ reply.message }}</p>
          </div>
        </div>
      </div>
    </div>

    <p v-else class="no-discussions">
      No discussions yet. Start a conversation!
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'

const props = defineProps({
  taskId: {
    type: Number,
    required: true
  },
  projectId: {
    type: Number,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

// State
const discussions = ref([])
const replies = ref({})
const showReplyForm = ref({})
const showReplies = ref({})
const replyMessage = ref({})
const showNewDiscussionForm = ref(false)
const newMessage = ref('')
const editingDiscussion = ref({})
const editMessage = ref({})

// Load discussions
const fetchDiscussions = async () => {
  try {
    const response = await axios.get(`/discussions/task/${props.taskId}`)
    discussions.value = response.data
  } catch (error) {
    console.error('Failed to fetch discussions:', error)
  }
}

// Create new discussion
const createDiscussion = async () => {
  try {
    await axios.post('/discussions/', {
      message: newMessage.value,
      project_id: props.projectId,
      task_id: props.taskId
    })
    newMessage.value = ''
    showNewDiscussionForm.value = false
    await fetchDiscussions()
  } catch (error) {
    console.error('Failed to create discussion:', error)
  }
}

// Load replies for a discussion
const loadReplies = async (discussionId) => {
  if (showReplies.value[discussionId] && replies.value[discussionId]) {
    showReplies.value[discussionId] = false
    return
  }

  try {
    const response = await axios.get(`/discussions/${discussionId}/replies`)
    replies.value[discussionId] = response.data
    showReplies.value[discussionId] = true
  } catch (error) {
    console.error('Failed to load replies:', error)
  }
}

// Create reply
const createReply = async (discussionId) => {
  try {
    await axios.post('/discussions/', {
      message: replyMessage.value[discussionId],
      project_id: props.projectId,
      task_id: props.taskId,
      parent_id: discussionId
    })
    replyMessage.value[discussionId] = ''
    showReplyForm.value[discussionId] = false
    await fetchDiscussions()
    if (showReplies.value[discussionId]) {
      await loadReplies(discussionId)
    }
  } catch (error) {
    console.error('Failed to create reply:', error)
  }
}

// Edit discussion
const startEdit = (discussion) => {
  editingDiscussion.value[discussion.id] = true
  editMessage.value[discussion.id] = discussion.message
}

const cancelEdit = (discussionId) => {
  editingDiscussion.value[discussionId] = false
  editMessage.value[discussionId] = ''
}

const updateDiscussion = async (discussionId) => {
  try {
    await axios.put(`/discussions/${discussionId}`, {
      message: editMessage.value[discussionId]
    })
    editingDiscussion.value[discussionId] = false
    await fetchDiscussions()
  } catch (error) {
    console.error('Failed to update discussion:', error)
  }
}

// Delete discussion
const deleteDiscussion = async (discussionId) => {
  if (!confirm('Are you sure you want to delete this discussion?')) return

  try {
    await axios.delete(`/discussions/${discussionId}`)
    await fetchDiscussions()
  } catch (error) {
    console.error('Failed to delete discussion:', error)
  }
}

// Format date
const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

// Load initial discussions
onMounted(fetchDiscussions)
</script>

<style scoped>
.task-discussions {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.discussions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.new-discussion-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.new-discussion-btn:hover {
  background: #2563eb;
}

.discussion-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  font-family: inherit;
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

.discussions-list {
  margin-top: 1rem;
}

.discussion-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.discussion-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: #4b5563;
  font-size: 0.875rem;
}

.author {
  font-weight: 500;
}

.timestamp {
  color: #6b7280;
}

.discussion-content {
  margin: 0.5rem 0;
  line-height: 1.5;
}

.discussion-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
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

.reply-form {
  margin: 0.5rem 0;
  padding-left: 1rem;
  border-left: 2px solid #e5e7eb;
}

.replies-list {
  margin-top: 0.5rem;
  padding-left: 1rem;
  border-left: 2px solid #e5e7eb;
}

.reply-item {
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  background: #f9fafb;
  border-radius: 4px;
}

.no-discussions {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 2rem;
}
</style> 