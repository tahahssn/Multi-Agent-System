from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, web_scrape
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="openrouter/free",
    temperature=0,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

# Create a first agent with a web search tool
search_agent = create_agent(
    model=llm,
    tools=[web_search],
)

# Create a second agent with a web scrape tool
scrape_agent = create_agent(
    model=llm,
    tools=[web_scrape],
)

# Writer prompt template & chain for the agents
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.
        Topic: {topic}

        Research Gathered:
        {research}

        Structure the report as:
        - Introduction
        - Key Findings (minimum 3 well-explained points)
        - Conclusion
        - Sources (list all URLs found in the research)

        Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic prompt template & chain for the agents
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

        Report:
        {report}

        Respond in this exact format:

        Score: X/10

        Strengths:
        - ...
        - ...

        Areas to Improve:
        - ...
        - ...

        One line verdict:
        ..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()