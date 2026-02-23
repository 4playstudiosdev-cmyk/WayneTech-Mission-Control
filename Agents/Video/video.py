import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# --- Setup Local AI ---
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"

llm = ChatOpenAI(model="llama-3.3-70b-versatile")
def save_script(task_name, content):
    folder = "Deliverables/Video"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Script_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def run_video_crew(task_description):
    print(f"\n🎥 STARTING VIDEO CREW: {task_description}\n")

    director = Agent(
        role='Creative Director',
        goal='Visualise viral video concepts',
        backstory='You know what stops the scroll on Instagram/YouTube.',
        allow_delegation=False,
        llm=llm
    )
    
    scriptwriter = Agent(
        role='Screenwriter',
        goal='Write scripts with timestamps and visual cues',
        backstory='You write engaging scripts.',
        allow_delegation=False,
        llm=llm
    )

    concept_task = Task(
        description=f"Create a video concept for: '{task_description}'",
        agent=director,
        expected_output="Concept summary and tone."
    )

    script_task = Task(
        description="Write the full script with Scene Numbers, Visuals, and Audio.",
        agent=scriptwriter,
        expected_output="A formatted video script."
    )

    crew = Crew(agents=[director, scriptwriter], tasks=[concept_task, script_task], verbose=True)
    result = crew.kickoff()
    
    saved_path = save_script(task_description, str(result))
    return f"🎥 VIDEO SQUAD REPORT:\nScript ready for production.\n📂 Saved at: {saved_path}"