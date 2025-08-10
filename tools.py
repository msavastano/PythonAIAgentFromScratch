from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime

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

from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
import wikipedia

# Create Wikipedia tool
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

