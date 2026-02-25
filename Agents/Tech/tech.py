import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama-3.3-70b-versatile")

def save_code(task_name, code_content):
    folder = "Deliverables/Tech"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Code_{timestamp}.py"
    with open(filename, "w", encoding="utf-8") as f: f.write(code_content)
    return filename

def run_tech_crew(task_description):
    print(f"\n💻 STARTING TECH CREW: {task_description}\n")

    # 🔥 9/10 QUALITY PROMPT UPGRADE
    developer = Agent(
        role='Principal Staff Software Engineer',
        goal='Write production-ready, 100% complete executable code without any omissions.',
        backstory='You are an elite developer. YOU NEVER USE PLACEHOLDERS like `// do something` or `# add logic here`. You write complete, bug-free, PEP8 compliant code with inline comments explaining the logic.',
        allow_delegation=False,
        llm=llm
    )

    code_task = Task(
        description=f"Write the FULL executable code for: '{task_description}'. \nCRITICAL RULES: \n1. Do NOT omit any code. \n2. Provide ALL imports. \n3. Ensure it runs immediately upon copying. \n4. Output only the code wrapped in markdown blocks.",
        agent=developer,
        expected_output="Complete, ready-to-run raw code."
    )

    crew = Crew(agents=[developer], tasks=[code_task], verbose=True)
    try:
        result = crew.kickoff()
        saved_path = save_code('Script', str(result))
        return f"💻 **TECH SQUAD REPORT:**\n\n✅ Production-grade code generated successfully.\n📂 **Saved at:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Tech Crew Error:** {str(e)}"