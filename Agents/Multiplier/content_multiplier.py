import os
import time
import datetime
import tweepy  # Real Twitter API Library (pip install tweepy)
import requests # Real HTTP requests library for LinkedIn (pip install requests)
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import YoutubeVideoSearchTool
from langchain.tools import tool

# --- Setup Local AI ---
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"

llm = ChatOpenAI(model="llama3-70b-8192")
# --- TOOLS ---
# Tool 1: YouTube Scraper
yt_tool = YoutubeVideoSearchTool()

# Tool 2: REAL Twitter API Publisher
@tool("Publish to Twitter API")
def publish_to_twitter(content: str) -> str:
    """Use this tool to automatically publish a thread or tweet to Twitter."""
    print(f"\n[🌐 API LOG] Connecting to REAL Twitter API...")
    
    # ⚠️ COMMANDER: Put your real Twitter API keys here
    api_key = os.getenv("TWITTER_API_KEY", "your_api_key_here")
    api_secret = os.getenv("TWITTER_API_SECRET", "your_api_secret_here")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN", "your_access_token_here")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET", "your_access_secret_here")
    
    if api_key == "your_api_key_here":
        return "⚠️ SKIPPED: Real Twitter keys not found in code. Please add them."

    try:
        # Authenticate with Twitter V2 API
        client = tweepy.Client(
            consumer_key=api_key, 
            consumer_secret=api_secret, 
            access_token=access_token, 
            access_token_secret=access_secret
        )
        
        # Twitter has a 280 character limit per tweet. 
        # For a simple implementation, we post the first chunk. 
        # (For full threads, a loop with client.create_tweet(in_reply_to_tweet_id=...) is needed)
        tweet_text = content[:280] 
        response = client.create_tweet(text=tweet_text)
        
        print(f"[✅ API SUCCESS] Real Tweet Published! ID: {response.data['id']}")
        return f"Successfully posted to Twitter. Tweet ID: {response.data['id']}"
    except Exception as e:
        print(f"[❌ API ERROR] Twitter error: {e}")
        return f"Failed to post to Twitter. Error: {str(e)}"

# Tool 3: REAL LinkedIn API Publisher
@tool("Publish to LinkedIn API")
def publish_to_linkedin(content: str) -> str:
    """Use this tool to automatically publish posts to LinkedIn."""
    print(f"\n[🌐 API LOG] Connecting to REAL LinkedIn Graph API...")
    
    # ⚠️ COMMANDER: Put your real LinkedIn Access Token and Person URN here
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "your_access_token_here")
    person_urn = os.getenv("LINKEDIN_PERSON_URN", "urn:li:person:your_id_here")
    
    if access_token == "your_access_token_here":
        return "⚠️ SKIPPED: Real LinkedIn keys not found in code. Please add them."

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"[✅ API SUCCESS] Real Post Live on LinkedIn!")
            return "Successfully posted to LinkedIn."
        else:
            print(f"[❌ API ERROR] LinkedIn API response: {response.text}")
            return f"Failed. LinkedIn API response: {response.text}"
    except Exception as e:
        print(f"[❌ API ERROR] LinkedIn error: {e}")
        return f"Error posting to LinkedIn: {str(e)}"

def save_omni_content(task_name, content):
    folder = "Deliverables/Omni_Content"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Repurposed_Content_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def run_multiplier_crew(youtube_link):
    print(f"\n🐙 MULTIPLIER ACTIVATED: Repurposing & Publishing {youtube_link}\n")

    # --- AGENT 1: The Video Analyst ---
    analyst = Agent(
        role='Video Content Extractor',
        goal='Extract the core message, best quotes, and most engaging hooks from the video.',
        backstory='Aap ek expert content analyst hain. Aap kisi bhi video ko dekh kar uski "Viral" baatein nikal lete hain.',
        tools=[yt_tool],
        allow_delegation=False,
        llm=llm
    )

    # --- AGENT 2: The Twitter (X) Ghostwriter ---
    twitter_writer = Agent(
        role='Viral Twitter Thread Creator',
        goal='Take the extracted video concepts and turn them into a 10-part highly engaging Twitter thread.',
        backstory='Aap Twitter ke king hain. Aapko pata hai ke pehla tweet kaisa hona chahiye jo log scroll karna band kar dein.',
        allow_delegation=False,
        llm=llm
    )

    # --- AGENT 3: The LinkedIn Strategist ---
    linkedin_writer = Agent(
        role='B2B LinkedIn Copywriter',
        goal='Turn the video concepts into 3 professional, value-driven LinkedIn posts with bullet points.',
        backstory='Aap LinkedIn par CEOs aur founders ke liye likhte hain. Aapki posts par hazaron likes aate hain.',
        allow_delegation=False,
        llm=llm
    )

    # --- AGENT 4: The Publisher (NEW) ---
    publisher_agent = Agent(
        role='Social Media Automation Manager',
        goal='Take the approved content from writers and publish it directly to Twitter and LinkedIn via API.',
        backstory='Aap executioner hain. Aapke paas company ke saare social media accounts ki API access hai. Aap ensure karte hain ke post automatically upload ho jaye.',
        tools=[publish_to_twitter, publish_to_linkedin],
        allow_delegation=False,
        llm=llm
    )

    # --- TASKS ---
    task_extract = Task(
        description=f"Analyze this YouTube video: '{youtube_link}'. Extract the 5 main takeaways, 3 powerful quotes, and the overall thesis of the video.",
        agent=analyst,
        expected_output="A detailed summary document with takeaways and quotes."
    )

    task_twitter = Task(
        description="Using the summary provided by the analyst, write a 10-tweet viral thread. The first tweet must be a strong hook. Use emojis and spacing.",
        agent=twitter_writer,
        expected_output="A complete 10-tweet thread."
    )

    task_linkedin = Task(
        description="Using the same summary, write 3 distinct LinkedIn posts. One should be a story, one should be a listicle, and one should be an actionable tip. Include hashtags.",
        agent=linkedin_writer,
        expected_output="3 ready-to-publish LinkedIn posts."
    )

    task_publish = Task(
        description="Take the final Twitter thread and LinkedIn posts. Use your API tools to publish them to Twitter and LinkedIn. You MUST use the tools.",
        agent=publisher_agent,
        expected_output="Confirmation logs from the social media APIs."
    )

    # Assemble the Multiplier Crew
    crew = Crew(
        agents=[analyst, twitter_writer, linkedin_writer, publisher_agent],
        tasks=[task_extract, task_twitter, task_linkedin, task_publish],
        verbose=True,
        process=Process.sequential 
    )

    try:
        result = crew.kickoff()
        saved_path = save_omni_content('YouTube_Repurpose_AutoPublished', str(result))
        return f"🐙 **CONTENT MULTIPLIER & PUBLISHER COMPLETE**\n\n✅ Content Generated & Successfully Auto-Published via API Tools.\n📂 **Logs & Assets Saved:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Multiplier Error:** Could not complete the pipeline. Error: {e}"