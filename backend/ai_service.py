import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Setup the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def prioritize_tasks_with_ai(tasks_list):
    """
    Expects a list of dicts: [{'id': 1, 'title': '...', 'description': '...', 'deadline': '...', 'priority': '...'}]
    Returns a ordered list of task IDs: [1, 3, 2]
    """
    prompt_template = """
    You are an elite productivity coach and task management assistant. 
    Analyze the following list of pending tasks and determine the absolute best order to complete them.
    Consider high priority tags, urgent approaching deadlines, and the nature of the tasks.

    Tasks JSON data:
    {tasks_data}

    Return ONLY a raw valid JSON array of integers containing the task IDs in the recommended execution order (first to last). 
    Do not include any markdown syntax, code wrappers (like ```json), or conversational prose. 
    Example Output format: [2, 1, 3]
    """
    
    # Standardize data to string for prompt insertion
    formatted_tasks = json.dumps(tasks_list, default=str)
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"tasks_data": formatted_tasks})
        
        # Strip any formatting slip-ups from the LLM response
        clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_content)
    except Exception as e:
        print(f"AI Optimization Error: {e}")
        # Fallback to current DB structure array if something breaks
        return [t['id'] for t in tasks_list]
    
def breakdown_task_with_ai(title, description):
    """
    Takes a task title/description and returns a list of 3-5 sub-task strings.
    """
    prompt_template = """
    You are an expert project management assistant. 
    Break down the following major task into an actionable, step-by-step checklist of 3 to 5 clear sub-tasks.

    Task Title: {title}
    Task Description: {description}

    Return ONLY a raw valid JSON array of strings representing the sub-tasks.
    Do not include markdown wrappers like ```json or any extra text.
    Example Output: ["Sub-task step 1", "Sub-task step 2", "Sub-task step 3"]
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"title": title, "description": description or "No description provided"})
        clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        print(f"AI Breakdown Error: {e}")
        return ["Research requirements", "Execute main implementation", "Verify and test work"]