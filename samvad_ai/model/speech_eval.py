"""
Speech Evaluator Model — Powered by Gemini AI
Analyzes and evaluates speech quality for debate performance
"""

import re
from typing import Dict, List, Any
from collections import Counter
from model.gemini_client import gemini


class SpeechEvaluator:
    def __init__(self):
        """Initialize the speech evaluator"""
        self.evaluation_criteria = {
            'clarity': {'weight': 0.25, 'description': 'Clarity of expression and communication'},
            'structure': {'weight': 0.25, 'description': 'Organization and logical flow'},
            'persuasiveness': {'weight': 0.25, 'description': 'Persuasive power and rhetorical skill'},
            'evidence': {'weight': 0.25, 'description': 'Use of evidence and supporting material'}
        }

        self.transition_words = [
            'however', 'furthermore', 'moreover', 'therefore', 'consequently',
            'additionally', 'nevertheless', 'meanwhile', 'subsequently', 'thus'
        ]

        self.evidence_indicators = [
            'study', 'research', 'data', 'statistics', 'according to',
            'evidence shows', 'research indicates', 'studies suggest'
        ]

        self.persuasive_words = [
            'compelling', 'crucial', 'essential', 'significant', 'important',
            'vital', 'critical', 'necessary', 'fundamental', 'key'
        ]

    def evaluate(self, speech_text: str, criteria: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate speech quality. Uses Gemini for rich feedback + heuristics for scores.
        """
        if criteria is None:
            criteria = list(self.evaluation_criteria.keys())

        # Always run heuristic analysis for numerical scores
        analysis = self._analyze_speech(speech_text)
        heuristic_scores = {}
        for criterion in criteria:
            if criterion in self.evaluation_criteria:
                heuristic_scores[criterion] = self._evaluate_criterion(analysis, criterion)

        overall_score = self._calculate_overall_score(heuristic_scores, criteria)

        # Try Gemini for rich qualitative feedback
        ai_feedback = None
        ai_suggestions = None
        if gemini.is_available:
            ai_result = self._evaluate_with_gemini(speech_text, criteria, heuristic_scores, overall_score)
            if ai_result:
                ai_feedback = ai_result.get('feedback', '')
                ai_suggestions = ai_result.get('suggestions', [])
                # Use Gemini scores if available (often more accurate)
                if 'scores' in ai_result:
                    for k, v in ai_result['scores'].items():
                        if k in heuristic_scores and isinstance(v, (int, float)):
                            heuristic_scores[k] = min(10, max(1, int(v)))
                    overall_score = self._calculate_overall_score(heuristic_scores, criteria)

        # Generate feedback
        feedback = ai_feedback or self._generate_feedback(analysis, heuristic_scores)

        return {
            'scores': heuristic_scores,
            'overall_score': overall_score,
            'feedback': feedback,
            'suggestions': ai_suggestions or self._generate_suggestions(heuristic_scores),
            'analysis': {
                'word_count': analysis['word_count'],
                'sentence_count': analysis['sentence_count'],
                'vocabulary_diversity': round(analysis['vocabulary_diversity'] * 100),
                'transitions_used': analysis['transitions'],
                'evidence_references': analysis['evidence_indicators']
            },
            'word_count': analysis['word_count'],
            'reading_time': round(analysis['estimated_reading_time'], 1),
            'ai_powered': ai_feedback is not None
        }

    def _evaluate_with_gemini(self, speech_text: str, criteria: List[str],
                               current_scores: Dict, overall: int) -> Dict:
        """Get rich evaluation from Gemini AI"""
        criteria_list = ", ".join(criteria)

        prompt = f"""You are an expert debate coach and speech evaluator. Analyze this speech and provide detailed feedback.

SPEECH TEXT:
"{speech_text}"

EVALUATION CRITERIA: {criteria_list}

Our heuristic analysis gave these scores: {current_scores} (overall: {overall}/10)

Provide your expert evaluation. Return ONLY a JSON object:
{{
    "scores": {{"clarity": 7, "structure": 8, "persuasiveness": 6, "evidence": 5}},
    "feedback": "2-3 paragraphs of detailed, constructive feedback covering strengths and areas for improvement. Be specific about what works and what doesn't.",
    "suggestions": [
        "Specific actionable suggestion 1",
        "Specific actionable suggestion 2",
        "Specific actionable suggestion 3",
        "Specific actionable suggestion 4"
    ]
}}

Only include criteria that were requested: {criteria_list}
Scores should be 1-10. Be fair but constructive."""

        try:
            return gemini.generate_json(prompt, temperature=0.6)
        except Exception as e:
            print(f"Gemini speech evaluation failed: {e}")
            return None

    def _analyze_speech(self, speech_text: str) -> Dict[str, Any]:
        """Analyze various aspects of the speech"""
        words = speech_text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', speech_text) if s.strip()]

        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'paragraphs': len(speech_text.split('\n\n')),
            'transitions': self._count_occurrences(speech_text, self.transition_words),
            'evidence_indicators': self._count_occurrences(speech_text, self.evidence_indicators),
            'persuasive_language': self._count_occurrences(speech_text, self.persuasive_words),
            'vocabulary_diversity': self._calc_vocab_diversity(words),
            'structure_analysis': self._analyze_structure(speech_text),
            'estimated_reading_time': len(words) / 150
        }

    def _count_occurrences(self, text: str, word_list: List[str]) -> int:
        """Count occurrences of words from a list in text"""
        text_lower = text.lower()
        return sum(text_lower.count(w) for w in word_list)

    def _calc_vocab_diversity(self, words: List[str]) -> float:
        """Calculate vocabulary diversity"""
        if not words:
            return 0
        return len(set(w.lower() for w in words)) / len(words)

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze structural elements"""
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        intro_words = ['today', 'first', 'begin', 'start', 'introduce', 'topic']
        conclusion_words = ['conclusion', 'finally', 'end', 'summary', 'therefore', 'thus']

        first_part = (paragraphs[0] if paragraphs else text[:200]).lower()
        last_part = (paragraphs[-1] if paragraphs else text[-200:]).lower()

        return {
            'has_introduction': any(w in first_part for w in intro_words),
            'has_conclusion': any(w in last_part for w in conclusion_words),
            'paragraph_count': len(paragraphs),
            'balanced_paragraphs': self._check_balance(paragraphs)
        }

    def _check_balance(self, paragraphs: List[str]) -> bool:
        """Check if paragraphs are balanced in length"""
        if len(paragraphs) < 2:
            return False
        lengths = [len(p.split()) for p in paragraphs if p.strip()]
        if not lengths:
            return False
        avg = sum(lengths) / len(lengths)
        if avg == 0:
            return False
        return all(abs(l - avg) / avg < 0.5 for l in lengths)

    def _evaluate_criterion(self, analysis: Dict, criterion: str) -> int:
        """Score a criterion out of 10"""
        evaluators = {
            'clarity': self._score_clarity,
            'structure': self._score_structure,
            'persuasiveness': self._score_persuasiveness,
            'evidence': self._score_evidence
        }
        return evaluators.get(criterion, lambda a: 7)(analysis)

    def _score_clarity(self, analysis: Dict) -> int:
        score = 5
        avg_len = analysis['avg_sentence_length']
        if 15 <= avg_len <= 20: score += 2
        elif 10 <= avg_len <= 25: score += 1
        if analysis['vocabulary_diversity'] > 0.6: score += 2
        elif analysis['vocabulary_diversity'] > 0.4: score += 1
        if analysis['transitions'] >= 3: score += 1
        return min(10, max(1, score))

    def _score_structure(self, analysis: Dict) -> int:
        score = 5
        s = analysis['structure_analysis']
        if s['has_introduction']: score += 2
        if s['has_conclusion']: score += 2
        if s['paragraph_count'] >= 3: score += 1
        if s['balanced_paragraphs']: score += 1
        return min(10, max(1, score))

    def _score_persuasiveness(self, analysis: Dict) -> int:
        score = 5
        if analysis['persuasive_language'] >= 5: score += 2
        elif analysis['persuasive_language'] >= 3: score += 1
        if analysis['evidence_indicators'] >= 3: score += 2
        elif analysis['evidence_indicators'] >= 1: score += 1
        if analysis['word_count'] >= 300: score += 1
        return min(10, max(1, score))

    def _score_evidence(self, analysis: Dict) -> int:
        score = 5
        ev = analysis['evidence_indicators']
        if ev >= 5: score += 3
        elif ev >= 3: score += 2
        elif ev >= 1: score += 1
        if analysis['vocabulary_diversity'] > 0.5: score += 1
        return min(10, max(1, score))

    def _calculate_overall_score(self, scores: Dict[str, int], criteria: List[str]) -> int:
        if not scores:
            return 7
        total_weight = sum(self.evaluation_criteria[c]['weight'] for c in criteria if c in self.evaluation_criteria)
        if total_weight == 0:
            return sum(scores.values()) // len(scores)
        weighted = sum(
            scores[c] * self.evaluation_criteria[c]['weight']
            for c in criteria if c in scores and c in self.evaluation_criteria
        )
        return round(weighted / total_weight)

    def _generate_feedback(self, analysis: Dict, scores: Dict[str, int]) -> str:
        """Generate rule-based feedback"""
        parts = []
        overall = sum(scores.values()) / len(scores) if scores else 7

        if overall >= 8: parts.append("Excellent speech with strong performance across multiple areas.")
        elif overall >= 6: parts.append("Good speech with solid fundamentals. A few areas could be enhanced.")
        else: parts.append("Your speech shows potential with room for improvement.")

        if 'clarity' in scores:
            if scores['clarity'] < 6: parts.append("Focus on shorter, clearer sentences and better transitions.")
            elif scores['clarity'] >= 8: parts.append("Your clarity and communication style are excellent.")

        if 'structure' in scores:
            if scores['structure'] < 6: parts.append("Strengthen your structure with a clear introduction and conclusion.")
            elif scores['structure'] >= 8: parts.append("Your speech structure is well-organized.")

        if 'persuasiveness' in scores:
            if scores['persuasiveness'] < 6: parts.append("Use more persuasive language and stronger arguments.")
            elif scores['persuasiveness'] >= 8: parts.append("Your persuasive techniques are highly effective.")

        if 'evidence' in scores:
            if scores['evidence'] < 6: parts.append("Include more evidence, data, and credible sources.")
            elif scores['evidence'] >= 8: parts.append("Your use of evidence is impressive.")

        return " ".join(parts)

    def _generate_suggestions(self, scores: Dict[str, int]) -> List[str]:
        """Generate improvement suggestions based on scores"""
        suggestions = []
        if scores.get('clarity', 10) < 7:
            suggestions.append("Use shorter sentences (15-20 words) for better clarity")
        if scores.get('structure', 10) < 7:
            suggestions.append("Add a clear introduction and conclusion to your speech")
        if scores.get('persuasiveness', 10) < 7:
            suggestions.append("Include more persuasive language like 'crucial', 'essential', 'compelling'")
        if scores.get('evidence', 10) < 7:
            suggestions.append("Reference specific studies, statistics, or expert opinions")
        if not suggestions:
            suggestions.append("Your speech is strong! Try adding more varied vocabulary for extra impact")
        return suggestions