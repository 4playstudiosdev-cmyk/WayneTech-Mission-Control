import os
import datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from crewai_tools import YoutubeVideoSearchTool

os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"
llm = ChatOpenAI(model="llama3-70b-8192")
# This tool can read YouTube Transcripts automatically!
yt_tool = YoutubeVideoSearchTool()

def save_yt_report(topic, content):
    folder = "Deliverables/Omni_Reader"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/YouTube_Summary_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def run_omnireader_crew(youtube_link_or_query):
    print(f"\n🧠 BRAINIAC (OMNI-READER) ACTIVATED FOR: {youtube_link_or_query}\n")

    yt_summarizer = Agent(
        role='Knowledge Extraction Specialist',
        goal='Extract actionable steps and key knowledge from YouTube videos.',
        backstory='Aap ek aisi AI hain jo 2 ghante ki video 2 minute mein parh kar uski summary bana sakti hai.',
        tools=[yt_tool],
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=f"Access this topic or YouTube link: '{youtube_link_or_query}'. Extract the top 5 most valuable lessons or steps mentioned in it.",
        agent=yt_summarizer,
        expected_output="Top 5 lessons extracted from the video."
    )

    crew = Crew(agents=[yt_summarizer], tasks=[task], verbose=True)
    try:
        result = crew.kickoff()
    except Exception as e:
        result = f"Error extracting video (It might not have captions): {e}"
        
    return f"🧠 **KNOWLEDGE EXTRACTION COMPLETE**\n\n📂 **Notes Saved:** {save_yt_report('YT', str(result))}"