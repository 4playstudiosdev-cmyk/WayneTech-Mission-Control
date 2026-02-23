import os
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama3-70b-8192")
def get_publishing_agent():
    return Agent(
        role='Channel Manager',
        goal='Plan the publishing schedule and pinned comment',
        backstory='You manage the community and ensure the video launches successfully.',
        allow_delegation=False,
        llm=llm
    )