import time
import os
import glob
import sys
import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- FOLDER PATHS FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'Agents')

sys.path.append(agents_dir)
sys.path.append(os.path.join(agents_dir, 'Marketing'))
sys.path.append(os.path.join(agents_dir, 'Tech'))
sys.path.append(os.path.join(agents_dir, 'Video'))
sys.path.append(os.path.join(agents_dir, 'Oracle'))
sys.path.append(os.path.join(agents_dir, 'SEO'))
sys.path.append(os.path.join(agents_dir, 'Legal'))       
sys.path.append(os.path.join(agents_dir, 'Finance'))     
sys.path.append(os.path.join(agents_dir, 'OmniReader'))  
sys.path.append(os.path.join(agents_dir, 'Multiplier'))  
sys.path.append(os.path.join(agents_dir, 'sales'))       

def agent_offline(task): return "⚠️ **System Alert:** This agent is offline."

run_marketing_crew = agent_offline
run_tech_crew = agent_offline
run_video_crew = agent_offline
run_kimi_squad = agent_offline
run_oracle_crew = agent_offline
run_mass_seo_campaign = agent_offline
run_legal_crew = agent_offline         
run_finance_crew = agent_offline       
run_omnireader_crew = agent_offline    
run_multiplier_crew = agent_offline
run_sales_crew = agent_offline

print("\n📡 Connecting Justice League to GROQ CLOUD...")

if not GROQ_API_KEY:
    print("❌ ERROR: Groq API Key not found! Add it in the Dashboard UI first.")
    sys.exit()

try:
    try: from marketing import run_marketing_crew
    except: pass
    try: from tech import run_tech_crew
    except: pass
    try: from video import run_video_crew
    except: pass
    try: from kimi_research import run_kimi_squad
    except: pass
    try: from oracle_intel import run_oracle_crew
    except: pass
    try: from seo_empire import run_mass_seo_campaign
    except: pass
    try: from Corporate_Lawyer import run_legal_crew
    except: pass
    try: from Investment_Banker import run_finance_crew
    except: pass
    try: from omni_reader import run_omnireader_crew
    except: pass
    try: from content_multiplier import run_multiplier_crew
    except: pass
    try: from SalesSquad import run_sales_crew
    except: 
        try: from sales_dept import run_sales_crew
        except: pass
    print("✅ All Cloud Agents Ready.")
except Exception as e:
    pass

# 🔥 THE CLOUD SWITCH 🔥
# Global override so ALL agents in your folders automatically use Groq!
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_API_KEY"] = GROQ_API_KEY

