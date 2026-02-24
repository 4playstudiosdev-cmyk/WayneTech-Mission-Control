import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# ☁️ CLOUD READY
llm = ChatOpenAI(model="llama-3.3-70b-versatile")

def save_code(task_name, code_content):
    folder = "Deliverables/Tech"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Code_{timestamp}.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Task: {task_name}\n\n{code_content}")
    return filename

def run_tech_crew(task_description):
    print(f"\n💻 STARTING TECH CREW: {task_description}\n")

    developer = Agent(
        role='Lead Python & Web Developer',
        goal='Write clean, bug-free, and modular code.',
        backstory='You build functional prototypes in minutes. You are an expert in Python, React, and HTML/CSS.',
        allow_delegation=False,
        llm=llm
    )

    code_task = Task(
        description=f"Write the COMPLETE executable code for: '{task_description}'. Do not use placeholders. Provide the raw code blocks.",
        agent=developer,
        expected_output="Fully functional code block (Python or HTML/JS)."
    )

    crew = Crew(agents=[developer], tasks=[code_task], verbose=True)
    try:
        result = crew.kickoff()
        saved_path = save_code(task_description, str(result))
        return f"💻 **TECH SQUAD REPORT:**\n\n✅ Code generated successfully.\n📂 **Saved at:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Tech Crew Error:** {str(e)}"