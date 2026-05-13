from crewai import Task
from pydantic import BaseModel

from src.agents_src.agents.question_answer_agent import qa_agent


class AnswerStructure(BaseModel):
    answer: str
    sources: list[str]
    tool_used: str
    rationale: str


qa_task = Task(
    agent=qa_agent,
    name="Question Answering Task",
    description="""
    Query: "{user_query}"
    History: "{chat_history}"

    ===== PRE-RETRIEVED CONTEXT =====
    {retrieved_context}
    ===== END CONTEXT =====

    MANDATORY STEPS:
    1. You MUST call rag_query_tool with the user's query BEFORE answering.
       Always use the tool first, even if you think you know the answer.
    2. Read the PRE-RETRIEVED CONTEXT above as additional evidence.
    3. Combine the tool results and the context to form your answer.
    4. Only say "not found" AFTER the tool returns no results AND the context is empty.
    5. Include source document names in your sources list.
    """,
    expected_output="""
    Return ONLY a JSON object:
    {
      "answer": "Response based on retrieved documents, or 'The knowledge source does not contain the required information.'",
      "sources": ["document titles used, or empty list"],
      "tool_used": "rag_query_tool",
      "rationale": "brief reasoning about how the answer was derived"
    }
    """,
    output_pydantic=AnswerStructure,
)
