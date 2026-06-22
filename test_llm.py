import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
from src.query_control.llm_helper import call_llm

try:
    res = call_llm(
        system_prompt="You are a helper. Output JSON.",
        user_prompt="Say hi in json",
        response_json=True
    )
    print("Result:", res)
except Exception as e:
    print("Error:", e)
