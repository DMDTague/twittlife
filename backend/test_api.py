import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

print("Booting up the Groq AI brain...")

# Swapped to the new, supported model!
response = client.chat.completions.create(
    model="llama-3.1-8b-instant", 
    messages=[
        {"role": "system", "content": "You are a toxic political troll bot on Twitter. Use bad-faith arguments and slang."},
        {"role": "user", "content": "The mayor just passed a new tax bill. Write a short, angry quote-tweet."}
    ]
)

print("\nSUCCESS! Here is the generated tweet:")
print(response.choices[0].message.content)