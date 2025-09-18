from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL_NAME = "mistralai/mistral-7b-instruct:free"

app = Flask(__name__)

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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    # Split Pro and Con by the markers
    content = response.choices[0].message.content.strip()
    try:
        pro = content.split("🅰️ Debater A (Pro):")[1].split("🅱️ Debater B (Con):")[0].strip()
        con = content.split("🅱️ Debater B (Con):")[1].strip()
    except Exception:
        pro, con = content, ""
    return {"pro": pro, "con": con}

def generate_summary(topic, full_debate_text):
    prompt = f"""Summarize the following debate on the topic: "{topic}".
Here is the debate content:
{full_debate_text}

Give a brief, neutral summary highlighting the main arguments from both sides."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_debate", methods=["POST"])
def generate_debate():
    data = request.get_json()
    topic = data.get("topic", "")
    rounds = int(data.get("rounds", 1))
    
    full_debate_text = ""
    debate_rounds = []
    
    try:
        for i in range(1, rounds + 1):
            round_data = generate_debate_round(topic, i)
            full_debate_text += f"Round {i}:\n🅰️ Debater A (Pro): {round_data['pro']}\n🅱️ Debater B (Con): {round_data['con']}\n\n"
            debate_rounds.append(round_data)
        
        summary = generate_summary(topic, full_debate_text)
        
        return jsonify({"rounds": debate_rounds, "summary": summary})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
