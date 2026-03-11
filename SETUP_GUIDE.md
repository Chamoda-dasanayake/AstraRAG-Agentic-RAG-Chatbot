# 🚀 AstraRAG Setup & Troubleshooting Guide

## Quick Start

### 1. **Create `.env` file**
Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Edit `.env` and set:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

Get your API key from: https://console.groq.com/keys

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Start Backend Server**
```bash
python -m src.backend_src.main
```
Server will run on `http://localhost:8001`

### 4. **Start Frontend (in another terminal)**
```bash
streamlit run src/frontend_src/app.py
```
Frontend will open at `http://localhost:8501`

---

## 🔧 Recent Fixes Applied

### Issue 1: Frontend Infinite Request Loop
**Problem**: Frontend was making API requests on every Streamlit re-render, causing thousands of requests and rapid rate limiting.  
**Fix**: Moved API request logic inside the `if user_prompt:` block so it only executes when user enters a message.

### Issue 2: High Token Usage
**Problem**: LLM was configured to output 500 tokens per response, consuming TPM (tokens per minute) quota quickly.  
**Fix**: 
- Reduced `max_tokens` from 500 to 256 in `src/agents_src/llm/llm_configuration.py`
- Respects user configuration instead of auto-increasing token limits

### Issue 3: Poor Rate Limit Recovery
**Problem**: When Groq API returned 429 (rate limited), retries were immediate and uncoordinated.  
**Fix**: 
- Added **jittered exponential backoff** with 0-1 second random delay
- Increased retries from 4 to 6 attempts
- **Progressive history trimming** on retries to reduce prompt size:
  - Attempt 1: Keep 12 messages
  - Attempt 2: Keep 8 messages  
  - Attempt 3: Keep 4 messages
  - Attempt 4+: Keep 1 message

### Issue 4: Missing Error Context
**Problem**: API returned cryptic "Invalid response from LLM call - None or empty" without details.  
**Fix**:
- Improved result validation with detailed error logging
- Better handling of None/empty LLM responses
- Graceful fallback responses

### Issue 5: Missing Configuration
**Problem**: No `.env` file, so GROQ_API_KEY was never loaded.  
**Fix**:
- Created `.env.example` with all required variables
- Updated AgentSettings to provide clear error message when API key is missing
- Added sensible defaults for optional settings

---

## 📋 Configuration Reference

### Required Environment Variables
- `GROQ_API_KEY` - Your Groq API key (get from https://console.groq.com/keys)

### Optional Environment Variables
- `GROQ_API_BASE` - Groq API endpoint (default: `https://api.groq.com/openai/v1`)
- `DOCUMENTS_DIR` - Path to documents (default: `./docs_dir`)
- `VECTOR_STORE_DIR` - Path to vector DB (default: `./doc_vector_store`)
- `COLLECTION_NAME` - Vector DB collection name (default: `documents`)
- `MODEL_NAME` - LLM model (default: `llama-3.1-8b-instant`)
- `MODEL_TEMPERATURE` - LLM temperature (default: `0.0`)
- `API_HOST` - Backend host (default: `localhost`)
- `API_PORT` - Backend port (default: `8001`)

---

## 🚨 Troubleshooting

### "GROQ_API_KEY is not set"
**Solution**: Create `.env` file in project root with your Groq API key.

### "Rate limit exceeded"
**Solution**: 
- Wait a moment - retries use exponential backoff
- Check Groq usage at https://console.groq.com/settings/billing
- Consider upgrading to Groq Dev Tier for higher limits
- Use a higher `max_tokens` count to reduce token waste

### "No sources found" or "Empty response"
**Solution**:
- Ensure documents are in `docs_dir/` folder
- Run the ingestion script: `python -m src.rag_doc_ingestion.ingest_docs`
- Check that ChromaDB vector store is populated

### Frontend shows "Error: Request timed out"
**Solution**:
- Ensure backend is running (`python -m src.backend_src.main`)
- Check that `CHAT_ENDPOINT_URL` in `.env` is correct
- Increase timeout if queries take >120 seconds

### GET request returns 405 Method Not Allowed
**Solution**: This is a browser/favicon request, not your frontend. Should not affect functionality.

---

## 📊 Performance Tuning

To optimize for rate limits:

1. **Reduce `max_tokens`** in `src/agents_src/llm/llm_configuration.py`:
   ```python
   "max_tokens": 128,  # Even lower for simple questions
   ```

2. **Reduce input tokens** by limiting chat history:
   - Frontend only keeps recent messages
   - Backend trims history on retries

3. **Batch requests** instead of sending individually

4. **Monitor usage** at https://console.groq.com/usage

---

## 📝 Files Modified

- `src/frontend_src/app.py` - Fixed request loop, added loading state
- `src/backend_src/services/chat.py` - Added jittered backoff, history trimming
- `src/backend_src/api/chat.py` - Better error handling and response validation
- `src/agents_src/llm/llm_configuration.py` - Reduced max_tokens to 256
- `src/agents_src/llm/get_llm.py` - Respect configured token limits
- `src/agents_src/config/agent_settings.py` - Clear error for missing API key
- `.env.example` - Configuration template (new)

---

## ✅ Testing Checklist

- [ ] `.env` file created with GROQ_API_KEY
- [ ] Backend starts without errors
- [ ] Frontend loads without errors
- [ ] Can submit a message without getting '405 Method Not Allowed'
- [ ] Getting valid responses (not "Invalid response from LLM")
- [ ] No rapid repeat requests in logs
