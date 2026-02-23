import os
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama3-70b-8192")
def get_seo_agent():
    return Agent(
        role='YouTube Growth & SEO Specialist',
        goal='Create the perfect Title, Tags, and Description',
        backstory='You are an algorithm hacker. You know the best keywords for high CTR.',
        allow_delegation=False,
        llm=llm
    )