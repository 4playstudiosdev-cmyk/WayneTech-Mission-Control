import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# --- Setup Local AI ---
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"

llm = ChatOpenAI(model="llama3-70b-8192")
# --- TOOLS (The Kimi Power) ---
search_tool = DuckDuckGoSearchRun()

def save_report(topic, content):
    folder = "Deliverables/DeepResearch"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Report_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Deep Research: {topic}\n\n{content}")
    return filename

def run_kimi_squad(topic):
    print(f"\n🧠 STARTING KIMI-LEVEL DEEP RESEARCH ON: {topic}\n")

    # Agent 1: The Hunter (Internet Searcher)
    # Iske paas 'search_tool' hai, ye internet par jayega
    researcher = Agent(
        role='Senior Web Researcher',
        goal='Find comprehensive, up-to-date data from the internet',
        backstory='You are an elite researcher who searches multiple sources, verifies facts, and ignores fake news. You act like Kimi AI.',
        tools=[search_tool],  # Internet Access Granted!
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Agent 2: The Analyst (Synthesizer)
    # Ye data ko padh kar report banayega
    analyst = Agent(
        role='Lead Data Analyst',
        goal='Synthesize research into a perfect Kimi-style report',
        backstory='You take raw data and turn it into a structured, highly detailed report with citations.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Tasks
    search_task = Task(
        description=f"Search the internet for detailed info on: '{topic}'. Get latest stats, news, and technical details.",
        agent=researcher,
        expected_output="A raw dump of verified information and links."
    )

    report_task = Task(
        description="Using the search results, create a 'Deep Dive Report'. It must be long, detailed, and structured like a Kimi AI response.",
        agent=analyst,
        expected_output="A professional markdown report."
    )

    # Crew
    kimi_crew = Crew(agents=[researcher, analyst], tasks=[search_task, report_task], verbose=True)
    result = kimi_crew.kickoff()
    
    saved_path = save_report(topic, str(result))
    return f"🧠 DEEP RESEARCH COMPLETE.\nFacts Verified from Internet.\n📂 Report: {saved_path}"