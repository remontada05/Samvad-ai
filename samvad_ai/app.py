"""
Samvad AI — Your AI-Powered Debate Companion
Built with Flask + Google Gemini AI
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__)

# Initialize AI models
from model.argument_model import ArgumentGenerator
from model.rebuttal_model import RebuttalAssistant
from model.speech_eval import SpeechEvaluator
from model.judge_panel import JudgePanel
from utils.bias_detector import BiasDetector

argument_gen = ArgumentGenerator()
rebuttal_assistant = RebuttalAssistant()
speech_evaluator = SpeechEvaluator()
judge_panel = JudgePanel()
bias_detector = BiasDetector()


# ─── Page Routes ─────────────────────────────────────────────────

@app.route('/')
def index():
    """Homepage with premium landing page"""
    return render_template('index.html')

@app.route('/argument')
def argument_page():
    """Argument Generator Page"""
    return render_template('argument.html')

@app.route('/rebuttal')
def rebuttal_page():
    """Rebuttal Assistant Page"""
    return render_template('rebuttal.html')

@app.route('/speech')
def speech_page():
    """Speech Evaluator Page"""
    return render_template('speech.html')

@app.route('/judge')
def judge_page():
    """Judge Panel Page"""
    return render_template('judge.html')

@app.route('/debate')
def debate_page():
    """Live AI Debate Page"""
    return render_template('debate.html')


# ─── API Endpoints ───────────────────────────────────────────────

@app.route('/api/generate-argument', methods=['POST'])
def generate_argument():
    """Generate arguments for a given topic"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        position = data.get('position', 'for')

        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        arguments = argument_gen.generate(topic, position)
        return jsonify({
            'success': True,
            'arguments': arguments,
            'topic': topic,
            'position': position
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-rebuttal', methods=['POST'])
def generate_rebuttal():
    """Generate intelligent rebuttals"""
    try:
        data = request.get_json()
        opponent_argument = data.get('argument', '').strip()
        context = data.get('context', '').strip()

        if not opponent_argument:
            return jsonify({'error': 'Opponent argument is required'}), 400

        result = rebuttal_assistant.generate(opponent_argument, context)
        return jsonify({
            'success': True,
            'rebuttal': result.get('rebuttal', ''),
            'strategy': result.get('strategy', ''),
            'strategy_explanation': result.get('strategy_explanation', ''),
            'strength': result.get('strength', 7),
            'weaknesses_found': result.get('weaknesses_found', []),
            'original_argument': opponent_argument,
            'ai_powered': result.get('ai_powered', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluate-speech', methods=['POST'])
def evaluate_speech():
    """Evaluate speech quality with AI feedback"""
    try:
        data = request.get_json()
        speech_text = data.get('speech', '').strip()
        criteria = data.get('criteria', ['clarity', 'structure', 'persuasiveness'])

        if not speech_text:
            return jsonify({'error': 'Speech text is required'}), 400

        evaluation = speech_evaluator.evaluate(speech_text, criteria)
        return jsonify({
            'success': True,
            'evaluation': evaluation,
            'overall_score': evaluation.get('overall_score', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/judge-debate', methods=['POST'])
def judge_debate():
    """Get AI judge panel verdict"""
    try:
        data = request.get_json()
        debate_data = data.get('debate', {})

        if not debate_data:
            return jsonify({'error': 'Debate data is required'}), 400

        # Check for bias
        bias_check = bias_detector.check_bias(debate_data)

        # Get judge panel scores
        scores = judge_panel.evaluate(debate_data)

        return jsonify({
            'success': True,
            'scores': scores,
            'bias_check': bias_check,
            'winner': judge_panel.determine_winner(scores)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/debate-respond', methods=['POST'])
def debate_respond():
    """AI debate opponent responds to user's argument"""
    try:
        data = request.get_json()
        motion = data.get('motion', '').strip()
        user_argument = data.get('user_argument', '').strip()
        ai_position = data.get('ai_position', 'opposition')
        history = data.get('history', [])

        if not motion or not user_argument:
            return jsonify({'error': 'Motion and argument are required'}), 400

        from model.gemini_client import gemini

        if gemini.is_available:
            history_text = ""
            if history:
                history_text = "\n\nDEBATE SO FAR:\n"
                for entry in history[-6:]:  # Last 6 exchanges
                    history_text += f"- {entry.get('role', 'unknown')}: {entry.get('text', '')}\n"

            prompt = f"""You are a skilled debate opponent arguing as the {ai_position} in a formal debate.

MOTION: "{motion}"
YOUR POSITION: {ai_position.upper()}{history_text}

YOUR OPPONENT JUST SAID:
"{user_argument}"

Respond as the {ai_position} debater. Your response should:
1. Directly address and rebut their specific points
2. Present your own counter-arguments
3. Be persuasive, logical, and well-structured
4. Be 3-5 sentences long
5. Stay in character as a formal debater

Respond with ONLY your debate argument, no meta-commentary."""

            response = gemini.generate(prompt, temperature=0.8)
            if response:
                return jsonify({
                    'success': True,
                    'response': response,
                    'ai_position': ai_position
                })

        # Fallback
        return jsonify({
            'success': True,
            'response': f"While my opponent raises interesting points about the motion, I must respectfully disagree. The evidence clearly shows that the {ai_position} position is stronger, as it considers the broader implications and long-term consequences that have been overlooked. We must look beyond surface-level arguments to understand the true impact of this motion.",
            'ai_position': ai_position
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/daily-motion')
def get_daily_motion():
    """Get today's debate motion"""
    try:
        motions_path = os.path.join(os.path.dirname(__file__), 'data', 'motions.json')
        with open(motions_path, 'r') as f:
            motions = json.load(f)

        day_of_year = datetime.datetime.now().timetuple().tm_yday
        motion_index = day_of_year % len(motions['motions'])

        return jsonify({
            'success': True,
            'motion': motions['motions'][motion_index],
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'motion': 'This House believes that artificial intelligence will fundamentally change the nature of human debate and discourse.',
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        })


# ─── Error Handlers ──────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    print("\n🚀 Samvad AI is starting...")
    print("🌐 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host='0.0.0.0', port=5000)