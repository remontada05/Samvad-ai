"""
Judge Panel Model — Powered by Gemini AI
Provides AI judge evaluation and scoring for debates with distinct judge personalities
"""

import random
from typing import Dict, List, Any
from model.gemini_client import gemini


class JudgePanel:
    def __init__(self):
        """Initialize the judge panel with scoring criteria and judge profiles"""
        self.scoring_criteria = {
            'content': {'weight': 0.3, 'description': 'Quality and relevance of arguments'},
            'delivery': {'weight': 0.2, 'description': 'Speaking style and presentation'},
            'rebuttal': {'weight': 0.2, 'description': 'Response to opponent arguments'},
            'evidence': {'weight': 0.15, 'description': 'Use of supporting material'},
            'organization': {'weight': 0.15, 'description': 'Structure and flow'}
        }

        self.judge_profiles = {
            'academic': {
                'name': 'Prof. Sharma',
                'title': 'Academic Judge',
                'personality': 'Rigorous, evidence-focused, values citations and logical structure',
                'avatar': '🎓',
                'strictness': 0.8,
                'preferences': ['evidence', 'organization']
            },
            'practical': {
                'name': 'Justice Mehta',
                'title': 'Practical Judge',
                'personality': 'Real-world focused, values practical impact and clear communication',
                'avatar': '⚖️',
                'strictness': 0.6,
                'preferences': ['content', 'delivery']
            },
            'balanced': {
                'name': 'Dr. Patel',
                'title': 'Balanced Judge',
                'personality': 'Fair and comprehensive, weighs all criteria equally',
                'avatar': '📋',
                'strictness': 0.7,
                'preferences': ['content', 'rebuttal']
            }
        }

    def evaluate(self, debate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a debate from both sides"""
        motion = debate_data.get('motion', '')
        proposition = debate_data.get('proposition', '')
        opposition = debate_data.get('opposition', '')

        # Try Gemini for intelligent judging
        if gemini.is_available:
            ai_result = self._evaluate_with_gemini(motion, proposition, opposition)
            if ai_result:
                return ai_result

        # Fallback to heuristic judging
        return self._evaluate_fallback(motion, proposition, opposition)

    def _evaluate_with_gemini(self, motion: str, proposition: str, opposition: str) -> Dict:
        """Evaluate using Gemini AI with distinct judge personalities"""
        prompt = f"""You are simulating a panel of 3 expert debate judges evaluating a formal debate. Each judge has a distinct personality and scoring tendency.

DEBATE MOTION: "{motion}"

PROPOSITION ARGUMENT:
"{proposition}"

OPPOSITION ARGUMENT:
"{opposition}"

THE THREE JUDGES:
1. Prof. Sharma (Academic) — Rigorous, values evidence and logical structure, strict scorer
2. Justice Mehta (Practical) — Values real-world impact and clear communication, moderate scorer
3. Dr. Patel (Balanced) — Fair, comprehensive evaluator, weighs all criteria equally

Each judge scores BOTH sides on these criteria (1-10 each):
- content: Quality and relevance of arguments
- delivery: Speaking style and presentation quality
- rebuttal: How well they address opponent's points
- evidence: Use of data, examples, and supporting material
- organization: Structure and logical flow

Return ONLY a JSON object:
{{
    "judges": {{
        "academic": {{
            "proposition": {{"content": 7, "delivery": 6, "rebuttal": 7, "evidence": 8, "organization": 7}},
            "opposition": {{"content": 6, "delivery": 7, "rebuttal": 6, "evidence": 5, "organization": 6}},
            "comments": "Prof. Sharma's specific feedback about the debate..."
        }},
        "practical": {{
            "proposition": {{"content": 7, "delivery": 7, "rebuttal": 6, "evidence": 6, "organization": 7}},
            "opposition": {{"content": 7, "delivery": 6, "rebuttal": 7, "evidence": 6, "organization": 6}},
            "comments": "Justice Mehta's specific feedback..."
        }},
        "balanced": {{
            "proposition": {{"content": 7, "delivery": 7, "rebuttal": 7, "evidence": 7, "organization": 7}},
            "opposition": {{"content": 7, "delivery": 7, "rebuttal": 7, "evidence": 7, "organization": 7}},
            "comments": "Dr. Patel's specific feedback..."
        }}
    }},
    "overall_feedback": "2-3 paragraph detailed analysis of the debate, highlighting key moments, strongest arguments from each side, and areas for improvement.",
    "key_moments": ["Notable moment 1", "Notable moment 2", "Notable moment 3"]
}}

Be fair, analytical, and provide constructive feedback. Score realistically — not everything deserves a high score."""

        try:
            result = gemini.generate_json(prompt, max_tokens=3000, temperature=0.6)
            if result and 'judges' in result:
                return self._process_gemini_result(result, motion)
        except Exception as e:
            print(f"Gemini judge evaluation failed: {e}")

        return None

    def _process_gemini_result(self, result: Dict, motion: str) -> Dict:
        """Process Gemini result into standardized format"""
        judges = result.get('judges', {})

        # Calculate final averaged scores
        final_scores = {'proposition': {}, 'opposition': {}}
        individual_judges = {}

        for judge_type in ['academic', 'practical', 'balanced']:
            judge_data = judges.get(judge_type, {})
            profile = self.judge_profiles[judge_type]

            individual_judges[judge_type] = {
                'judge_name': profile['name'],
                'title': profile['title'],
                'avatar': profile['avatar'],
                'personality': profile['personality'],
                'proposition': judge_data.get('proposition', self._default_scores()),
                'opposition': judge_data.get('opposition', self._default_scores()),
                'comments': judge_data.get('comments', 'No comments available.')
            }

        # Average scores across judges
        for side in ['proposition', 'opposition']:
            for criterion in self.scoring_criteria:
                scores = []
                for judge_type in judges:
                    judge = judges[judge_type]
                    side_scores = judge.get(side, {})
                    if criterion in side_scores:
                        scores.append(side_scores[criterion])
                final_scores[side][criterion] = round(sum(scores) / len(scores)) if scores else 7

            final_scores[side]['total'] = sum(
                final_scores[side].get(c, 7) for c in self.scoring_criteria
            )

        return {
            'proposition': final_scores['proposition'],
            'opposition': final_scores['opposition'],
            'individual_judges': individual_judges,
            'feedback': result.get('overall_feedback', 'Both sides presented reasonable arguments.'),
            'key_moments': result.get('key_moments', []),
            'motion': motion,
            'ai_powered': True
        }

    def _default_scores(self):
        return {c: 7 for c in self.scoring_criteria}

    def _evaluate_fallback(self, motion: str, proposition: str, opposition: str) -> Dict:
        """Fallback heuristic-based evaluation"""
        prop_analysis = self._analyze_speech(proposition)
        opp_analysis = self._analyze_speech(opposition)

        judge_scores = {}
        for judge_type, profile in self.judge_profiles.items():
            judge_scores[judge_type] = {
                'judge_name': profile['name'],
                'title': profile['title'],
                'avatar': profile['avatar'],
                'personality': profile['personality'],
                'proposition': self._score_speech(prop_analysis, profile),
                'opposition': self._score_speech(opp_analysis, profile),
                'comments': self._generate_comment(prop_analysis, opp_analysis, profile)
            }

        # Calculate final scores
        final_scores = {'proposition': {}, 'opposition': {}}
        for side in ['proposition', 'opposition']:
            for criterion in self.scoring_criteria:
                scores = [judge_scores[j][side].get(criterion, 7) for j in judge_scores]
                final_scores[side][criterion] = round(sum(scores) / len(scores))
            final_scores[side]['total'] = sum(final_scores[side][c] for c in self.scoring_criteria)

        return {
            'proposition': final_scores['proposition'],
            'opposition': final_scores['opposition'],
            'individual_judges': judge_scores,
            'feedback': self._generate_overall_feedback(final_scores),
            'key_moments': [],
            'motion': motion,
            'ai_powered': False
        }

    def _analyze_speech(self, speech: str) -> Dict:
        """Analyze a speech for scoring"""
        words = speech.split()
        sentences = [s for s in speech.split('.') if s.strip()]
        evidence_markers = ['study', 'research', 'data', 'statistics', 'according to', 'evidence']
        rebuttal_markers = ['however', 'but', 'although', 'despite', 'nevertheless', 'opponent']
        org_markers = ['first', 'second', 'third', 'firstly', 'furthermore', 'moreover', 'finally', 'conclusion']
        persuasive = ['clearly', 'obviously', 'crucial', 'essential', 'vital', 'important', 'significant']

        speech_lower = speech.lower()
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'evidence_count': sum(speech_lower.count(m) for m in evidence_markers),
            'rebuttal_markers': sum(speech_lower.count(m) for m in rebuttal_markers),
            'organization_markers': sum(1 for m in org_markers if m in speech_lower),
            'persuasive_language': sum(speech_lower.count(m) for m in persuasive)
        }

    def _score_speech(self, analysis: Dict, profile: Dict) -> Dict[str, int]:
        """Score a speech based on judge profile"""
        base = 6
        strictness = profile['strictness']
        prefs = profile['preferences']

        scores = {}
        scores['content'] = min(10, max(1, int((base + (2 if analysis['word_count'] >= 200 else 0) + (1 if analysis['organization_markers'] >= 2 else 0)) * strictness)))
        scores['delivery'] = min(10, max(1, int((base + (2 if analysis['persuasive_language'] >= 3 else 1 if analysis['persuasive_language'] >= 1 else 0)) * strictness)))
        scores['rebuttal'] = min(10, max(1, int((base + (2 if analysis['rebuttal_markers'] >= 3 else 1 if analysis['rebuttal_markers'] >= 1 else 0)) * strictness)))
        scores['evidence'] = min(10, max(1, int((base + (3 if analysis['evidence_count'] >= 5 else 2 if analysis['evidence_count'] >= 3 else 1 if analysis['evidence_count'] >= 1 else 0)) * strictness)))
        scores['organization'] = min(10, max(1, int((base + (2 if analysis['organization_markers'] >= 3 else 1 if analysis['organization_markers'] >= 1 else 0)) * strictness)))

        for pref in prefs:
            if pref in scores:
                scores[pref] = min(10, scores[pref] + 1)

        scores['total'] = sum(scores[c] for c in self.scoring_criteria)
        return scores

    def _generate_comment(self, prop: Dict, opp: Dict, profile: Dict) -> str:
        """Generate judge-specific comments"""
        name = profile['name']
        if profile['preferences'][0] == 'evidence':
            if prop['evidence_count'] > opp['evidence_count']:
                return f"{name}: Proposition provided stronger evidence support. Both sides should continue to strengthen their data citations."
            else:
                return f"{name}: Opposition had better evidence backing. Proposition needs to bolster their supporting data."
        elif profile['preferences'][0] == 'content':
            return f"{name}: Looking for practical real-world applications. Both sides presented relevant arguments with varying levels of practical grounding."
        else:
            return f"{name}: Evaluating overall debate performance. Both sides showed competence, with room for improvement in specific areas."

    def _generate_overall_feedback(self, scores: Dict) -> str:
        """Generate overall feedback"""
        prop_total = scores['proposition']['total']
        opp_total = scores['opposition']['total']

        parts = []
        diff = abs(prop_total - opp_total)
        if diff <= 2:
            parts.append("This was a very close and competitive debate with strong performances from both sides.")
        elif prop_total > opp_total:
            parts.append("The proposition presented a stronger overall case, winning on multiple scoring criteria.")
        else:
            parts.append("The opposition delivered a more compelling set of arguments and secured the victory.")

        parts.append("Both sides could strengthen their arguments with additional evidence and more direct engagement with opposing points.")
        return " ".join(parts)

    def determine_winner(self, scores: Dict[str, Any]) -> str:
        """Determine the winner based on final scores"""
        prop_total = scores.get('proposition', {}).get('total', 0)
        opp_total = scores.get('opposition', {}).get('total', 0)

        if prop_total > opp_total:
            return "Proposition"
        elif opp_total > prop_total:
            return "Opposition"
        else:
            return "Draw"