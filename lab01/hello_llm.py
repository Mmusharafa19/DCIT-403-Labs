"""Lab 1, Step 2: your first LLM call through LiteLLM.

Usage:
    python lab01/hello_llm.py          # temperature 0 (default)
    python lab01/hello_llm.py 1        # temperature 1
"""
import os
import sys

from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
TEMPERATURE = float(sys.argv[1]) if len(sys.argv) > 1 else 0

resp = completion(
    model=MODEL,                                   # 1. the model
    messages=[                                     # 2. the messages
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "In one sentence, what is an intelligent agent?"},
    ],
    temperature=TEMPERATURE,                       # 3. the settings
)
print(resp.choices[0].message.content)
print(resp.usage)
