import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"
llm = ChatOpenAI(model="llama-3.3-70b-versatile")
search_tool = DuckDuckGoSearchRun()

def save_finance_report(topic, content):
    folder = "Deliverables/Finance_Reports"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/VC_Report_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def run_finance_crew(company_or_market):
    print(f"\n💰 LUCIUS (FINANCE TEAM) ACTIVATED FOR: {company_or_market}\n")

    vc_analyst = Agent(
        role='Wall Street VC Analyst',
        goal='Analyze the financial viability and market trends of a company/niche.',
        backstory='Aap numbers aur market trends dekh kar bata dete hain ke company doobegi ya uregi.',
        tools=[search_tool],
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=f"Search the web for financial news and market size regarding: '{company_or_market}'. Write a 'BUY, HOLD, or SELL' recommendation with 3 factual reasons.",
        agent=vc_analyst,
        expected_output="VC Due Diligence Report with BUY/SELL recommendation."
    )

    crew = Crew(agents=[vc_analyst], tasks=[task], verbose=True)
    result = crew.kickoff()
    
    return f"💰 **VC DUE DILIGENCE COMPLETE**\n\n📂 **Report Saved:** {save_finance_report('Finance', str(result))}"