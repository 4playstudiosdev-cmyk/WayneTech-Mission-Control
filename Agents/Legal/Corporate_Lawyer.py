import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# --- Local AI Setup ---
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"
llm = ChatOpenAI(model="llama3-70b-8192")

def save_legal_report(topic, content):
    folder = "Deliverables/Legal_Reports"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Contract_Audit_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def run_legal_crew(contract_text_or_query):
    print(f"\n⚖️ DAREDEVIL (LEGAL TEAM) ACTIVATED...\n")

    risk_assessor = Agent(
        role='Senior Corporate Lawyer',
        goal='Identify loopholes, risks, and unfair terms in the given text.',
        backstory='Aap ek ruthless corporate lawyer hain jo choti se choti galti pakar lete hain.',
        allow_delegation=False,
        llm=llm
    )

    summarizer = Agent(
        role='Legal Translator',
        goal='Translate complex legal jargon into simple bullet points for the CEO.',
        backstory='Aap mushkil kanooni zaban ko aam insaan ki zaban mein samjhane ke expert hain.',
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f"Analyze this legal query/contract: '{contract_text_or_query}'. Find top 3 legal risks.",
        agent=risk_assessor,
        expected_output="A list of 3 severe legal risks."
    )

    task2 = Task(
        description="Take the risks found and create a simple 'CEO Action Plan' on how to fix these terms.",
        agent=summarizer,
        expected_output="Simple CEO summary and action plan."
    )

    crew = Crew(agents=[risk_assessor, summarizer], tasks=[task1, task2], verbose=True)
    result = crew.kickoff()
    
    return f"⚖️ **LEGAL AUDIT COMPLETE**\n\n📂 **Report Saved:** {save_legal_report('Legal_Task', str(result))}"