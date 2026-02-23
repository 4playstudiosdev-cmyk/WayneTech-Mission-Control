import os
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama3-70b-8192")
def get_script_agent():
    return Agent(
        role='Lead Scriptwriter',
        goal='Write an engaging script with Hook, Body, and CTA',
        backstory='You write scripts that keep retention high. You use storytelling frameworks.',
        allow_delegation=False,
        llm=llm
    )