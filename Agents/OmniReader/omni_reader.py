import os
import datetime
import re # <-- Yeh line add karein
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import YoutubeLoader 

llm = ChatOpenAI(model="llama-3.3-70b-versatile")

def save_yt_report(topic, content):
    folder = "Deliverables/Omni_Reader"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/YouTube_Summary_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def run_omnireader_crew(youtube_link_or_query):
    print(f"\n🧠 BRAINIAC (OMNI-READER) ACTIVATED FOR: {youtube_link_or_query}\n")

    # 🐛 FIX: Regex se sirf link nikalo
    match = re.search(r'(https?://[^\s]+)', youtube_link_or_query)
    if match:
        clean_url = match.group(0)
    else:
        return "⚠️ **Error:** Aapke message mein koi valid YouTube link nahi mila."

    # 1. Fetch Transcript Directly (Bug Fixed!)
    try:
        loader = YoutubeLoader.from_youtube_url(clean_url, add_video_info=False)
        docs = loader.load()
        if not docs:
            return "⚠️ **Error:** No captions found for this video."
        transcript_text = docs[0].page_content[:20000] 
    except Exception as e:
        return f"⚠️ **Error fetching captions:** {e} (Make sure the link is correct and video has subtitles)."

    # --- Baaki saara purana code wese hi rahega ---
    yt_summarizer = Agent(
        role='Knowledge Extraction Specialist',
        goal='Extract actionable steps and key knowledge from the provided video transcript.',
        backstory='Aap ek aisi AI hain jo 2 ghante ki video ka text 2 second mein parh kar uski summary bana sakti hai.',
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=f"Here is the transcript of the video:\n\n{transcript_text}\n\nExtract the top 5 most valuable lessons, key takeaways, or actionable steps mentioned in it. Make it structured and easy to read.",
        agent=yt_summarizer,
        expected_output="Top 5 lessons extracted from the video formatted cleanly."
    )

    crew = Crew(agents=[yt_summarizer], tasks=[task], verbose=True)
    try:
        result = crew.kickoff()
        saved_path = save_yt_report('YT', str(result))
        return f"🧠 **KNOWLEDGE EXTRACTION COMPLETE**\n\n✅ Video summarized successfully.\n📂 **Notes Saved:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Processing Error:** {e}"
