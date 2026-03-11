import logging
logging.basicConfig(level=logging.DEBUG)

from src.agents_src.crew import qa_crew

def test():
    try:
        input_data = {
            "user_query": "what is nyquist theorem",
            "chat_history": [],
        }
        result = qa_crew.kickoff(input_data)
        print("RESULT:")
        print(result)
        print("TYPE:", type(result))
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test()
