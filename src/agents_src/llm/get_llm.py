from crewai import LLM

from src.agents_src.config.agent_settings import AgentSettings


def get_llm_for_agent(agent_name: str) -> LLM:
    settings = AgentSettings()
    temp = settings.MODEL_TEMPERATURE if settings.MODEL_TEMPERATURE is not None else 0.1
    return LLM(
        model=settings.crewai_openai_model(),
        api_key=settings.OPENAI_API_KEY,
        temperature=temp,
    )