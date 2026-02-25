import os
import datetime
import concurrent.futures
import re
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(model="llama-3.3-70b-versatile", base_url="https://api.groq.com/openai/v1", api_key=os.environ.get("OPENAI_API_KEY", "NA"))

def save_blog(keyword, content):
    folder = "Deliverables/SEO_Blogs"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c for c in keyword if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:20]
    filename = f"{folder}/Blog_{safe_name}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def generate_single_blog(keyword):
    cloud_llm = get_llm()
    
    # 🔥 9/10 QUALITY PROMPT UPGRADE
    writer_agent = Agent(
        role='10x Technical SEO Writer',
        goal=f'Write a 1500+ word article on "{keyword}" that bypasses AI detectors and ranks #1 on Google.',
        backstory='You are an elite SEO writer. You never use words like "Delve into", "Tapestry", or "In conclusion". You write with high burstiness and perplexity. You use short paragraphs, bold text for scanning, and actionable lists.',
        allow_delegation=False,
        llm=cloud_llm
    )

    task = Task(
        description=f"Write a comprehensive, human-sounding SEO blog post for the keyword: '{keyword}'. \nConstraints: NO AI fluff words. Use Markdown H2 and H3 headers. Include a 'Key Takeaways' bulleted list at the start. End with a strong CTA, not a generic conclusion.",
        agent=writer_agent,
        expected_output="A 1500+ word highly optimized Markdown blog post."
    )

    crew = Crew(agents=[writer_agent], tasks=[task], verbose=True)
    return save_blog(keyword, str(crew.kickoff()))

def run_mass_seo_campaign(keywords_input):
    print(f"\n🌐 MASS SEO EMPIRE ACTIVATED FOR: {keywords_input}\n")
    clean_input = re.sub(r'(?i)^(write\s*(seo)?\s*blogs?\s*on:?\s*)', '', keywords_input)
    raw_keywords = re.split(r',|\band\b', clean_input, flags=re.IGNORECASE)
    keywords = [k.strip() for k in raw_keywords if k.strip()]
        
    saved_files = []
    error_logs = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_keyword = {executor.submit(generate_single_blog, kw): kw for kw in keywords}
        for future in concurrent.futures.as_completed(future_to_keyword):
            kw = future_to_keyword[future]
            try:
                filepath = future.result()
                saved_files.append(filepath)
            except Exception as exc:
                error_logs.append(f"'{kw}': {exc}")

    report = f"🌐 **MASS SEO CAMPAIGN COMPLETE**\n\n✅ {len(saved_files)} Human-like Blogs generated.\n"
    if error_logs: report += "\n⚠️ **Errors:**\n" + "\n".join(error_logs)
    return report