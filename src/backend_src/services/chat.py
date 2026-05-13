import logging
import time
import random
from typing import List

from litellm.exceptions import RateLimitError

from src.agents_src.tools.rag_qa_tool import retrieve_context


class LocalRateLimitError(Exception):
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


from src.agents_src.crew import qa_crew

logger = logging.getLogger(__name__)


CASUAL_PATTERNS = {
    "hi", "hello", "hey", "hii", "hiii", "howdy", "sup",
    "thanks", "thank you", "thx", "bye", "goodbye", "see you",
    "good morning", "good evening", "good night", "good afternoon",
}


def _is_casual_message(text: str) -> bool:
    cleaned = text.strip().lower().rstrip("!?.,")
    return cleaned in CASUAL_PATTERNS


def _trim_history_for_attempt(history: List[dict], attempt: int) -> List[dict]:
    if not history:
        return []
    if attempt == 1:
        keep = 12
    elif attempt == 2:
        keep = 8
    elif attempt == 3:
        keep = 4
    else:
        keep = 1
    return history[-keep:]


def get_answer(chat_history: List[dict]) -> dict:
    logger.info(f"Received chat_history with {len(chat_history)} messages")

    if not chat_history:
        raise ValueError("chat_history is empty")

    last_user_message = chat_history[-1]
    user_query = last_user_message["content"]
    logger.info(f"Extracted user_query (len={len(user_query)}): {user_query[:120]}")

    # Handle casual messages without invoking the RAG pipeline
    if _is_casual_message(user_query):
        logger.info("Casual message detected, skipping RAG pipeline")
        return {
            "answer": "Hi! 👋 I can help you understand your documents. Upload a PDF in the sidebar, then ask me anything about it!",
            "sources": [],
            "tool_used": "Greeting Handler",
            "rationale": "Casual greeting detected — no document lookup needed.",
        }

    # ── STEP 1: Retrieve context DIRECTLY (guaranteed, not dependent on agent) ──
    logger.info("Retrieving context from vector store...")
    retrieved_context = retrieve_context(user_query, top_k=3)
    logger.info(f"Retrieved context length: {len(retrieved_context)} chars")

    history_without_last = chat_history[:-1]

    # Configure retry/backoff
    max_attempts = 6
    base_delay = 1.0

    for attempt in range(1, max_attempts + 1):
        trimmed_history = _trim_history_for_attempt(history_without_last, attempt)
        input_data = {
            "user_query": user_query,
            "chat_history": trimmed_history,
            "retrieved_context": retrieved_context,
        }

        logger.debug(f"Attempt {attempt}/{max_attempts}, trimmed_history len={len(trimmed_history)}")

        try:
            result = qa_crew.kickoff(input_data)
            logger.info(f"Result from qa_crew: {result}")
            logger.info(f"Result type: {type(result)}")
            return result

        except RateLimitError as e:
            msg = str(e)
            retry_after = None
            try:
                import re
                m = re.search(r"Please try again in ([0-9]+(?:\.[0-9]+)?)s", msg)
                if m:
                    retry_after = float(m.group(1))
            except Exception:
                retry_after = None

            if retry_after is None:
                retry_after = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)

            logger.warning(
                f"Rate limit hit (attempt {attempt}/{max_attempts}), retrying after {retry_after:.2f}s: {msg}"
            )
            time.sleep(retry_after)
            continue

        except Exception as ex:
            logger.error(f"Error on attempt {attempt}/{max_attempts}: {type(ex).__name__}: {ex}", exc_info=True)
            raise

    raise LocalRateLimitError("Rate limit exceeded after retries; please try again later.")
