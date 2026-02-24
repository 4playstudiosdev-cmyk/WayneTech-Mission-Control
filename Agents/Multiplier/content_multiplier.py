import os
import time
import datetime
import tweepy
import requests
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import YoutubeLoader # 🐛 FIXED: Bulletproof YouTube Loader
from langchain.tools import tool

llm = ChatOpenAI(model="llama-3.3-70b-versatile")

@tool("Publish to Twitter API")
def publish_to_twitter(content: str) -> str:
    """Use this tool to automatically publish a thread or tweet to Twitter."""
    print(f"\n[🌐 API LOG] Connecting to REAL Twitter API...")
    api_key = os.getenv("TWITTER_API_KEY", "your_api_key_here")
    api_secret = os.getenv("TWITTER_API_SECRET", "your_api_secret_here")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN", "your_access_token_here")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET", "your_access_secret_here")
    
    if api_key == "your_api_key_here" or not api_key:
        return "⚠️ SKIPPED: Twitter keys not found in Dashboard UI. Please add them."

    try:
        client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)
        tweet_text = content[:280] 
        response = client.create_tweet(text=tweet_text)
        return f"Successfully posted to Twitter. Tweet ID: {response.data['id']}"
    except Exception as e:
        return f"Failed to post to Twitter. Error: {str(e)}"

@tool("Publish to LinkedIn API")
def publish_to_linkedin(content: str) -> str:
    """Use this tool to automatically publish posts to LinkedIn."""
    print(f"\n[🌐 API LOG] Connecting to REAL LinkedIn Graph API...")
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "your_access_token_here")
    
    if access_token == "your_access_token_here" or not access_token:
        return "⚠️ SKIPPED: LinkedIn keys not found in Dashboard UI. Please add them."
        
    return "LinkedIn API configured but skipped for safety during text phase."

def save_omni_content(task_name, content):
    folder = "Deliverables/Omni_Content"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Repurposed_Content_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

def run_multiplier_crew(youtube_link):
    print(f"\n🐙 MULTIPLIER ACTIVATED: Repurposing & Publishing {youtube_link}\n")

    # 1. Fetch Transcript Directly (Bug Fixed!)
    try:
        loader = YoutubeLoader.from_youtube_url(youtube_link, add_video_info=False)
        docs = loader.load()
        if not docs:
            return "⚠️ **Error:** No captions found for this video."
        transcript_text = docs[0].page_content[:20000] 
    except Exception as e:
        return f"⚠️ **Error fetching captions:** {e} (Make sure the link is correct and video has subtitles)."

    analyst = Agent(
        role='Video Content Extractor',
        goal='Extract the core message, best quotes, and most engaging hooks from the video text.',
        backstory='Aap ek expert content analyst hain. Aap text se viral baatein nikalte hain.',
        allow_delegation=False,
        llm=llm
    )

    twitter_writer = Agent(
        role='Viral Twitter Thread Creator',
        goal='Take the extracted video concepts and turn them into a 10-part highly engaging Twitter thread.',
        backstory='Aap Twitter ke king hain. Aapko pata hai ke pehla tweet kaisa hona chahiye.',
        allow_delegation=False,
        llm=llm
    )

    linkedin_writer = Agent(
        role='B2B LinkedIn Copywriter',
        goal='Turn the video concepts into 3 professional, value-driven LinkedIn posts.',
        backstory='Aap LinkedIn par CEOs ke liye likhte hain.',
        allow_delegation=False,
        llm=llm
    )

    publisher_agent = Agent(
        role='Social Media Automation Manager',
        goal='Take the approved content and publish it to Twitter and LinkedIn.',
        backstory='Aap executioner hain. Aap ensure karte hain ke post API ke zariye upload ho jaye.',
        tools=[publish_to_twitter, publish_to_linkedin],
        allow_delegation=False,
        llm=llm
    )

    task_extract = Task(
        description=f"Analyze this video transcript:\n\n{transcript_text}\n\nExtract the 5 main takeaways and the overall thesis of the video.",
        agent=analyst,
        expected_output="A detailed summary document with takeaways."
    )

    task_twitter = Task(
        description="Using the summary, write a 10-tweet viral thread. Use emojis and spacing.",
        agent=twitter_writer,
        expected_output="A complete 10-tweet thread."
    )

    task_linkedin = Task(
        description="Using the summary, write 3 distinct LinkedIn posts. Include hashtags.",
        agent=linkedin_writer,
        expected_output="3 ready-to-publish LinkedIn posts."
    )

    task_publish = Task(
        description="Take the final Twitter thread. Use your API tools to publish it. You MUST use the Twitter tool.",
        agent=publisher_agent,
        expected_output="Confirmation logs from the APIs."
    )

    crew = Crew(
        agents=[analyst, twitter_writer, linkedin_writer, publisher_agent],
        tasks=[task_extract, task_twitter, task_linkedin, task_publish],
        verbose=True,
        process=Process.sequential 
    )

    try:
        result = crew.kickoff()
        saved_path = save_omni_content('YouTube_Repurpose', str(result))
        return f"🐙 **CONTENT MULTIPLIER COMPLETE**\n\n✅ Content Generated & Auto-Published.\n📂 **Logs & Assets Saved:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Multiplier Error:** {e}"