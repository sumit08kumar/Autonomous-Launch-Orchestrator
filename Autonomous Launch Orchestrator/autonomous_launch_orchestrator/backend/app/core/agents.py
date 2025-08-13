from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
import json
import uuid
from datetime import datetime, timedelta

class PlannerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)        
    def create_launch_plan(self, goal: str) -> list:
        """Create a structured launch plan from a high-level goal"""
        prompt = ChatPromptTemplate.from_template("""
        You are a launch planning expert. Given a high-level launch goal, break it down into specific, actionable tasks.
        
        Goal: {goal}
        
        Create a JSON list of tasks with the following structure:
        [
            {{
                "task_id": "unique_id",
                "role": "marketing|developer|legal|sales",
                "description": "specific task description",
                "deadline": "YYYY-MM-DD",
                "priority": "high|medium|low"
            }}
        ]
        
        Consider typical launch activities:
        - Marketing: social media campaigns, blog posts, press releases
        - Developer: code releases, documentation updates, bug fixes
        - Legal: compliance reviews, terms updates, privacy policies
        - Sales: customer outreach, pricing updates, sales materials
        
        Return only the JSON array, no additional text.
        """)
        
        response = self.llm.invoke(prompt.format(goal=goal))
        try:
            tasks = json.loads(response.content)
            return tasks
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._create_default_plan(goal)
    
    def _create_default_plan(self, goal: str) -> list:
        """Fallback plan if LLM response can't be parsed"""
        base_date = datetime.now()
        return [
            {
                "task_id": str(uuid.uuid4()),
                "role": "marketing",
                "description": f"Create social media campaign for {goal}",
                "deadline": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "priority": "high"
            },
            {
                "task_id": str(uuid.uuid4()),
                "role": "developer",
                "description": f"Prepare release documentation for {goal}",
                "deadline": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                "priority": "high"
            },
            {
                "task_id": str(uuid.uuid4()),
                "role": "sales",
                "description": f"Update sales materials for {goal}",
                "deadline": (base_date + timedelta(days=10)).strftime("%Y-%m-%d"),
                "priority": "medium"
            }
        ]

class RoleAgent:
    def __init__(self, role: str):
        self.role = role
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)        
    def generate_content(self, task_description: str) -> str:
        """Generate role-specific content for a task"""
        role_prompts = {
            "marketing": """
            You are a marketing expert. Create engaging marketing content for the following task:
            Task: {task}
            
            Provide specific, actionable marketing content (social media posts, email copy, etc.).
            """,
            "developer": """
            You are a senior developer. Create technical content for the following task:
            Task: {task}
            
            Provide specific technical deliverables (release notes, documentation, etc.).
            """,
            "legal": """
            You are a legal compliance expert. Create legal content for the following task:
            Task: {task}
            
            Provide specific legal deliverables (compliance checklists, policy updates, etc.).
            """,
            "sales": """
            You are a sales expert. Create sales content for the following task:
            Task: {task}
            
            Provide specific sales deliverables (email templates, pricing sheets, etc.).
            """
        }
        
        prompt = role_prompts.get(self.role, role_prompts["marketing"])
        response = self.llm.invoke(prompt.format(task=task_description))
        return response.content

