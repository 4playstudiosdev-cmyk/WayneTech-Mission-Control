import os
import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# ☁️ CLOUD READY
llm = ChatOpenAI(model="llama-3.3-70b-versatile")

def save_leads(task_name, content):
    folder = "Deliverables/Sales_Leads"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Lead_Gen_Report_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def run_sales_crew(product_or_niche):
    print(f"\n💰 SALES DEPARTMENT ACTIVATED FOR NICHE: {product_or_niche}\n")

    reddit_discord_scout = Agent(
        role='Community Lead Hunter (Reddit/Discord)',
        goal='Identify users asking questions or having problems related to the product.',
        backstory='You monitor subreddits and Discord servers. You find people who are desperate for a solution.',
        allow_delegation=False,
        llm=llm
    )

    twitter_scout = Agent(
        role='Twitter (X) Signal Finder',
        goal='Find tweets where people are complaining about competitors or asking for recommendations.',
        backstory='You use advanced search operators to find high-intent buyers on X.',
        allow_delegation=False,
        llm=llm
    )
    
    meta_scout = Agent(
        role='Facebook/Insta Group Analyst',
        goal='Identify target audiences and relevant Facebook Groups for outreach.',
        backstory='You know exactly which Facebook groups contain wealthy, ready-to-buy customers.',
        allow_delegation=False,
        llm=llm
    )

    dm_specialist = Agent(
        role='Direct Message (DM) Copywriter',
        goal='Write highly personalized, non-spammy DMs that get a 50%+ reply rate.',
        backstory='You understand human psychology. You never sound like a bot. Your DMs feel like a message from a friend.',
        allow_delegation=False,
        llm=llm
    )

    email_closer = Agent(
        role='Cold Email Strategist (Gmail)',
        goal='Write irresistible cold email sequences with high open rates.',
        backstory='You write subject lines that get opened and copy that converts cold leads into booked calls.',
        allow_delegation=False,
        llm=llm
    )

    task_scout = Task(
        description=f"Analyze the niche: '{product_or_niche}'. Where do these customers hang out? Give specific examples of subreddits, Discord server types, Twitter keywords, and Facebook group names to target.",
        agent=reddit_discord_scout,
        expected_output="A list of specific platforms, groups, and keywords to scrape."
    )

    task_dm = Task(
        description="Based on the target audience identified, write 3 variations of an initial Outreach DM (for Insta/Twitter/Reddit). The DM MUST NOT sound salesy. It must ask a relevant question to start a conversation.",
        agent=dm_specialist,
        expected_output="3 highly personalized DM templates."
    )

    task_email = Task(
        description="Write a 3-step Cold Email sequence (Initial, Follow-up 1, Follow-up 2) for these leads. Include subject lines.",
        agent=email_closer,
        expected_output="3-step cold email sequence."
    )

    crew = Crew(
        agents=[reddit_discord_scout, twitter_scout, meta_scout, dm_specialist, email_closer],
        tasks=[task_scout, task_dm, task_email],
        verbose=True,
        process=Process.sequential 
    )

    try:
        result = crew.kickoff()
        saved_path = save_leads(product_or_niche, str(result))
        return f"💰 **SALES OUTREACH PLAN READY**\n\n✅ Target Groups Identified & Custom DMs/Emails Written.\n📂 **Check Deliverables:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Sales Crew Error:** {str(e)}"