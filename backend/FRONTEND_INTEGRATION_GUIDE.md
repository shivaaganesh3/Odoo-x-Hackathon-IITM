# 🧠 Frontend Integration Guide for AI Task Feature

## Current Status
- ✅ **Backend**: Fully implemented with `/api/task/parse-nl-task` endpoint
- ❌ **Frontend**: Needs to be created

## Quick Integration Steps

### 1. Add AI Button to ProjectTasks.vue

Add this button near the existing task creation form in `synergy-sphere-frontend/src/pages/ProjectTasks.vue`:

```vue
<!-- Add this before the existing task form -->
<div class="ai-task-section">
  <button @click="showAiInput = !showAiInput" class="ai-toggle-btn">
    🧠 {{ showAiInput ? 'Hide' : 'Show' }} AI Task Input
  </button>
  
  <!-- Simple AI Input -->
  <div v-if="showAiInput" class="ai-input-area">
    <textarea
      v-model="aiTaskText"
      placeholder="Describe your task naturally... (e.g., 'Remind John to finish the presentation by Friday')"
      class="ai-textarea"
      rows="3"
    ></textarea>
    
    <div class="ai-actions">
      <button @click="parseAiTask" :disabled="isParsingAi" class="ai-parse-btn">
        {{ isParsingAi ? '🔄 Parsing...' : '🧠 Parse Task' }}
      </button>
    </div>
    
    <!-- Show parsed result -->
    <div v-if="aiParsedTask" class="ai-result">
      <h4>🎯 Parsed Result:</h4>
      <p><strong>Title:</strong> {{ aiParsedTask.title }}</p>
      <p><strong>Assignee:</strong> {{ aiParsedTask.parsing_info?.resolved_assignee?.name || 'Not found' }}</p>
      <p><strong>Due Date:</strong> {{ aiParsedTask.due_date || 'Not specified' }}</p>
      
      <button @click="fillFormFromAi" class="fill-form-btn">
        📝 Fill Manual Form
      </button>
      <button @click="createTaskDirectly" class="create-direct-btn">
        ✅ Create Task Directly
      </button>
    </div>
  </div>
</div>
```

### 2. Add Methods to ProjectTasks.vue

Add these methods to the existing script section:

```javascript
// Add these reactive variables
const showAiInput = ref(false)
const aiTaskText = ref('')
const aiParsedTask = ref(null)
const isParsingAi = ref(false)

// Add these methods
const parseAiTask = async () => {
  if (!aiTaskText.value.trim()) return
  
  isParsingAi.value = true
  try {
    const response = await axios.post('/tasks/parse-nl-task', {
      text: aiTaskText.value,
      project_id: projectId
    })
    aiParsedTask.value = response.data
  } catch (error) {
    alert('Failed to parse task: ' + (error.response?.data?.error || error.message))
  } finally {
    isParsingAi.value = false
  }
}

const fillFormFromAi = () => {
  if (!aiParsedTask.value) return
  
  // Fill the existing newTask form
  newTask.value.title = aiParsedTask.value.title || ''
  newTask.value.description = aiParsedTask.value.description || ''
  newTask.value.due_date = aiParsedTask.value.due_date || ''
  newTask.value.assigned_to = aiParsedTask.value.assigned_to || null
  newTask.value.effort_score = aiParsedTask.value.effort_score || 3
  newTask.value.impact_score = aiParsedTask.value.impact_score || 3
  newTask.value.status_id = aiParsedTask.value.status_id || (customStatuses.value.find(s => s.is_default)?.id || '')
  
  // Clear AI section
  aiTaskText.value = ''
  aiParsedTask.value = null
  showAiInput.value = false
  
  alert('Form filled with AI data! Please review and submit.')
}

const createTaskDirectly = async () => {
  if (!aiParsedTask.value) return
  
  try {
    await axios.post('/tasks/', {
      ...aiParsedTask.value,
      project_id: projectId
    })
    
    // Clear AI section
    aiTaskText.value = ''
    aiParsedTask.value = null
    showAiInput.value = false
    
    fetchTasks()
    alert('AI task created successfully! 🎉')
  } catch (error) {
    alert('Failed to create task: ' + (error.response?.data?.error || error.message))
  }
}
```

### 3. Add CSS Styles

Add these styles to ProjectTasks.vue:

```css
.ai-task-section {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.ai-toggle-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin-bottom: 1rem;
}

.ai-input-area {
  margin-top: 1rem;
}

.ai-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 1rem;
}

.ai-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.ai-parse-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.ai-parse-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.ai-result {
  background: white;
  border: 2px solid #10b981;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.fill-form-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.create-direct-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
```

## 🚀 Testing Steps

1. **Set your Gemini API key** in `backend/.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

2. **Start the backend**:
   ```bash
   cd backend
   python app.py
   ```

3. **Start the frontend**:
   ```bash
   cd synergy-sphere-frontend
   npm run dev
   ```

4. **Test the AI feature**:
   - Go to any project's tasks page
   - Click "🧠 Show AI Task Input"
   - Type: "Remind John to finish the presentation by Friday"
   - Click "🧠 Parse Task"
   - Review the results and create the task

## 📋 Example Test Cases

Try these natural language inputs:
- `"Remind John to finalize the pitch deck by Friday"`
- `"High priority task - Sarah needs to review the marketing budget this week"`
- `"Create user documentation for the new feature"`
- `"Alex should complete the database migration by tomorrow"`
- `"Urgent: Fix the login bug"`

## 🎯 Future Enhancements

After basic integration:
- [ ] Better error handling and user feedback
- [ ] Confidence indicators
- [ ] Bulk task creation
- [ ] Voice input support
- [ ] Learning from user corrections

The AI feature is **ready to use** once you add this simple frontend integration! 🧠✨ 