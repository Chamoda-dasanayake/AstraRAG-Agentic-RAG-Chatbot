from crewai import Crew

from src.agents_src.agents.question_answer_agent import qa_agent
from src.agents_src.tasks.question_answer_task import qa_task

qa_crew = Crew(
    agents=[qa_agent],
    tasks=[qa_task],
    verbose=True,
)