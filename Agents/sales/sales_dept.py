import os
import datetime
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# ☁️ Dynamic LLM Configuration
def get_llm():
    return ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL_NAME", "llama-3.3-70b-versatile"),
        base_url=os.environ.get("OPENAI_API_BASE", "https://api.groq.com/openai/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "NA")
    )

# 🔥 THE BULLETPROOF EMAIL FUNCTION 🔥
def send_email_func(json_input: str) -> str:
    """Asli email bhejne ka function jo sirf ek JSON string leta hai taake crash na ho."""
    try:
        # JSON parsing safely
        data = json.loads(json_input)
        to_email = data.get("to_email")
        subject = data.get("subject")
        body = data.get("body")
    except Exception as e:
        # Try alternate parsing if LLM gives single quotes
        import ast
        try:
            data = ast.literal_eval(json_input)
            to_email = data.get("to_email")
            subject = data.get("subject")
            body = data.get("body")
        except:
            return f"❌ FAILED: Agent generated invalid format. Must be JSON. Error: {str(e)}"
        
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "") 
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return "⚠️ SKIPPED: Asli Email bhejne ke liye Dashboard ki sidebar mein 'Email Engine Setup' mukammal karein."

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"✅ SUCCESS: {to_email} par '{subject}' ke unwan se email bhej di gayi hai!"
    except Exception as e:
        return f"❌ FAILED: Email nahi bheji ja saki. Wajah: {str(e)}"

# 🛡️ THE TOOL WRAPPER (No @tool decorator to prevent Pydantic Crash)
send_email_tool = Tool(
    name="Send Real Cold Email",
    func=send_email_func,
    description='''Is tool ka istemaal tab karein jab prospect ko asal mein email bhejna ho. 
    Aapka input LAZMI ek valid JSON string hona chahiye jisme ye 3 keys hon: "to_email", "subject", "body". 
    Example Input: {"to_email": "client@example.com", "subject": "Hello", "body": "We offer AI services."}'''
)

def save_leads(task_name, content):
    folder = "Deliverables/Sales_Leads"
    if not os.path.exists(folder): os.makedirs(folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/Lead_Gen_Report_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def run_sales_crew(product_or_niche):
    print(f"\n💰 AUTONOMOUS SALES DEPARTMENT ACTIVATED: {product_or_niche}\n")
    
    active_llm = get_llm()

    reddit_discord_scout = Agent(
        role='Community Lead Hunter',
        goal='Identify target audience and potential contact methods.',
        backstory='Aap aise logo ko dhoondhte hain jinhe solution ki zaroorat hai. Aap market ke gaps ko samajhte hain.',
        allow_delegation=False,
        llm=active_llm
    )

    email_closer = Agent(
        role='Cold Email Executioner',
        goal='Write irresistible cold emails and ACTUALLY SEND THEM using your tools if an email address is provided.',
        backstory='Aap ek high-ticket closer hain. Aap sirf drafts nahi likhte, balke client ko asli email bhi bhejte hain.',
        tools=[send_email_tool], # 🔥 Safely passed tool
        allow_delegation=False,
        llm=active_llm
    )

    task_scout = Task(
        description=f"Analyze the request: '{product_or_niche}'. Find target audience angles.",
        agent=reddit_discord_scout,
        expected_output="Target audience ki tafseel aur psychological angles."
    )

    task_email = Task(
        description=f"Based on the request: '{product_or_niche}'. \nCRITICAL INSTRUCTION: Agar prompt mein koi email address diya gaya hai, to ek behtareen cold email likhein aur FAURAN usko bhejne ke liye 'Send Real Cold Email' tool ka istemaal karein! Input mein strictly ek JSON string dein jisme to_email, subject, aur body shamil hon. \nAgar email address nahi hai, to sirf ek 3-step sequence ka draft likhein.",
        agent=email_closer,
        expected_output="Bheji gayi emails ka log aur unka text, ya draft sequence agar email na mili ho."
    )

    crew = Crew(
        agents=[reddit_discord_scout, email_closer],
        tasks=[task_scout, task_email],
        verbose=True,
        process=Process.sequential 
    )

    try:
        result = crew.kickoff()
        saved_path = save_leads("Sales_Execution", str(result))
        return f"💰 **SALES OUTREACH MUKAMMAL HUI**\n\n✅ Live actions poore ho gaye hain. \n📂 **Logs Yahan Dekhein:** {saved_path}\n\n**Agent ki Summary:**\n{result}"
    except Exception as e:
        return f"⚠️ **Sales Crew mein Error:** {str(e)}"