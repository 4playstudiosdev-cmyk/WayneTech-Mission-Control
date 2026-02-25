import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from duckduckgo_search import DDGS

# ☁️ CLOUD READY
llm = ChatOpenAI(model="llama-3.3-70b-versatile")

# 🔥 BUG FIX: Using Native DDGS Library for Bulletproof Search
@tool("Bulletproof Web Search")
def robust_search_tool(query: str) -> str:
    """Useful to search the internet for current events, facts, and research."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results: return "No results found."
            return "\n\n".join([f"Title: {r['title']}\nBody: {r['body']}\nURL: {r['href']}" for r in results])
    except Exception as e:
        return f"Search API failed: {str(e)}"

def save_report(topic, content):
    folder = "Deliverables/DeepResearch"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Research_Report_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def run_kimi_squad(topic):
    print(f"\n🧠 STARTING MANHUNTER RESEARCH: {topic}\n")

    # 🔥 9/10 QUALITY PROMPT UPGRADE
    researcher = Agent(
        role='Chief Intelligence Officer (CIA Level)',
        goal='Find highly verified, hidden insights from the internet avoiding generic surface-level advice.',
        backstory='You are L Lawliet. You dig deeper than anyone else. You triangulate data from multiple sources to ensure 100% factual accuracy. You never hallucinates.',
        tools=[robust_search_tool],
        allow_delegation=False,
        llm=llm
    )

    analyst = Agent(
        role='Master Synthesizer',
        goal='Structure the raw intelligence into a highly actionable executive brief.',
        backstory='You take messy research data and turn it into a consulting-grade executive report. You use frameworks like SWOT and PESTLE when applicable.',
        allow_delegation=False,
        llm=llm
    )

    search_task = Task(
        description=f"Conduct a deep internet search on: '{topic}'. Do not stop until you have hard numbers, current dates, and specific facts.",
        agent=researcher,
        expected_output="A massive raw data dump of verified facts, numbers, and sources."
    )

    synthesis_task = Task(
        description="Take the raw data dump and write a completely formatted Markdown Executive Report. Include an 'Executive Summary', 'Key Findings', and 'Actionable Recommendations'.",
        agent=analyst,
        expected_output="A beautifully formatted Markdown report."
    )

    kimi_crew = Crew(agents=[researcher, analyst], tasks=[search_task, synthesis_task], verbose=True)
    try:
        result = kimi_crew.kickoff()
        saved_path = save_report(topic, str(result))
        return f"🧠 **DEEP RESEARCH COMPLETE**\n\n✅ CIA-Level Intel Gathered.\n📂 **Report Saved:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Research Error:** {str(e)}"