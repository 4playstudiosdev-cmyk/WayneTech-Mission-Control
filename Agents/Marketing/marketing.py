import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama-3.3-70b-versatile")

def save_to_file(task_name, content):
    folder = "Deliverables/Marketing_OpenClaw"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c for c in task_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:20]
    filename = f"{folder}/Campaign_{safe_name}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def run_marketing_crew(campaign_topic):
    print(f"\n🦸‍♂️ OPENCLAW MARKETING TEAM ACTIVATED: {campaign_topic}\n")

    # 🔥 9/10 QUALITY PROMPT UPGRADE
    head_of_marketing = Agent(
        role='Chief Marketing Officer (Direct Response)',
        goal='Develop a ruthless direct response campaign strategy using the AIDA (Attention, Interest, Desire, Action) framework.',
        backstory='You have managed $500M in ad spend. You don\'t care about "branding", you only care about ROI and conversions. You know exact human psychological triggers.',
        allow_delegation=False,
        llm=llm
    )

    creative_director = Agent(
        role='Elite Meta Ads Copywriter',
        goal='Write 3 distinct Ad Angles with Primary Text, Headlines, and visual briefs that guarantee a 3%+ CTR.',
        backstory='You write ad copy that stops people from scrolling instantly. You use short, punchy sentences. You know how to overcome objections in the copy.',
        allow_delegation=False,
        llm=llm
    )

    task_strategy = Task(
        description=f"Create a Direct Response Strategy for: '{campaign_topic}'. Identify the Core Desire, the Core Fear, and the Big Promise for the target audience.",
        agent=head_of_marketing,
        expected_output="A robust psychological marketing strategy document."
    )

    task_creation = Task(
        description="Using the strategy, write exactly 3 Meta Ad variations. Angle 1: Logical/Features. Angle 2: Emotional/Story. Angle 3: Fear of Missing Out (Urgency). Provide the Headline, Primary Text, and Image/Video prompt for each.",
        agent=creative_director,
        expected_output="3 Complete Ad Copy Variations."
    )

    marketing_crew = Crew(agents=[head_of_marketing, creative_director], tasks=[task_strategy, task_creation], verbose=True, process=Process.sequential)
    
    try:
        result = marketing_crew.kickoff()
        saved_path = save_to_file(campaign_topic, str(result))
        return f"🚀 **META ADS CAMPAIGN READY**\n\n✅ 3 High-Converting Angles Generated.\n📂 **Saved at:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Marketing Crew Error:** {str(e)}"