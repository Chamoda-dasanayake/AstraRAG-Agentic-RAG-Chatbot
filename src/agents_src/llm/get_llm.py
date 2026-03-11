from crewai import LLM

from src.agents_src.llm.llm_configuration import LLM_CONFIG
from src.agents_src.config.agent_settings import AgentSettings


def get_llm_for_agent(agent_name: str) -> LLM:
    settings = AgentSettings()

    # Prefer explicit environment override, otherwise fall back to config
    model = (
        getattr(settings, "MODEL_NAME", None)
        or LLM_CONFIG.get(agent_name, {}).get("model", "groq/llama-3.3-70b-versatile")
    )
    temperature = (
        getattr(settings, "MODEL_TEMPERATURE", None)
        or LLM_CONFIG.get(agent_name, {}).get("temperature", 0.0)
    )
    max_tokens = LLM_CONFIG.get(agent_name, {}).get("max_tokens") or LLM_CONFIG.get(agent_name, {}).get("max_completion_tokens")

    # If a bare model name was provided, prefix with groq to avoid falling back to OpenAI
    if "/" not in model:
        model = f"groq/{model}"

    # Prevent accidental use of OpenAI models when user requested non-OpenAI providers
    if "openai" in model.lower():
        raise RuntimeError(
            "OpenAI models are disallowed by configuration. Please use a Groq (groq/...) model identifier."
        )

    api_key = getattr(settings, "GROQ_API_KEY", None)

    # Only set api_base if user explicitly provides it; otherwise let litellm route correctly
    api_base = getattr(settings, "GROQ_API_BASE", None)

    try:
        # Groq has strict timeout requirements; set reasonable timeout
        timeout = 60.0  # 60 seconds for Groq models
        
        llm_kwargs = {
            "model": model,
            "temperature": temperature,
            "api_key": api_key,
            "timeout": timeout,
        }
        if api_base:
            llm_kwargs["api_base"] = api_base
        # Respect configured `max_tokens` when provided to avoid unintentional increases
        if max_tokens:
            llm_kwargs["max_tokens"] = max_tokens
        else:
            llm_kwargs["max_tokens"] = 2048  # Default reasonable size for small model

        return LLM(**llm_kwargs)
    except Exception as e:
        raise RuntimeError(
            f"Failed creating LLM(model={model}). Ensure your GROQ_API_KEY is set and the model is enabled in your Groq org settings. Original error: {e}"
        )