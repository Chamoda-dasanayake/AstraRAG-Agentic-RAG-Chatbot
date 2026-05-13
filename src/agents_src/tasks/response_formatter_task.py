from crewai import Task
from pydantic import BaseModel

from src.agents_src.agents.response_formatter_agent import response_formatter_agent
from src.agents_src.tasks.fact_checker_task import fact_checker_task


class FormattedResponse(BaseModel):
    formatted_answer: str
    follow_up_suggestions: list[str]
    confidence_level: str
    sources: list[str]


response_formatter_task = Task(
    agent=response_formatter_agent,
    name="Conversational Response Formatting Task",
    description="""
    Take the fact-checked answer from the previous agent and transform it into
    a warm, engaging, and beautifully formatted conversational response.

    Original user query: "{user_query}"
    Chat history: "{chat_history}"

    FORMATTING RULES:
    1. **Tone**: Friendly, professional, and approachable — like a helpful expert colleague.
       Use natural language, not bullet-point dumps. Start with a brief warm opener
       that acknowledges the question (e.g., "Great question!" or "Here's what I found").
    2. **Structure**: Use markdown formatting for readability:
       - Use **bold** for key terms and important points.
       - Use bullet points or numbered lists ONLY when listing 3+ items.
       - Keep paragraphs short (2-3 sentences max).
    3. **Confidence Level**: Based on the source evidence:
       - "High" → The answer is fully supported by document sources.
       - "Medium" → The answer is partially supported or inferred from sources.
       - "Low" → The answer has weak or no source support.
    4. **Follow-Up Suggestions**: Generate exactly 2-3 relevant follow-up questions
       the user might want to ask next. These should be specific to the topic and
       document content, not generic. Write them as natural questions.
    5. **Edge Cases**:
       - If the previous answer says "not found" or similar, respond warmly:
         "I couldn't find that specific information in your documents. Here are
         some things I CAN help with based on what's in your knowledge base..."
       - Never say "I don't know" — always guide the user toward what IS available.
    6. **Sources**: Preserve all source document names from the fact-checker's output.
    7. **Length**: Keep the formatted answer concise but complete — aim for 3-6 sentences.
       Do NOT pad with unnecessary filler.
    """,
    expected_output="""
    You MUST return ONLY a valid JSON object. DO NOT include any additional text.
    {
      "formatted_answer": "The warm, beautifully formatted response using markdown",
      "follow_up_suggestions": ["Relevant follow-up question 1?", "Relevant follow-up question 2?", "Relevant follow-up question 3?"],
      "confidence_level": "High | Medium | Low",
      "sources": ["Source document 1", "Source document 2"]
    }
    """,
    output_pydantic=FormattedResponse,
    context=[fact_checker_task],
)
