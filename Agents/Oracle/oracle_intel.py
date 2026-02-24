import os
import datetime
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import tool

llm = ChatOpenAI(model="llama-3.3-70b-versatile")

# 🐛 FIXED: Custom Bulletproof Scraper Tool (No Embeddings API required!)
@tool("Scrape Website Text")
def scrape_tool(url: str) -> str:
    """Useful to scrape and read the text content of a website URL. Use this to read competitor websites."""
    try:
        # Browser jaisa pretend karne ke liye headers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Website se kachra (scripts/styles) nikal kar sirf text lena
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator='\n', strip=True)
        return text[:15000] # LLM ki memory full na ho isliye first 15k characters
    except Exception as e:
        return f"Failed to scrape website. Error: {str(e)}"

def save_intel(task_name, content):
    folder = "Deliverables/Oracle_Intel"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c for c in task_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:20]
    filename = f"{folder}/Competitor_Report_{safe_name}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def run_oracle_crew(target_url_or_desc):
    print(f"\n🔮 ITACHI (ORACLE) ACTIVATED FOR: {target_url_or_desc}\n")

    # --- AGENT 1: The Scraper (Data Gatherer) ---
    scraper_agent = Agent(
        role='Chief Web Scraper & Data Extractor',
        goal='Extract all meaningful text, pricing, and services from the given website URL.',
        backstory='You are a master hacker and data gatherer. You can read a website and instantly know what they are selling.',
        tools=[scrape_tool],
        allow_delegation=False,
        llm=llm
    )

    # --- AGENT 2: The Analyst (Competitor Profiler) ---
    analyst_agent = Agent(
        role='Competitor Profiler & Business Analyst',
        goal='Analyze the scraped data to find their target audience, pricing strategy, and weaknesses.',
        backstory='You have an MBA from Harvard. You look at a business model and instantly find its flaws.',
        allow_delegation=False,
        llm=llm
    )

    # --- AGENT 3: The Strategist (Action Plan Creator) ---
    strategist_agent = Agent(
        role='Master Business Strategist',
        goal='Create a step-by-step plan on how OUR agency can beat this competitor.',
        backstory='You are a war general for businesses. You give actionable advice on how to dominate the market.',
        allow_delegation=False,
        llm=llm
    )

    # --- TASKS ---
    task1 = Task(
        description=f"Go to the web and gather all information regarding: '{target_url_or_desc}'. YOU MUST USE the 'Scrape Website Text' tool to read the URL provided.",
        agent=scraper_agent,
        expected_output="Raw scraped text containing business details, features, and pricing."
    )

    task2 = Task(
        description="Take the raw scraped data. Identify: 1) What is their main product? 2) Who is their target audience? 3) What is their pricing structure? 4) What are their weaknesses (what are they missing)?",
        agent=analyst_agent,
        expected_output="A structured Competitor Profile."
    )

    task3 = Task(
        description="Based on the Competitor Profile, write a 3-Step 'Attack Plan' for our company to offer a better service and steal their clients.",
        agent=strategist_agent,
        expected_output="A 3-Step Business Domination Plan."
    )

    # --- ASSEMBLE CREW ---
    crew = Crew(
        agents=[scraper_agent, analyst_agent, strategist_agent],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential 
    )

    try:
        result = crew.kickoff()
        saved_path = save_intel(target_url_or_desc, str(result))
        return f"🔮 **ORACLE INTELLIGENCE GATHERED**\n\n✅ Competitor analyzed and Attack Plan created.\n📂 **Report Saved:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Oracle Error:** {str(e)}"