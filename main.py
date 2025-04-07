import json
from typing import Literal, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Import from helper scripts
from utils import parse_email, format_few_shot_examples
from schemas import Router, State  # Assume State updated with history
from prompts import agent_system_prompt_memory, triage_system_prompt, triage_user_prompt
from email_inputs import get_email_input

# Load environment variables
load_dotenv()

# Constants
PROFILE = {
    "name": "Anamay",
    "full_name": "Anamay Deshapdne",
    "user_profile_background": "Junior Data Scientist working with a team of 3 data scientists\
        and 2 data engineers to build a recommendation system",
}

PROMPT_INSTRUCTIONS = {
    "triage_rules": {
        "ignore": "Marketing newsletters, spam emails, mass company announcements",
        "notify": "Team member out sick, build system notifications, project status updates",
        "respond": "Direct questions from team members, meeting requests, critical bug reports",
    },
    "agent_instructions": "Use these tools when appropriate to help manage John's tasks efficiently."
}

# Initialize embedding model and store
embedder = SentenceTransformer('all-MiniLM-L6-v2')
store = InMemoryStore(index={"embed": embedder.encode})

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
llm_router = llm.with_structured_output(Router)

# Define tools
@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write and send an email."""
    return f"Email sent to {to} with subject '{subject}'"

@tool
def schedule_meeting(attendees: List[str], subject: str, duration_minutes: int, preferred_day: str) -> str:
    """Schedule a calendar meeting."""
    return f"Meeting '{subject}' scheduled for {preferred_day} with {len(attendees)} attendees"

@tool
def check_calendar_availability(day: str) -> str:
    """Check calendar availability for a given day."""
    return f"Available times on {day}: 9:00 AM, 2:00 PM, 4:00 PM"

tools = [write_email, schedule_meeting, check_calendar_availability]

# Prompt creation for response agent
def create_prompt(state: State, config: dict) -> list:
    history_str = "\n".join([f"{h['email']['subject']}: {h['label']}" for h in state.get("history", [])])
    return [
        {"role": "system", "content": agent_system_prompt_memory.format(
            instructions=PROMPT_INSTRUCTIONS["agent_instructions"] + f"\nPast: {history_str}", **PROFILE)}
    ] + state["messages"]

# Update rules based on feedback
def update_rules_and_store(feedback: str, email: dict, classification: str, namespace: tuple):
    if feedback != classification:
        prompt = f"Email: {email}\nClassified as: {classification}\nFeedback: {feedback}\nSuggest rule update and corrected label:"
        response = llm.invoke(prompt).content
        if "add to" in response.lower():
            rule, addition = response.split("add to ")[1].split(":")
            PROMPT_INSTRUCTIONS["triage_rules"][rule.strip()] += f", {addition.strip()}"
        corrected_label = feedback if "label:" not in response else response.split("label:")[1].strip()
        store.put(namespace, str(email), {"email": email, "label": corrected_label})
    else:
        store.put(namespace, str(email), {"email": email, "label": classification})

# Triage router function
def triage_router(state: State, config: dict) -> dict:
    author, to, subject, email_thread = parse_email(state["email_input"])
    namespace = ("email_assistant", config["configurable"]["langgraph_user_id"], "examples")
    
    # Get few-shot examples
    examples = store.search(namespace, query=str({"email": state["email_input"]}))
    formatted_examples = format_few_shot_examples(examples) if examples else ""
    
    # Format triage prompt
    system_prompt = triage_system_prompt.format(
        full_name=PROFILE["full_name"],
        name=PROFILE["name"],
        user_profile_background=PROFILE["user_profile_background"],
        triage_no=PROMPT_INSTRUCTIONS["triage_rules"]["ignore"],
        triage_notify=PROMPT_INSTRUCTIONS["triage_rules"]["notify"],
        triage_email=PROMPT_INSTRUCTIONS["triage_rules"]["respond"],
        examples=formatted_examples
    )
    user_prompt = triage_user_prompt.format(
        author=author, to=to, subject=subject, email_thread=email_thread
    )
    
    # Classify email
    result = llm_router.invoke([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    
    # Store and update history
    state["history"] = state.get("history", []) + [{"email": state["email_input"], "label": result.classification}]
    
    # Get user feedback (simulated here, replace with input in practice)
    feedback = input(f"Classified as {result.classification}. Correct? (enter correct label or press Enter if correct): ").strip() or result.classification
    update_rules_and_store(feedback, state["email_input"], result.classification, namespace)
    
    # Handle classification
    if result.classification == "respond":
        print("📧 Classification: RESPOND - This email requires a response")
        return {"goto": "response_agent", "update": {"messages": [{"role": "user", "content": f"Respond to the email {state['email_input']}"}]}}
    elif result.classification == "ignore":
        print("🚫 Classification: IGNORE - This email can be safely ignored")
        return {"goto": END, "update": None}
    elif result.classification == "notify":
        print("🔔 Classification: NOTIFY - This email contains important information")
        return {"goto": END, "update": None}
    else:
        raise ValueError(f"Invalid classification: {result.classification}")

# Create response agent
response_agent = create_react_agent(model=llm, tools=tools, prompt=create_prompt, store=store)

# Define and compile state graph
email_agent = StateGraph(State)
email_agent.add_node("triage_router", triage_router)
email_agent.add_node("response_agent", response_agent)
email_agent.add_edge(START, "triage_router")
email_agent = email_agent.compile(store=store)

# Main execution
if __name__ == "__main__":
    config = {"configurable": {"langgraph_user_id": "lance"}}

    # Change the index to test different email inputs
    email_input = get_email_input(0)

    response = email_agent.invoke({"email_input": email_input, "messages": []}, config=config)
    for message in response["messages"]:
        message.pretty_print()