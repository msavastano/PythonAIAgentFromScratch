from dotenv import load_dotenv
from pydantic import BaseModel
# from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool, arxiv_tool, python_repl_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# llm = ChatAnthropic(model_name="claude-3-5-sonnet-20241022", timeout=60, stop=None)
llm = ChatAnthropic(model_name="claude-3-haiku-20240307", timeout=60, stop=None)


parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use neccessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool, arxiv_tool, python_repl_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent(query: str):
    raw_response = agent_executor.invoke({"query": query})
    try:
        output = raw_response.get("output")
        if output and isinstance(output, list) and len(output) > 0 and "text" in output[0]:
            structured_response = parser.parse(output[0]["text"])
            return structured_response.dict()
        else:
            return {"error": "No valid output found in response.", "raw_response": raw_response}
    except Exception as e:
        return {"error": f"Error parsing response: {e}", "raw_response": raw_response}

if __name__ == '__main__':
    query = input("What can i help you research? ")
    response = run_agent(query)
    print(response)
