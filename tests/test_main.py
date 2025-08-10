import unittest
from unittest.mock import patch, MagicMock
import main
from langchain_core.agents import AgentAction

class TestMain(unittest.TestCase):

    def test_run_agent_with_extra_text(self):
        raw_response_text = """
Okay, I now have the GDP data for the last 3 years:
2023: $27,720,700 million
2024: $29,180,000 million
2025: $30,340,000 million

To calculate the average:
(27720700 + 29180000 + 30340000) / 3 = 29080233.33 million

Here is the final output formatted as a JSON object:

{
  "topic": "US GDP for the last 3 years",
  "summary": "The GDP of the United States for the last 3 years is... (summary)",
  "sources": [
    "https://www.bea.gov/data/gdp/gross-domestic-product"
  ]
}
"""
        mock_agent_executor = MagicMock()
        mock_action = AgentAction(tool="mock_tool", tool_input={"query": "GDP"}, log="")
        mock_agent_executor.invoke.return_value = {
            "output": raw_response_text,
            "intermediate_steps": [(mock_action, "some_observation")]
        }

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")

            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")
            self.assertIsInstance(result["sources"], list)
            self.assertIsInstance(result["tool_details"], list)
            self.assertEqual(len(result["tool_details"]), 1)
            self.assertEqual(result["tool_details"][0]['tool_name'], 'mock_tool')

    def test_run_agent_with_stray_brace_in_preamble(self):
        raw_response_text = """
I am thinking about the structure { "topic": ..., "summary": ... }.
Now, here is the real data:
{
  "topic": "US GDP for the last 3 years",
  "summary": "The GDP of the United States for the last 3 years is...",
  "sources": []
}
"""
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {
            "output": raw_response_text,
            "intermediate_steps": []
        }

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")

            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")
            self.assertEqual(result["tool_details"], [])

    def test_run_agent_with_trailing_text(self):
        raw_response_text = """
{
  "topic": "US GDP for the last 3 years",
  "summary": "The GDP of the United States for the last 3 years is...",
  "sources": []
}
This is some trailing text.
"""
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {
            "output": raw_response_text,
            "intermediate_steps": []
        }

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")

            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")
            self.assertEqual(result["tool_details"], [])

    def test_run_agent_with_nested_json(self):
        raw_response_text = """
Here is the data:
{
  "topic": "US GDP for the last 3 years",
  "summary": "The GDP of the United States for the last 3 years is...",
  "data": {
    "2023": 27720700,
    "2024": 29180000,
    "2025": 30340000
  },
  "sources": []
}
"""
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {
            "output": raw_response_text,
            "intermediate_steps": []
        }

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")
            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")
            self.assertEqual(result["tool_details"], [])


    def test_research_response_model(self):
        fields = main.ResearchResponse.model_fields.keys()
        self.assertEqual(len(fields), 4)
        self.assertIn("topic", fields)
        self.assertIn("summary", fields)
        self.assertIn("sources", fields)
        self.assertIn("tool_details", fields)

if __name__ == '__main__':
    unittest.main()
