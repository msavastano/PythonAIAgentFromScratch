from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from datetime import datetime
from langchain.chains import LLMMathChain
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
import wikipedia
import re

def get_tools(llm):
    def save_to_txt(data: str, filename: str = "research_output.txt"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

        with open(filename, "a", encoding="utf-8") as f:
            f.write(formatted_text)

        return f"Data successfully saved to {filename}"

    save_tool = Tool(
        name="save_text_to_file",
        func=save_to_txt,
        description="Saves structured research data to a text file.",
    )

    search = DuckDuckGoSearchRun()
    search_tool = Tool(
        name="search",
        func=search.run,
        description="Search the web for information",
    )

    wikipedia_api = WikipediaAPIWrapper(
        wiki_client=wikipedia,
        top_k_results=3,
        lang="en",
        load_all_available_meta=False,
        doc_content_chars_max=4000
    )
    wikipedia_query = WikipediaQueryRun(api_wrapper=wikipedia_api)

    wiki_tool = Tool(
        name="wikipedia",
        func=wikipedia_query.run,
        description="Search Wikipedia for information about a topic"
    )

    arxiv_tool = ArxivQueryRun()

    calculator_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

    def run_calculator(query: str):
        # The LLM can be a bit verbose, so we need to extract the expression
        # from the output.
        try:
            return calculator_chain.run(query)
        except ValueError as e:
            # If the initial run fails, it might be because the LLM is being too verbose.
            # We can try to extract the math expression from the output and run it again.
            llm_output = str(e)
            match = re.search(r"```text\n(.*)\n```", llm_output, re.DOTALL)
            if match:
                expression = match.group(1)
                return calculator_chain.run(expression)
            else:
                raise e


    calculator_tool = Tool.from_function(
        name="calculator",
        func=run_calculator,
        description="useful for when you need to answer questions about math"
    )

    return [save_tool, search_tool, wiki_tool, arxiv_tool, calculator_tool]
