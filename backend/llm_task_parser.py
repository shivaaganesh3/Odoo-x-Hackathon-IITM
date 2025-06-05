import os
import json
import logging
from datetime import datetime, date, timedelta
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from models import Users, TeamMembers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaturalLanguageTaskParser:
    """
    Natural Language Task Parser using Gemini + LangChain
    Extracts structured task information from natural language input
    """
    
    def __init__(self):
        """Initialize the parser with Gemini configuration"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize Gemini LLM with LangChain
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model="gemini-1.5-flash",  # Updated to current model name
            temperature=0.1,  # Low temperature for consistent parsing
            convert_system_message_to_human=True
        )
        
        logger.info("Natural Language Task Parser initialized with Gemini")

    def _get_system_prompt(self):
        """Get the system prompt for task parsing"""
        return """You are a smart task management assistant that extracts structured information from natural language task descriptions.

INSTRUCTIONS:
1. Extract task details from the user's natural language input
2. Return ONLY a valid JSON object with the specified fields
3. Be conservative - if you're unsure about a field, use null
4. For dates, use YYYY-MM-DD format
5. Match assignee names to real users when possible

REQUIRED OUTPUT FORMAT (JSON only, no other text):
{
    "title": "extracted task title (string)",
    "description": "detailed description if provided (string or null)",
    "assignee_name": "person's name mentioned for assignment (string or null)",
    "due_date": "extracted due date in YYYY-MM-DD format (string or null)",
    "priority": "urgent/high/medium/low based on context (string or null)",
    "effort_score": "1-5 scale if mentioned (integer 1-5 or null)",
    "impact_score": "1-5 scale if mentioned (integer 1-5 or null)",
    "extracted_info": {
        "confidence": "high/medium/low confidence in extraction",
        "date_context": "context used for date parsing",
        "assignee_context": "context used for assignee detection"
    }
}

EXAMPLES:
Input: "Remind John to finalize the pitch deck by Friday"
Output: {"title": "Finalize the pitch deck", "assignee_name": "John", "due_date": "[calculated Friday date]", "priority": null, "effort_score": null, "impact_score": null, "description": null, "extracted_info": {"confidence": "high", "date_context": "by Friday", "assignee_context": "John"}}

Input: "High priority task - Sarah needs to review the marketing budget this week"
Output: {"title": "Review the marketing budget", "assignee_name": "Sarah", "due_date": "[end of this week]", "priority": "high", "effort_score": null, "impact_score": null, "description": null, "extracted_info": {"confidence": "medium", "date_context": "this week", "assignee_context": "Sarah"}}

