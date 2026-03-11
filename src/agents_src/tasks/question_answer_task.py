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
    Answer the user query "{user_query}" using a Retrieval-Augmented Generation (RAG) pipeline.
    chat_history: "{chat_history}"

    Instructions:
    - Retrieve relevant context from the document store
    - Prioritize evidence that directly addresses the query
    - Synthesize a clear, accurate answer grounded in the retrieved sources or chat history
    - If the query cannot be answered from the knowledge source or chat history, do not generate your own response.
     Instead, state clearly that the knowledge source does not contain the required information.
    - Provide transparency by including references, tool usage, and reasoning steps
    """,
    expected_output=""" 
    You MUST return ONLY a valid JSON object matching the requested schema. DO NOT include any additional conversational text.
    The output must strictly be a JSON object with the following structure:
    {
      "answer": "Direct response to the query. If no answer is found, return: 'The knowledge source does not contain the required information.'",
      "sources": ["List of document titles/sections used (use empty list [] if none)"],
      "tool_used": "Name of the retrieval/analysis tool invoked, or 'None'",
      "rationale": "Brief explanation of why this answer was chosen, or why no relevant information was found."
    }
    """,
    output_pydantic=AnswerStructure,
)
