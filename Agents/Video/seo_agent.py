import os
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama-3.3-70b-versatile")
def get_seo_agent():
    return Agent(
        role='YouTube Growth & SEO Specialist',
        goal='Create the perfect Title, Tags, and Description',
        backstory='You are an algorithm hacker. You know the best keywords for high CTR.',
        allow_delegation=False,
        llm=llm
    )