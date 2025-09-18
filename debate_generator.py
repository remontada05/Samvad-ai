import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL_NAME = "mistralai/mistral-7b-instruct:free"

def generate_debate_round(topic, round_num):
    prompt = f"""You are simulating a structured debate on the topic: "{topic}".
Each round should contain:
🅰️ Debater A (Pro): gives an argument in favor.
🅱️ Debater B (Con): responds with a counterargument.

Present only Round {round_num} of the debate. Do not include summary.
Format:
Round {round_num}:
🅰️ Debater A (Pro): ...
🅱️ Debater B (Con): ...
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


def generate_summary(topic, debate_text):
    prompt = f"""Summarize the following debate on the topic: "{topic}".
Here is the debate content:
{debate_text}

Give a brief, neutral summary highlighting the main arguments from both sides."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


def main():
    print("🎯 Welcome to the AI Debate Generator (Claude via OpenRouter)!")
    topic = input("Enter the debate topic: ")
    try:
        rounds = int(input("Enter number of rounds: "))
    except ValueError:
        print("Invalid number. Using 3 rounds by default.")
        rounds = 3

    full_debate = ""
    for i in range(1, rounds + 1):
        print(f"\nGenerating Round {i}...")
        round_text = generate_debate_round(topic, i)
        print(round_text)
        full_debate += f"\n{round_text}\n"

    print("\n🧠 Generating Summary...")
    summary = generate_summary(topic, full_debate)
    print("\n📌 Debate Summary:")
    print(summary)

if __name__ == "__main__":
    main()
