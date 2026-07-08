import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Setup the Gemini LLM cleanly (Let the prompt explicitly dictate structural parsing)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    temperature=0.1
)

def prioritize_tasks_with_ai(tasks_list):
    """
    Expects a list of dicts: [{'id': 1, 'title': '...', 'description': '...', 'deadline': '...', 'priority': '...'}]
    Returns an ordered list of task IDs: [1, 3, 2]
    """
    prompt_template = """
    You are an elite productivity coach. Analyze this JSON list of pending tasks and determine the absolute best order to complete them based on priority tags and deadlines.

    Tasks JSON data:
    {tasks_data}

    Return ONLY a raw valid JSON array of integers containing the task IDs in the recommended execution order.
    Do not include any markdown formatting syntax, conversational text, or block wrappers like ```json.
    Example Output: [2, 1, 3]
    """
    
    formatted_tasks = json.dumps(tasks_list, default=str)
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"tasks_data": formatted_tasks})
        clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        print(f"AI Optimization Error: {e}")
        return [t['id'] for t in tasks_list]
    
def breakdown_task_with_ai(title, description):
    """
    Takes a task title/description and returns a dynamic list of 3-5 sub-task strings.
    """
    prompt_template = """
    You are an expert project management assistant. 
    Break down the following major task into an actionable checklist of 3 to 5 clear, unique sub-tasks.

    Task Title: {title}
    Task Description: {description}

    Return ONLY a raw valid JSON array of strings representing the unique sub-tasks.
    Do not include markdown wrappers or extra conversational text.
    Example Output: ["Step one info", "Step two info", "Step three info"]
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"title": title, "description": description or "No description provided"})
        clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        print(f"AI Breakdown Error: {e}")
        # DYNAMIC FALLBACK: If the API blips, generate a unique list matching the user's title
        return [f"Analyze requirements for {title}", f"Build prototype implementation for {title}", f"Test complete workflow execution for {title}"]