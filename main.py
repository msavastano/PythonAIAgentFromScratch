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
    tool_details: list


# llm = ChatAnthropic(model_name="claude-3-5-sonnet-20241022", timeout=60, stop=None)
llm = ChatAnthropic(model_name="claude-3-haiku-20240307", timeout=60, stop=None)


parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Role: You are a diligent and expert research assistant. Your primary function is to provide accurate, comprehensive, and well-sourced information by using your search and browsing tools.

You will be given a research topic and a list of key questions to answer. Your goal is to conduct thorough research and then synthesize the findings into a coherent summary.

Process (Orchestration):
1.  **Formulate Queries:** Begin by creating and executing multiple search queries to gather a broad range of sources on the topic.
2.  **Evaluate Sources:** Analyze the search results to identify the most credible, authoritative, and relevant sources (e.g., academic papers, reputable news organizations, official reports, expert analyses).
3.  **Extract Information:** Browse the top sources to extract key facts, data points, arguments, and quotes that directly address the "Key Questions to Answer."
4.  **Synthesize Findings:** Consolidate the information from all sources into a coherent and easy-to-understand summary. Do not simply list facts; explain the connections and context.
5.  **Cite Sources:** Provide clear citations for all information presented so the user can verify the findings.

Guardrails (Rules & Constraints):
-   **Cite Everything:** Attribute all facts, statistics, and direct quotes to their original source.
-   **Remain Objective:** Do not include personal opinions, assumptions, or unverified claims.
-   **Present Multiple Perspectives:** If the topic is complex or debated, represent the main viewpoints fairly.
-   **Prioritize Currency:** Use the most recent and up-to-date information available unless the query specifically requests historical context.

Your final answer MUST be a JSON object that follows this format. Do not include any other text in your response.
\n{format_instructions}""",
        ),
        ("placeholder", "{chat_history}"),
        (
            "human",
            """Research Objective: To conduct thorough research on the following topic: {topic}

Key Questions to Answer:
{questions}""",
        ),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = get_tools(llm)
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

def run_agent(topic: str, questions: List[str]):
    # Format the questions into a numbered list string
    formatted_questions = "\n".join([f"{i}. {q}" for i, q in enumerate(questions, 1)])

    # Pass the topic and formatted questions to the agent
    raw_response = agent_executor.invoke({
        "topic": topic,
        "questions": formatted_questions,
        "chat_history": []
    })
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

        # Extract tool details from intermediate steps
        tool_details = []
        if "intermediate_steps" in raw_response:
            for action, observation in raw_response["intermediate_steps"]:
                tool_details.append(
                    {
                        "tool_name": action.tool,
                        "tool_input": action.tool_input,
                        "tool_output": str(observation),
                    }
                )

        # Find the start of the JSON object and loop until a valid JSON object is found
        start_index = output.find('{')
        while start_index != -1:
            try:
                # Decode the JSON part of the string
                json_obj, _ = json.JSONDecoder().raw_decode(output[start_index:])
                # Add the tool details to the python object
                json_obj['tool_details'] = tool_details
                # Re-encode to string to parse with pydantic
                json_str = json.dumps(json_obj)
                structured_response = parser.parse(json_str)
                return structured_response.model_dump()
            except (json.JSONDecodeError, OutputParserException):
                start_index = output.find('{', start_index + 1)

        raise ValueError("No valid JSON object found in the output.")
    except Exception as e:
        serializable_raw_response = {
            k: str(v) for k, v in raw_response.items()
        }
        return {"error": f"Error parsing response: {e}", "raw_response": serializable_raw_response}

if __name__ == '__main__':
    topic = input("Enter the research topic: ")
    questions_str = input("Enter the questions, separated by newlines:\n")
    questions = questions_str.split('\n')
    response = run_agent(topic, questions)
    print(response)
