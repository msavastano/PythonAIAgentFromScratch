# Agent Instructions

This document provides instructions for AI agents on how to work with the codebase in this repository.

## Project Overview

This project is a research assistant that uses a large language model (LLM) to help with research tasks. It's built using Python and the LangChain framework. The agent is designed to take a user's research query, use a set of tools to find information, and then return a structured summary of the findings.

The main components are:
- `main.py`: The entry point of the application. It initializes the agent, tools, and LLM, and it handles the user interaction.
- `tools.py`: Defines the tools that the agent can use. Currently, it includes tools for web search, Wikipedia lookup, and saving results to a file.
- `requirements.txt`: Lists the necessary Python packages.
- `sample.env`: A template for the environment variables file, which is needed to store API keys.

## Setup Instructions

To run this project, you need to set up your environment.

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**
    - Create a copy of `sample.env` and name it `.env`.
    - Open the `.env` file and add your API key. The project is currently configured to use Anthropic's Claude model, so you will need an `ANTHROPIC_API_KEY`.
    ```
    ANTHROPIC_API_KEY="your-api-key-here"
    ```
    - If you want to use an OpenAI model, you will need to modify `main.py` to use `ChatOpenAI` and provide an `OPENAI_API_KEY` in the `.env` file.

## Usage

To run the agent, execute the `main.py` script from your terminal:

```bash
python main.py
```

The script will prompt you to enter a research query. After you provide a query, the agent will use its tools to find information and then print a structured summary of its findings.

## Adding New Tools

You can extend the agent's capabilities by adding new tools.

1.  **Define a tool function:** Open `tools.py` and create a new Python function that will perform the action for your tool. The function should take the necessary arguments and return a string.

2.  **Create a `Tool` instance:** In `tools.py`, create an instance of the `Tool` class from `langchain.tools`. You will need to provide a `name`, the `func` (your function), and a `description`. The `description` is important, as the LLM uses it to decide when to use the tool.

    ```python
    from langchain.tools import Tool

    # Example of a new tool
    def get_current_date(query: str):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    date_tool = Tool(
        name="get_current_date",
        func=get_current_date,
        description="Returns the current date.",
    )
    ```

3.  **Add the tool to the agent:** Open `main.py` and import your new tool from `tools.py`. Then, add the tool to the `tools` list.

    ```python
    # In main.py
    from tools import search_tool, wiki_tool, save_tool, date_tool # Import your new tool

    # ...

    tools = [search_tool, wiki_tool, save_tool, date_tool] # Add your new tool to the list
    ```
