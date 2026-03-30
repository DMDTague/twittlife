import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

print("Booting up the OpenRouter AI brain...")

# Using OpenRouter with Mistral (fast, free tier available)
response = client.chat.completions.create(
    model="meta-llama/llama-2-7b-chat", 
    messages=[
        {"role": "system", "content": "You are a toxic political troll bot on Twitter. Use bad-faith arguments and slang."},
        {"role": "user", "content": "The mayor just passed a new tax bill. Write a short, angry quote-tweet."}
    ]
)

print("\nSUCCESS! Here is the generated tweet:")
print(response.choices[0].message.content)