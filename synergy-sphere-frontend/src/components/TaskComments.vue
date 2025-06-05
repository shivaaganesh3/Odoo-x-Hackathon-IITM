<template>
  <div class="task-comments">
    <h3>Comments</h3>
    
    <!-- Comment Form -->
    <form @submit.prevent="submitComment" class="comment-form">
      <textarea
        v-model="newComment"
        placeholder="Write a comment..."
        required
        class="comment-input"
      ></textarea>
      <button type="submit" class="submit-btn">Post Comment</button>
    </form>

    <!-- Comments List -->
    <div class="comments-list">
      <div v-for="comment in comments" :key="comment.id" class="comment">
        <div class="comment-header">
          <span class="author">{{ comment.user_name }}</span>
          <span class="timestamp">{{ formatDate(comment.timestamp) }}</span>
        </div>
        <div class="comment-content">{{ comment.content }}</div>
        
        <!-- Reply Form -->
        <div class="reply-form" v-if="replyingTo === comment.id">
          <textarea
            v-model="replyContent"
            placeholder="Write a reply..."
            required
            class="reply-input"
          ></textarea>
          <div class="reply-actions">
            <button @click="submitReply(comment.id)" class="submit-btn">Reply</button>
            <button @click="cancelReply" class="cancel-btn">Cancel</button>
          </div>
        </div>
        
        <!-- Reply Button -->
        <button 
          v-if="replyingTo !== comment.id"
          @click="startReply(comment.id)"
          class="reply-btn"
        >
          Reply
        </button>

        <!-- Replies -->
        <div class="replies" v-if="comment.replies && comment.replies.length">
          <div v-for="reply in comment.replies" :key="reply.id" class="reply">
            <div class="comment-header">
              <span class="author">{{ reply.user_name }}</span>
              <span class="timestamp">{{ formatDate(reply.timestamp) }}</span>
            </div>
            <div class="comment-content">{{ reply.content }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'

const props = defineProps({
  taskId: {
    type: Number,
    required: true
  }
})

const comments = ref([])
const newComment = ref('')
const replyContent = ref('')
const replyingTo = ref(null)

// Fetch comments
const fetchComments = async () => {
  try {
    const response = await axios.get(`/task-comments/task/${props.taskId}`)
    comments.value = response.data
  } catch (error) {
    console.error('Failed to fetch comments:', error)
  }
}

// Submit new comment
const submitComment = async () => {
  try {
    await axios.post('/task-comments/', {
      task_id: props.taskId,
      content: newComment.value
    })
    newComment.value = ''
    await fetchComments()
  } catch (error) {
    console.error('Failed to post comment:', error)
  }
}

// Start reply
const startReply = (commentId) => {
  replyingTo.value = commentId
  replyContent.value = ''
}

// Cancel reply
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

// Submit reply
const submitReply = async (parentId) => {
  try {
    await axios.post('/task-comments/', {
      task_id: props.taskId,
      content: replyContent.value,
      parent_id: parentId
    })
    replyContent.value = ''
    replyingTo.value = null
    await fetchComments()
  } catch (error) {
    console.error('Failed to post reply:', error)
  }
}

// Format date
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(fetchComments)
</script>

<style scoped>
.task-comments {
  margin-top: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.comment-form {
  margin-bottom: 2rem;
}

.comment-input, .reply-input {
  width: 100%;
  min-height: 80px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  resize: vertical;
}

.submit-btn, .reply-btn, .cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.submit-btn {
  background-color: #10b981;
  color: white;
}

.reply-btn {
  background-color: #e5e7eb;
  color: #374151;
}

.cancel-btn {
  background-color: #ef4444;
  color: white;
  margin-left: 0.5rem;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.author {
  font-weight: 600;
  color: #1f2937;
}

.timestamp {
  color: #6b7280;
}

.comment-content {
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.replies {
  margin-left: 2rem;
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid #e5e7eb;
}

.reply {
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.reply-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
</style> 