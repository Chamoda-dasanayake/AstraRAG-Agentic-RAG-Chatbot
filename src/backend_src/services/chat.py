import logging
import time
import random
from typing import List

from litellm.exceptions import RateLimitError


# Local exception to represent rate-limit exhaustion in our service layer
class LocalRateLimitError(Exception):
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after

from src.agents_src.crew import qa_crew

logger = logging.getLogger(__name__)


def _trim_history_for_attempt(history: List[dict], attempt: int) -> List[dict]:
    """Progressively trim chat history on retries to reduce token usage.

    attempt=1 -> keep up to 12 messages
    attempt=2 -> keep up to 8
    attempt=3 -> keep up to 4
    attempt>=4 -> keep last message only
    """
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
    
    # get the last message in the chat_history as user_query
    if not chat_history:
        raise ValueError("chat_history is empty")
    last_user_message = chat_history[-1]
    user_query = last_user_message["content"]
    logger.info(f"Extracted user_query (len={len(user_query)}): {user_query[:120]}")

    # Remove the last user message from chat_history
    history_without_last = chat_history[:-1]

    # Configure retry/backoff
    max_attempts = 6
    base_delay = 1.0

    for attempt in range(1, max_attempts + 1):
        # progressively trim history to reduce prompt size on retries
        trimmed_history = _trim_history_for_attempt(history_without_last, attempt)
        input_data = {
            "user_query": user_query,
            "chat_history": trimmed_history,
        }

        logger.debug(f"Attempt {attempt}/{max_attempts}, trimmed_history len={len(trimmed_history)}")

        try:
            result = qa_crew.kickoff(input_data)
            logger.info(f"Result from qa_crew: {result}")
            return result

        except RateLimitError as e:
            # Parse retry seconds from message if available, otherwise use exponential backoff with jitter
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
                # exponential backoff plus small jitter
                retry_after = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)

            logger.warning(
                f"Rate limit hit (attempt {attempt}/{max_attempts}), retrying after {retry_after:.2f}s: {msg}"
            )
            time.sleep(retry_after)
            continue

        except Exception as ex:
            logger.error(f"Error on attempt {attempt}/{max_attempts}: {type(ex).__name__}: {ex}", exc_info=True)
            # Re-raise other exceptions for upstream handling
            raise

    # If we exhausted retries, raise a local rate-limit error to be handled by caller
    raise LocalRateLimitError("Rate limit exceeded after retries; please try again later.")

