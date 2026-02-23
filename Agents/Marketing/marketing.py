import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# --- Setup Local AI ---
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"

llm = ChatOpenAI(model="llama-3.3-70b-versatile")
search_tool = DuckDuckGoSearchRun()

def save_to_file(task_name, content):
    folder = "Deliverables/Marketing_OpenClaw"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    safe_name = "".join([c for c in task_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:20]
    filename = f"{folder}/Campaign_{safe_name}_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# OpenClaw Meta Campaign: {task_name}\n\n{content}")
    return filename

def run_marketing_crew(campaign_topic):
    print(f"\n🦸‍♂️ OPENCLAW MARKETING TEAM ACTIVATED: {campaign_topic}\n")

    # --- 1. RESEARCH (Ads Analyst) ---
    ads_analyst = Agent(
        role='Ads & Competitor Analyst',
        goal='Study the full meta marketing strategy and ad creatives from competitors.',
        backstory='You are a master of market research. You extract data on what ads are working right now and analyze landing pages.',
        tools=[search_tool],
        allow_delegation=False,
        llm=llm
    )

    # --- 2. STRATEGY (Head of Marketing) ---
    head_of_marketing = Agent(
        role='Head of Marketing',
        goal='Create brand guidelines and plan the overarching campaign strategy.',
        backstory='You are the big-picture thinker. You take raw competitor data and build a unique angle and brand voice that converts.',
        allow_delegation=False,
        llm=llm
    )

    # --- 3. CREATION (Creative Director) ---
    creative_director = Agent(
        role='Creative Director',
        goal='Create the actual ad assets including ad copy, image/carousel ideas, and video scripts.',
        backstory='You are the artist and copywriter. You write hooks that grab attention and scripts that make people buy.',
        allow_delegation=False,
        llm=llm
    )

    # --- 4. EXECUTION (Performance Marketer) ---
    performance_marketer = Agent(
        role='Performance Marketer',
        goal='Compile everything into a structured campaign ready to be deployed directly in Meta Ads Manager.',
        backstory='You handle the technical side of Ads. You define the budget, targeting, demographics, and campaign structure (CBO/ABO).',
        allow_delegation=False,
        llm=llm
    )

    # --- TASKS (Sequential Pipeline) ---
    task_research = Task(
        description=f"Research the market and competitors for: '{campaign_topic}'. Identify their current ad angles, target audiences, and landing page strategies.",
        agent=ads_analyst,
        expected_output="A comprehensive Competitor & Meta Ads Analysis document."
    )

    task_strategy = Task(
        description="Using the analyst's research, develop a unique Campaign Strategy. Define the 'Big Idea', the core offer, and the brand voice guidelines.",
        agent=head_of_marketing,
        expected_output="A strategic Campaign Plan and Brand Guidelines document."
    )

    task_creation = Task(
        description="Using the strategy, write the actual assets. Produce 3 Facebook/Instagram Ad Copies (Primary Text & Headline), 2 Image/Carousel visual descriptions, and 1 short-form Video Script (Reel/TikTok format).",
        agent=creative_director,
        expected_output="The final Creative Assets (Copy, Visual Ideas, Scripts)."
    )

    task_execution = Task(
        description="Take the creative assets and package them into a Meta Ads Manager execution plan. Specify the targeting interests, age groups, budget distribution, and campaign objective.",
        agent=performance_marketer,
        expected_output="A complete, ready-to-publish Meta Ads Campaign blueprint."
    )

    # Assemble the OpenClaw Pipeline
    marketing_crew = Crew(
        agents=[ads_analyst, head_of_marketing, creative_director, performance_marketer], 
        tasks=[task_research, task_strategy, task_creation, task_execution], 
        verbose=True,
        process=Process.sequential
    )
    
    result = marketing_crew.kickoff()
    
    saved_path = save_to_file(campaign_topic, str(result))
    return f"🚀 **OPENCLAW CAMPAIGN READY**\n\n✅ 4-Agent Pipeline executed. Campaign Assets generated.\n📂 **Saved at:** {saved_path}"