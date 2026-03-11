import logging
from fastapi import APIRouter, HTTPException
from litellm.exceptions import RateLimitError
from src.backend_src.services.chat import LocalRateLimitError
from pydantic import BaseModel
from typing import List
from src.backend_src.services.chat import get_answer

# -------------------- Logging setup --------------------
logger = logging.getLogger(__name__)

# -------------------- FastAPI Router --------------------
router = APIRouter()

# -------------------- Request Models --------------------
class ChatMessage(BaseModel): 
    role: str
    content: str

class ChatHistoryRequest(BaseModel):
    chat_history: List[ChatMessage]

# -------------------- API Endpoint --------------------
@router.post("/chat/answer")
def chat_answer(request: ChatHistoryRequest):
    logger.info(f"Received API request with chat_history: {request.chat_history}")

    # 1️⃣ Validate input to avoid empty history errors
    if not request.chat_history:
        raise HTTPException(
            status_code=400,
            detail="chat_history cannot be empty. Add at least one user message."
        )

    try:
        # Convert Pydantic objects to plain dicts
        chat_history = [msg.dict() for msg in request.chat_history]

        # 2️⃣ Call your backend chat logic
        result = get_answer(chat_history)

        # Handle the result - it should be a dict with answer, sources, tool_used, rationale
        if not result:
            raise ValueError("No response from crew - result is empty or None")
        
        if isinstance(result, dict):
            response_data = result
        else:
            # If it's an object with as_dict or to_dict methods, try those
            if hasattr(result, 'as_dict'):
                response_data = result.as_dict()
            elif hasattr(result, 'to_dict'):
                response_data = result.to_dict()
            elif hasattr(result, 'dict'):
                response_data = result.dict()
            else:
                response_data = {"answer": str(result), "sources": [], "tool_used": "N/A", "rationale": "N/A"}

        # Validate response has required fields
        required_fields = ["answer", "sources", "tool_used", "rationale"]
        for field in required_fields:
            if field not in response_data or response_data[field] is None:
                logger.warning(f"Missing or None field '{field}' in response: {response_data}")
                if field == "answer":
                    response_data["answer"] = "Could not generate an answer. Please try again."
                else:
                    response_data[field] = [] if field == "sources" else "N/A"

        logger.info(f"API response: {response_data}")
        return response_data

    # -------------------- Rate Limit Handling --------------------
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
        logger.warning(f"Rate limit error returned to client: {msg}")
        raise HTTPException(status_code=429, detail=msg, headers=headers)

    # -------------------- General Error Handling --------------------
    except Exception as e:
        logger.error(msg=f"Error in chat_answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))