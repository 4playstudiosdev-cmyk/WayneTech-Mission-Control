import os
import datetime
import concurrent.futures
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# --- Local AI Setup ---
llm = ChatOpenAI(model="llama-3.3-70b-versatile")

def save_blog(keyword, content):
    folder = "Deliverables/SEO_Blogs"
    if not os.path.exists(folder): os.makedirs(folder)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c for c in keyword if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:20]
    filename = f"{folder}/Blog_{safe_name}_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def generate_single_blog(keyword):
    print(f"🚀 Started generation for: {keyword}")
    
    seo_agent = Agent(
        role='Chief SEO Strategist',
        goal=f'Find the best LSI keywords, search intent, and H1/H2 structure for: {keyword}',
        backstory='Aap ek master SEO expert hain jo Google algorithm ko beat karna jante hain.',
        allow_delegation=False,
        llm=llm
    )

    writer_agent = Agent(
        role='Long-form Content Writer',
        goal='Write a highly engaging, human-like 2000-word article based on the SEO outline.',
        backstory='Aap ek top-tier copywriter hain. Aapki writing boring nahi hoti, balki reader ko hook karti hai.',
        allow_delegation=False,
        llm=llm
    )

    editor_agent = Agent(
        role='Senior Editor & Proofreader',
        goal='Format the article with Markdown, add Meta Description, and ensure 0% fluff.',
        backstory='Aap details par focus karte hain. Aap ensure karte hain ke article publish-ready ho.',
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f"Analyze the keyword '{keyword}'. Create a detailed outline with H1, H2, H3 tags and a list of 10 LSI keywords to include.",
        agent=seo_agent,
        expected_output="Detailed SEO Outline and Keyword List."
    )

    task2 = Task(
        description="Using the outline, write a massive, comprehensive blog post. Write engaging intros and actionable body paragraphs.",
        agent=writer_agent,
        expected_output="Full length blog post draft."
    )

    task3 = Task(
        description="Review the draft. Format it beautifully in Markdown. Add a catchy Meta Title and a 160-character Meta Description at the top.",
        agent=editor_agent,
        expected_output="Final, polished, publish-ready Markdown file."
    )

    crew = Crew(
        agents=[seo_agent, writer_agent, editor_agent],
        tasks=[task1, task2, task3],
        verbose=True, 
        process=Process.sequential 
    )

    result = crew.kickoff()
    saved_path = save_blog(keyword, str(result))
    return saved_path

def run_mass_seo_campaign(keywords_input):
    print(f"\n🌐 MASS SEO EMPIRE ACTIVATED FOR: {keywords_input}\n")
    
    keywords = [k.strip() for k in keywords_input.split(',')]
    if len(keywords) == 1 and (" AND " in keywords_input.upper()):
        keywords = [k.strip() for k in keywords_input.upper().split(' AND ')]
        
    saved_files = []
    error_logs = []
    
    # 🐛 FIXED: Changed max_workers from 5 to 1 to prevent Groq API Rate Limit crashes
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_keyword = {executor.submit(generate_single_blog, kw): kw for kw in keywords}
        for future in concurrent.futures.as_completed(future_to_keyword):
            kw = future_to_keyword[future]
            try:
                filepath = future.result()
                saved_files.append(filepath)
                print(f"✅ Success: Blog generated for '{kw}'")
            except Exception as exc:
                error_msg = f"'{kw}': {exc}"
                error_logs.append(error_msg)
                print(f"❌ Error generating blog for {error_msg}")

    report = f"🌐 **MASS SEO CAMPAIGN COMPLETE**\n\n✅ {len(saved_files)} Blogs generated.\n"
    
    # Show exactly why it failed in the UI if there's an error
    if error_logs:
        report += "\n⚠️ **API Limits Hit for:**\n" + "\n".join(error_logs) + "\n*(Tip: Try generating one blog at a time)*"
    else:
        report += "📂 **Files Saved in:** Deliverables/SEO_Blogs/"
        
    return report