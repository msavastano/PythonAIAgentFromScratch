import unittest
from unittest.mock import patch, MagicMock
import main

class TestMain(unittest.TestCase):

    def test_run_agent_with_extra_text(self):
        # The problematic response from the user's description
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
  "summary": "The GDP of the United States for the last 3 years is:\\n2023: $27,720,700 million\\n2024: $29,180,000 million\\n2025: $30,340,000 million\\nThe average of these 3 years is $29,080,233.33 million.",
  "sources": [
    "https://www.bea.gov/data/gdp/gross-domestic-product",
    "https://www.imf.org/external/datamapper/NGDPD@WEO/OEMDC/ADVEC/WEOWORLD/USA"
  ],
  "tools_used": [
    "search",
    "calculator"
  ]
}
"""
        # Create a mock agent_executor
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {"output": [{"text": raw_response_text}]}

        # Patch the agent_executor in the main module
        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")

            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")
            self.assertIsInstance(result["sources"], list)
            self.assertIsInstance(result["tools_used"], list)

    def test_run_agent_with_stray_brace_in_preamble(self):
        raw_response_text = """
I am thinking about the structure { "topic": ..., "summary": ... }.
Now, here is the real data:
{
  "topic": "US GDP for the last 3 years",
  "summary": "The GDP of the United States for the last 3 years is...",
  "sources": [],
  "tools_used": []
}
"""
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {"output": [{"text": raw_response_text}]}

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")

            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")

    def test_run_agent_with_trailing_text(self):
        raw_response_text = """
{
  "topic": "US GDP for the last 3 years",
  "summary": "The GDP of the United States for the last 3 years is...",
  "sources": [],
  "tools_used": []
}
This is some trailing text.
"""
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {"output": [{"text": raw_response_text}]}

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")

            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")

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
  "sources": [],
  "tools_used": []
}
"""
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {"output": [{"text": raw_response_text}]}

        with patch('main.agent_executor', mock_agent_executor):
            result = main.run_agent("some query")
            self.assertNotIn("error", result)
            self.assertEqual(result["topic"], "US GDP for the last 3 years")


    def test_research_response_model(self):
        # Test that the pydantic model is correctly defined
        # This is to ensure we don't have duplicate fields
        fields = main.ResearchResponse.model_fields.keys()
        self.assertEqual(len(fields), 4)
        self.assertIn("topic", fields)
        self.assertIn("summary", fields)
        self.assertIn("sources", fields)
        self.assertIn("tools_used", fields)

if __name__ == '__main__':
    unittest.main()
