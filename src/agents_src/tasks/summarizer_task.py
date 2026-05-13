from crewai import Task
from pydantic import BaseModel

from src.agents_src.agents.summarizer_agent import summarizer_agent
from src.agents_src.tasks.question_answer_task import qa_task


class SummaryStructure(BaseModel):
    summary: str
    key_takeaways: list[str]
    original_sources: list[str]


summarizer_task = Task(
    agent=summarizer_agent,
    name="Summarization Task",
    description="""
    Take the output from the Question Answering Task and create a concise, refined summary.

    Instructions:
    - Summarize the answer in 2-3 sentences maximum.
    - Extract 2-3 key takeaways or important points.
    - Preserve document sources and accuracy from the original answer.
    - Make the response more readable and user-friendly.
    - Do not add information not present in the original answer.
    """,
    expected_output="""
    You MUST return ONLY a valid JSON object matching the requested schema. DO NOT include any additional conversational text.
    The output must strictly be a JSON object with the following structure:
    {
      "summary": "Concise 2-3 sentence summary",
      "key_takeaways": ["Key point 1", "Key point 2", "Key point 3"],
      "original_sources": ["Source 1", "Source 2"]
    }
    """,
    output_pydantic=SummaryStructure,
    context=[qa_task],
)