Input: "Create user documentation for the new feature"
Output: {"title": "Create user documentation for the new feature", "assignee_name": null, "due_date": null, "priority": null, "effort_score": null, "impact_score": null, "description": null, "extracted_info": {"confidence": "high", "date_context": "none", "assignee_context": "none"}}"""

    def _parse_relative_date(self, date_str, reference_date=None):
        """Parse relative dates like 'Friday', 'next week', 'tomorrow'"""
        if not date_str:
            return None
            
        if reference_date is None:
            reference_date = datetime.now()
            
        date_str = date_str.lower().strip()
        
        # Today/Tomorrow/Yesterday
        if 'today' in date_str:
            return reference_date.date()
        elif 'tomorrow' in date_str:
            return (reference_date + timedelta(days=1)).date()
        elif 'yesterday' in date_str:
            return (reference_date - timedelta(days=1)).date()
        
        # Days of the week
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if day in date_str:
                days_ahead = i - reference_date.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    if 'next' in date_str:
                        days_ahead += 7  # Next week
                    elif days_ahead == 0 and 'this' not in date_str:
                        days_ahead += 7  # Default to next occurrence
                return (reference_date + timedelta(days=days_ahead)).date()
        
        # Week-based
        if 'this week' in date_str:
            # End of this week (Friday)
            days_until_friday = (4 - reference_date.weekday()) % 7
            return (reference_date + timedelta(days=days_until_friday)).date()
        elif 'next week' in date_str:
            # End of next week
            days_until_next_friday = (4 - reference_date.weekday()) % 7 + 7
            return (reference_date + timedelta(days=days_until_next_friday)).date()
        
        # Month-based
        if 'this month' in date_str:
            # End of this month
            next_month = reference_date.replace(day=28) + timedelta(days=4)
            return (next_month - timedelta(days=next_month.day)).date()
        elif 'next month' in date_str:
            # End of next month
            next_month = reference_date + relativedelta(months=1)
            return (next_month.replace(day=28) + timedelta(days=4) - timedelta(days=(next_month.replace(day=28) + timedelta(days=4)).day)).date()
        
        # Try standard date parsing
        try:
            parsed_date = parse_date(date_str, fuzzy=True)
            return parsed_date.date()
        except:
            logger.warning(f"Could not parse date: {date_str}")
            return None

    def _find_team_member_by_name(self, name, project_id):
        """Find team member by name within the project"""
        if not name:
            return None
            
        logger.info(f"Looking for team member '{name}' in project {project_id}")
        
        # Get all team members for the project
        team_members = Users.query.join(TeamMembers).filter(
            TeamMembers.project_id == project_id
        ).all()
        
        name_lower = name.lower().strip()
        
        # Exact match first
        for user in team_members:
            if user.name and user.name.lower() == name_lower:
                logger.info(f"Found exact match: {user.name} (ID: {user.id})")
                return user.id
        
        # Partial match (first name, last name, or contains)
        for user in team_members:
            if user.name:
                user_name_lower = user.name.lower()
                name_parts = name_lower.split()
                user_parts = user_name_lower.split()
                
                # Check if any part of the search name matches any part of user name
                if any(part in user_parts for part in name_parts) or any(part in name_parts for part in user_parts):
                    logger.info(f"Found partial match: {user.name} (ID: {user.id})")
                    return user.id
        
        logger.warning(f"No team member found matching '{name}' in project {project_id}")
        return None

    def parse_natural_language_task(self, text, project_id=None):
        """
        Parse natural language input into structured task data
        
        Args:
            text (str): Natural language task description
            project_id (int): Project ID for team member lookup
            
        Returns:
            dict: Structured task data with extracted fields
        """
        try:
            logger.info(f"Parsing natural language task: '{text}'")
            
            # Prepare messages for Gemini
            system_message = SystemMessage(content=self._get_system_prompt())
            human_message = HumanMessage(content=f"Parse this task: {text}")
            
            # Call Gemini via LangChain
            response = self.llm([system_message, human_message])
            
            logger.info(f"Raw Gemini response: {response.content}")
            
            # Parse JSON response
            try:
                parsed_data = json.loads(response.content.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response content: {response.content}")
                # Return basic parsing fallback
                return self._fallback_parsing(text)
            
            # Post-process the parsed data
            result = self._post_process_parsed_data(parsed_data, project_id)
            
            logger.info(f"Final parsed result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing natural language task: {e}")
            # Return fallback parsing
            return self._fallback_parsing(text)

    def _post_process_parsed_data(self, parsed_data, project_id=None):
        """Post-process the parsed data from Gemini"""
        result = parsed_data.copy()
        
        # Parse due date if provided
        if result.get('due_date'):
            try:
                # Try to parse the date string
                parsed_date = self._parse_relative_date(result['due_date'])
                if parsed_date:
                    result['due_date'] = parsed_date.strftime('%Y-%m-%d')
                else:
                    result['due_date'] = None
            except Exception as e:
                logger.warning(f"Could not parse due date '{result['due_date']}': {e}")
                result['due_date'] = None
        
        # Find team member if assignee name is provided
        if result.get('assignee_name') and project_id:
            user_id = self._find_team_member_by_name(result['assignee_name'], project_id)
            result['assigned_to'] = user_id
        else:
            result['assigned_to'] = None
        
        # Validate effort and impact scores
        for score_field in ['effort_score', 'impact_score']:
            score = result.get(score_field)
            if score is not None:
                try:
                    score = int(score)
                    if score < 1 or score > 5:
                        result[score_field] = None
                    else:
                        result[score_field] = score
                except (ValueError, TypeError):
                    result[score_field] = None
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if result.get('priority'):
            if result['priority'].lower() not in valid_priorities:
                result['priority'] = None
            else:
                result['priority'] = result['priority'].title()
        
        return result

    def _fallback_parsing(self, text):
        """Simple fallback parsing if Gemini fails"""
        logger.info("Using fallback parsing")
        
        # Basic title extraction (use the whole text, cleaned up)
        title = text.strip()
        if len(title) > 150:
            title = title[:147] + "..."
        
        # Try to extract simple patterns
        assignee_name = None
        due_date = None
        
        # Look for name patterns (e.g., "John", "Sarah needs to", "remind Alex")
        name_patterns = [
            r'remind\s+(\w+)',
            r'(\w+)\s+(?:needs to|should|must)',
            r'assign(?:ed)?\s+to\s+(\w+)',
            r'for\s+(\w+)\s+to'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                assignee_name = match.group(1)
                break
        
        # Look for date patterns
        date_patterns = [
            r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'by\s+(tomorrow|today)',
            r'(this|next)\s+week',
            r'by\s+(\d{4}-\d{2}-\d{2})',
            r'due\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1) if len(match.groups()) > 0 else match.group(0)
                parsed_date = self._parse_relative_date(date_str)
                if parsed_date:
                    due_date = parsed_date.strftime('%Y-%m-%d')
                break
        
        return {
            'title': title,
            'description': None,
            'assignee_name': assignee_name,
            'assigned_to': None,  # Will be resolved later
            'due_date': due_date,
            'priority': None,
            'effort_score': None,
            'impact_score': None,
            'extracted_info': {
                'confidence': 'low',
                'date_context': 'fallback parsing',
                'assignee_context': 'fallback parsing'
            }
        }


# Global parser instance (can be reused)
_parser_instance = None

def get_task_parser():
    """Get singleton instance of the task parser"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = NaturalLanguageTaskParser()
    return _parser_instance 