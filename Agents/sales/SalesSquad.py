import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# ☁️ CLOUD READY
llm = ChatOpenAI(model="llama-3.3-70b-versatile")

# 🔥 THE INVESTOR PROOF: REAL EMAIL SENDING TOOL 🔥
@tool("Send Real Cold Email")
def send_email_tool(to_email: str, subject: str, body: str) -> str:
    """Use this tool to ACTUALLY SEND a real email to the prospect's email address."""
    # ⚠️ User Needs to set these in their .env file
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "") 
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "") # Note: Use Gmail App Password, not normal password
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return "⚠️ SKIPPED: Asli Email bhejne ke liye .env file mein SENDER_EMAIL aur SENDER_PASSWORD configure karein."

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
        return f"✅ SUCCESS: Email sent successfully to {to_email} with subject '{subject}'!"
    except Exception as e:
        return f"❌ FAILED: Email sending failed. Error: {str(e)}"

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

    reddit_discord_scout = Agent(
        role='Community Lead Hunter',
        goal='Identify target audience and potential contact methods.',
        backstory='You find people who are desperate for a solution.',
        allow_delegation=False,
        llm=llm
    )

    # 🚀 This Agent has the power to take ACTION
    email_closer = Agent(
        role='Cold Email Executioner',
        goal='Write irresistible cold emails and ACTUALLY SEND THEM using your tools if an email is provided.',
        backstory='You are a high-ticket closer. You don\'t just write drafts, you execute outreach automatically.',
        tools=[send_email_tool], # 🔥 Giving the agent the power to send email
        allow_delegation=False,
        llm=llm
    )

    task_scout = Task(
        description=f"Analyze the request: '{product_or_niche}'. Find target audience angles.",
        agent=reddit_discord_scout,
        expected_output="Target audience breakdown."
    )

    task_email = Task(
        description=f"Based on the request: '{product_or_niche}'. \n1. If an email address is provided in the prompt, WRITE a compelling cold email and USE THE 'Send Real Cold Email' TOOL to send it to them immediately! \n2. If no email is provided, just write a 3-step sequence draft.",
        agent=email_closer,
        expected_output="Log of emails sent or draft sequences."
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
        return f"💰 **SALES OUTREACH EXECUTED**\n\n✅ Live actions taken. \n📂 **Check Logs:** {saved_path}"
    except Exception as e:
        return f"⚠️ **Sales Crew Error:** {str(e)}"