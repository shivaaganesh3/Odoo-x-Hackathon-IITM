# 🧠 Natural Language Task Parser

## Overview

The **Natural Language Task Parser** allows users to create tasks using natural language input like:
- `"Remind John to finalize the pitch deck by Friday"`
- `"High priority task - Sarah needs to review the marketing budget this week"`
- `"Create user documentation for the new feature"`

The system uses **Gemini + LangChain** to intelligently extract structured task information.

## 🚀 Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set the environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 3. Test the Parser

```bash
cd backend
python test_nl_task_parser.py
```

## 📡 API Endpoint

### `POST /api/task/parse-nl-task`

Parses natural language input into structured task data.

#### Request Body
```json
{
  "text": "Remind John to finalize the pitch deck by Friday",
  "project_id": 2
}
```

#### Response
```json
{
  "title": "Finalize the pitch deck",
  "description": null,
  "assigned_to": 5,
  "due_date": "2024-01-26",
  "status_id": 1,
  "project_id": 2,
  "priority": "Medium",
  "effort_score": 3,
  "impact_score": 3,
  "parsing_info": {
    "confidence": "high",
    "assignee_name": "John",
    "date_context": "by Friday",
    "assignee_context": "John",
    "original_text": "Remind John to finalize the pitch deck by Friday",
    "resolved_assignee": {
      "id": 5,
      "name": "John Smith",
      "email": "john@example.com"
    }
  },
  "default_status": {
    "id": 1,
    "name": "To Do",
    "color": "#6B7280"
  }
}
```

#### Error Response
```json
{
  "error": "Project not found or user not authorized",
  "warnings": [
    "Could not find team member 'John' in project",
    "Low confidence in parsing results - please review"
  ]
}
```

## 🎯 Features

### Smart Extraction
- **Task Title**: Extracted from the main action/objective
- **Assignee**: Matches names to existing team members in the project
- **Due Date**: Parses relative dates (Friday, next week, tomorrow, etc.)
- **Priority**: Detects priority keywords (urgent, high, low, etc.)
- **Effort/Impact**: Extracts if mentioned explicitly

### Date Parsing Examples
- `"by Friday"` → Next Friday
- `"tomorrow"` → Tomorrow's date
- `"this week"` → End of current week
- `"next Monday"` → Following Monday
- `"2024-02-15"` → Specific date

### Assignee Resolution
- Matches names against team members in the specified project
- Supports partial name matching (first name, last name)
- Returns user ID for found matches

## 🧪 Testing with Thunder Client/Postman

### Example Request

```bash
POST http://localhost:5000/api/task/parse-nl-task
Content-Type: application/json
Authorization: Bearer YOUR_AUTH_TOKEN

{
  "text": "Remind Sarah to review the budget proposal by next Friday - high priority",
  "project_id": 1
}
```

### Test Cases

1. **Basic Task Assignment**
   ```json
   {"text": "John needs to update the documentation", "project_id": 1}
   ```

2. **With Due Date**
   ```json
   {"text": "Complete the database migration by tomorrow", "project_id": 1}
   ```

3. **With Priority**
   ```json
   {"text": "Urgent: Fix the login bug", "project_id": 1}
   ```

4. **Complex Task**
   ```json
   {"text": "High priority - Maria should finalize the client presentation by Friday", "project_id": 1}
   ```

## 🛠️ Architecture

### Components

1. **`llm_task_parser.py`** - Core parsing logic using Gemini
2. **`/api/task/parse-nl-task`** - Flask endpoint in `routes/task.py`
3. **Fallback Parser** - Regex-based backup when LLM fails

### Data Flow

```
Natural Language Input
        ↓
Gemini LLM Processing
        ↓
JSON Structure Extraction
        ↓
Post-processing & Validation
        ↓
Team Member Resolution
        ↓
Structured Task Data
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY` - Required for LLM functionality

### Fallback Behavior
- If Gemini is unavailable, uses regex-based parsing
- Gracefully handles API failures
- Provides confidence scoring

## 🚨 Error Handling

- Invalid API key → Clear error message with setup instructions
- Network issues → Falls back to regex parsing
- Malformed JSON from LLM → Uses fallback parser
- Unknown team members → Warning in response
- Missing project permissions → 403 Forbidden

## 💡 Integration Tips

### Frontend Integration
1. Create a text input for natural language
2. Call the parsing endpoint
3. Show parsed results for user confirmation
4. Allow editing before final task creation
5. Use existing task creation logic

### Best Practices
- Always validate parsed results before creating tasks
- Show confidence levels to users
- Provide fallback manual entry
- Log parsing results for debugging
- Handle API rate limits gracefully

## 🔍 Debugging

### Check Logs
```bash
# View parsing logs
tail -f app.log | grep "llm_task_parser"
```

### Test Parser Directly
```bash
python test_nl_task_parser.py
```

### Common Issues
1. **API Key Issues**: Check environment variable
2. **Import Errors**: Install all dependencies
3. **Database Errors**: Ensure Flask app context
4. **Low Confidence**: Review and adjust prompts

## 📈 Future Enhancements

- [ ] Support for bulk task creation
- [ ] Project context awareness
- [ ] Custom parsing rules per project
- [ ] Voice input integration
- [ ] Multi-language support
- [ ] Learning from user corrections 