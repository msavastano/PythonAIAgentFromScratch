from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
# from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import get_tools
import re
import json

load_dotenv()
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: List[str]
    tools_used: list[str]


# llm = ChatAnthropic(model_name="claude-3-5-sonnet-20241022", timeout=60, stop=None)
llm = ChatAnthropic(model_name="claude-3-haiku-20240307", timeout=60, stop=None)


parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant. Your final answer MUST be a JSON object that follows this format.
            Do not include any other text in your response.
            \n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = get_tools(llm)
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
        if isinstance(output, list):
            output = output[0].get("text", "")

        # The response can sometimes be wrapped in ```json ... ```, so we extract it.
        if output is not None and "```json" in output:
            output = output.split("```json")[1].split("```")[0]

        if output is None:
            raise ValueError("Agent did not return any output to parse.")
        if not isinstance(output, str):
            output = str(output)

        # Find the start of the JSON object and loop until a valid JSON object is found
        start_index = output.find('{')
        while start_index != -1:
            try:
                json_obj, _ = json.JSONDecoder().raw_decode(output[start_index:])
                json_str = json.dumps(json_obj)
                structured_response = parser.parse(json_str)
                return structured_response.model_dump()
            except (json.JSONDecodeError, OutputParserException):
                start_index = output.find('{', start_index + 1)

        raise ValueError("No valid JSON object found in the output.")
    except Exception as e:
        return {"error": f"Error parsing response: {e}", "raw_response": raw_response}

if __name__ == '__main__':
    query = input("What can i help you research? ")
    response = run_agent(query)
    print(response)