llm = ChatOpenAI(model="llama3-70b-8192", base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

MEMORY_FOLDER = "memory_logs"
SILENCE_THRESHOLD = 5 
last_processed_msg_text = "" 

def get_latest_memory_file():
    if not os.path.exists(MEMORY_FOLDER): return None
    files = glob.glob(f"{MEMORY_FOLDER}/*.txt")
    return max(files, key=os.path.getmtime) if files else None

def read_unprocessed_user_message(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            if not lines: return None
            if "] USER:" in lines[-1]: return lines[-1].split("USER:", 1)[1].strip()
    except: return None
    return None

def notify_batman(message):
    latest_file = get_latest_memory_file()
    if latest_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(latest_file, "a", encoding="utf-8") as f: f.write(f"\n[{timestamp}] SYSTEM: {message}\n")

print("\n🦇 Batcomputer Cloud Observer is ONLINE...\n")

while True:
    latest_file = get_latest_memory_file()
    if latest_file:
        try: last_msg_time = os.path.getmtime(latest_file)
        except: continue
            
        if (time.time() - last_msg_time) > SILENCE_THRESHOLD:
            last_user_msg = read_unprocessed_user_message(latest_file)
            
            if last_user_msg and last_user_msg != last_processed_msg_text:
                last_processed_msg_text = last_user_msg
                print(f"\n⚡ Cloud Processing: '{last_user_msg[:50]}...'")
                
                msg_upper = last_user_msg.upper()
                decision = "NONE"

                if "REPURPOSE" in msg_upper or "TURN THIS VIDEO" in msg_upper: decision = "MULTIPLIER"
                elif "LEAD" in msg_upper or "DM" in msg_upper or "OUTREACH" in msg_upper: decision = "SALES"
                elif "YOUTUBE.COM" in msg_upper or "YOUTU.BE" in msg_upper: decision = "YOUTUBE"
                elif "CONTRACT" in msg_upper or "LEGAL" in msg_upper or "SUE " in msg_upper: decision = "LEGAL"
                elif "INVEST" in msg_upper or "STOCK" in msg_upper or "FINANCE" in msg_upper: decision = "FINANCE"
                elif "HTTP://" in msg_upper or "HTTPS://" in msg_upper or "WWW." in msg_upper: decision = "ORACLE"
                elif "BLOG" in msg_upper or "SEO" in msg_upper or "ARTICLE" in msg_upper: decision = "SEO"
                else:
                    routing_prompt = f"""Analyze this message: "{last_user_msg}". Which department? Choose EXACTLY ONE WORD: MULTIPLIER, SALES, LEGAL, FINANCE, YOUTUBE, SEO, MARKETING, TECH, VIDEO, RESEARCH, ORACLE."""
                    try: decision = llm.invoke(routing_prompt).content.upper().strip()
                    except: pass

                if "MULTIPLIER" in decision:
                    notify_batman("🐙 **Multiplier:** Generating Omni-channel content from video...")
                    result = run_multiplier_crew(last_user_msg)
                    notify_batman(f"✅ **Repurposing Done:**\n{result}")

                elif "SALES" in decision:
                    notify_batman("📅 **LeadBooker:** Hunting leads and drafting outreach DMs...")
                    result = run_sales_crew(last_user_msg)
                    notify_batman(f"✅ **Sales Outreach Ready:**\n{result}")

                elif "LEGAL" in decision:
                    notify_batman("⚖️ **Daredevil:** Scanning legal documents...")
                    result = run_legal_crew(last_user_msg)
                    notify_batman(f"✅ **Legal Audit Done:**\n{result}")

                elif "FINANCE" in decision:
                    notify_batman("💰 **Lucius:** Crunching market numbers and VC data...")
                    result = run_finance_crew(last_user_msg)
                    notify_batman(f"✅ **Finance Report Done:**\n{result}")

                elif "YOUTUBE" in decision:
                    notify_batman("🧠 **Brainiac:** Extracting video transcripts...")
                    result = run_omnireader_crew(last_user_msg)
                    notify_batman(f"✅ **Extraction Done:**\n{result}")

                elif "SEO" in decision:
                    notify_batman("✍️ **SEO Team:** Mass Blog Campaign initiated...")
                    clean_kw = last_user_msg.lower().replace("write blogs on", "").replace("seo", "")
                    result = run_mass_seo_campaign(clean_kw)
                    notify_batman(f"✅ **SEO Done:**\n{result}")

                elif "ORACLE" in decision:
                    notify_batman("🔮 **Oracle:** Initiating Web Spy Protocol...")
                    result = run_oracle_crew(last_user_msg)
                    notify_batman(f"✅ **Intel Done:**\n{result}")
                
                elif "TECH" in decision or "CODE" in msg_upper:
                    notify_batman("🤖 **Cyborg:** Compiling code...")
                    result = run_tech_crew(last_user_msg)
                    notify_batman(f"✅ **Code Done:**\n{result}")
                
                elif "VIDEO" in decision:
                    notify_batman("💍 **Green Lantern:** Scripting video...")
                    result = run_video_crew(last_user_msg)
                    notify_batman(f"✅ **Script Done:**\n{result}")
                
                elif "RESEARCH" in decision:
                    notify_batman("👽 **Manhunter:** Deep Research initiated...")
                    result = run_kimi_squad(last_user_msg)
                    notify_batman(f"✅ **Research Done:**\n{result}")
                
                elif "MARKETING" in decision:
                    notify_batman("🦸‍♂️ **Superman:** Executing OpenClaw Ad Campaign...")
                    result = run_marketing_crew(last_user_msg)
                    notify_batman(f"✅ **Campaign Done:**\n{result}")
                
                else:
                    notify_batman("🦇 **Batman:** Task unclear. Need more details.")

    time.sleep(3)