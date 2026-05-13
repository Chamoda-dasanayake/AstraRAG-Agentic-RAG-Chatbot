import logging
from fastapi import APIRouter, HTTPException
from litellm.exceptions import RateLimitError
from src.backend_src.services.chat import LocalRateLimitError
from pydantic import BaseModel
from typing import List
from src.backend_src.services.chat import get_answer

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatHistoryRequest(BaseModel):
    chat_history: List[ChatMessage]


@router.post("/chat/answer")
def chat_answer(request: ChatHistoryRequest):
    logger.info(f"Received API request with chat_history: {request.chat_history}")

    if not request.chat_history:
        raise HTTPException(status_code=400, detail="chat_history cannot be empty.")

    try:
        chat_history = [msg.dict() for msg in request.chat_history]
        result = get_answer(chat_history)

        if not result:
            raise ValueError("No response from crew")

        # Convert result to dict
        if isinstance(result, dict):
            response_data = result
        else:
            # CrewOutput or Pydantic model
            for method in ("to_dict", "model_dump", "dict"):
                if hasattr(result, method):
                    response_data = getattr(result, method)()
                    break
            else:
                response_data = {"answer": str(result), "sources": [], "tool_used": "N/A", "rationale": "N/A"}

        # Normalize: map new FormattedResponse fields
        if "formatted_answer" in response_data:
            response_data["answer"] = response_data["formatted_answer"]
        elif "summary" in response_data and "answer" not in response_data:
            response_data["answer"] = response_data["summary"]

        if "original_sources" in response_data and "sources" not in response_data:
            response_data["sources"] = response_data["original_sources"]

        # Ensure all required fields exist
        response_data.setdefault("answer", "Could not generate an answer. Please try again.")
        response_data.setdefault("sources", [])
        response_data.setdefault("tool_used", "RAG Pipeline")
        response_data.setdefault("rationale", "N/A")
        response_data.setdefault("follow_up_suggestions", [])
        response_data.setdefault("confidence_level", "N/A")

        logger.info(f"Final API response: {response_data}")
        return response_data

    except (RateLimitError, LocalRateLimitError) as e:
        msg = str(e)
        retry_after = None
        try:
            import re
            m = re.search(r"Please try again in ([0-9]+(?:\.[0-9]+)?)s", msg)
            if m:
                retry_after = float(m.group(1))
        except Exception:
            retry_after = None

        headers = {"Retry-After": str(int(retry_after))} if retry_after else None
        logger.warning(f"Rate limit error: {msg}")
        raise HTTPException(status_code=429, detail=msg, headers=headers)

    except Exception as e:
        logger.error(f"Error in chat_answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))