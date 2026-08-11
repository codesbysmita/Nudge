import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["FEATHERLESS_API_KEY"],
    base_url="https://api.featherless.ai/v1"
)

response = client.chat.completions.create(
    model="MiniMaxAI/MiniMax-M2.5",
    messages=[
        {
            "role": "user",
            "content": "Say hello to Nudge in one sentence."
        }
    ]
)

print(response.choices[0].message.content)