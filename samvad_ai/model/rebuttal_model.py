"""
Rebuttal Assistant Model — Powered by Gemini AI
Generates intelligent counter-arguments and rebuttals
"""

import re
import random
from typing import List, Dict, Any
from collections import Counter
from model.gemini_client import gemini


class RebuttalAssistant:
    def __init__(self):
        """Initialize the rebuttal assistant"""
        self.strategies = [
            'challenge_evidence', 'alternative_interpretation', 'unintended_consequences',
            'false_dichotomy', 'scope_limitation', 'precedent_analysis', 'cost_benefit_analysis'
        ]

    def generate(self, opponent_argument: str, context: str = "") -> Dict[str, Any]:
        """
        Generate a rebuttal for the opponent's argument.
        Uses Gemini AI when available, falls back to rule-based approach.
        
        Returns dict with 'rebuttal', 'strategy', and 'strength' keys.
        """
        # Try Gemini first
        if gemini.is_available:
            ai_result = self._generate_with_gemini(opponent_argument, context)
            if ai_result:
                return ai_result

        # Fallback to rule-based
        return self._generate_fallback(opponent_argument, context)

    def _generate_with_gemini(self, opponent_argument: str, context: str) -> Dict[str, Any]:
        """Generate rebuttal using Gemini AI"""
        context_section = f'\nDebate context: "{context}"' if context else ""

        prompt = f"""You are a master debater and argumentation expert. Craft a powerful, strategic rebuttal to the following opponent argument:

Opponent's Argument: "{opponent_argument}"{context_section}

Analyze the argument for weaknesses, then construct a devastating counter-argument.

Return ONLY a JSON object in this exact format:
{{
    "rebuttal": "Your 3-5 sentence rebuttal here. Be specific, logical, and persuasive.",
    "strategy": "One of: challenge_evidence, alternative_interpretation, unintended_consequences, false_dichotomy, scope_limitation, precedent_analysis, cost_benefit_analysis",
    "strategy_explanation": "Brief 1-sentence explanation of why this strategy was chosen",
    "strength": 8,
    "weaknesses_found": ["weakness 1", "weakness 2"]
}}

The strength should be a number from 1-10 indicating how strong the rebuttal is."""

        try:
            result = gemini.generate_json(prompt, temperature=0.7)
            if result and 'rebuttal' in result:
                return {
                    'rebuttal': result['rebuttal'],
                    'strategy': result.get('strategy', 'alternative_interpretation'),
                    'strategy_explanation': result.get('strategy_explanation', ''),
                    'strength': result.get('strength', 7),
                    'weaknesses_found': result.get('weaknesses_found', []),
                    'ai_powered': True
                }
        except Exception as e:
            print(f"Gemini rebuttal generation failed: {e}")

        return None

    def _generate_fallback(self, opponent_argument: str, context: str) -> Dict[str, Any]:
        """Generate rebuttal using rule-based approach"""
        analysis = self._analyze_argument(opponent_argument)
        strategy = self._select_strategy(analysis)
        rebuttal_text = self._build_rebuttal(opponent_argument, strategy, analysis)

        return {
            'rebuttal': rebuttal_text,
            'strategy': strategy,
            'strategy_explanation': f'Selected based on argument structure analysis',
            'strength': 6,
            'weaknesses_found': [],
            'ai_powered': False
        }

    def _analyze_argument(self, argument: str) -> Dict[str, Any]:
        """Analyze the structure and content of the opponent's argument"""
        words = argument.lower().split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', argument) if s.strip()]

        evidence_words = ['study', 'research', 'data', 'statistics', 'evidence', 'proof', 'survey', 'analysis']
        emotional_words = ['terrible', 'wonderful', 'devastating', 'amazing', 'horrible', 'fantastic', 'outrageous']

        return {
            'length': len(words),
            'sentence_count': len(sentences),
            'evidence_words': sum(1 for w in words if w in evidence_words),
            'emotional_language': any(w in words for w in emotional_words),
            'has_absolutes': any(w in words for w in ['always', 'never', 'all', 'none', 'every']),
            'has_causation': any(w in argument.lower() for w in ['because', 'since', 'therefore', 'thus']),
            'key_terms': self._extract_key_terms(argument)
        }

    def _extract_key_terms(self, argument: str) -> List[str]:
        """Extract key terms from the argument"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', argument.lower())
        common = {'that', 'this', 'with', 'from', 'they', 'have', 'will', 'been', 'their', 'said', 'each', 'which'}
        filtered = [w for w in words if w not in common]
        return [term for term, _ in Counter(filtered).most_common(5)]

    def _select_strategy(self, analysis: Dict) -> str:
        """Select the best rebuttal strategy based on analysis"""
        if analysis['evidence_words'] == 0:
            return 'challenge_evidence'
        elif analysis['has_absolutes']:
            return 'scope_limitation'
        elif analysis['emotional_language']:
            return 'alternative_interpretation'
        elif analysis['has_causation']:
            return 'unintended_consequences'
        else:
            return random.choice(self.strategies)

    def _build_rebuttal(self, argument: str, strategy: str, analysis: Dict) -> str:
        """Build a rebuttal based on the selected strategy"""
        topic = analysis['key_terms'][0] if analysis['key_terms'] else "this issue"

        strategy_rebuttals = {
            'challenge_evidence': f"While the opponent makes claims about {topic}, they provide insufficient evidence to support such a broad conclusion. Without rigorous data or credible sources, this argument remains speculative. A more comprehensive analysis of the available research suggests alternative conclusions.",
            'alternative_interpretation': f"The opponent's interpretation of {topic} overlooks important contextual factors. When examined from different perspectives, the same evidence can lead to significantly different conclusions. A more nuanced view reveals the situation is far more complex than presented.",
            'unintended_consequences': f"The opponent fails to consider that their proposed approach to {topic} could lead to significant unintended consequences. While the stated benefits sound appealing, practical implementation could create outcomes that directly contradict the intended goals.",
            'false_dichotomy': f"The opponent presents this as a simple either/or choice regarding {topic}, but this is a false dichotomy. Nuanced approaches exist that address concerns from multiple perspectives, and graduated solutions could better serve all stakeholders.",
            'scope_limitation': f"While the opponent's reasoning about {topic} may hold in specific circumstances, it fails when applied to diverse situations and broader contexts. This narrow scope ignores the full range of potential implications.",
            'precedent_analysis': f"Historical precedent regarding approaches similar to {topic} shows mixed results at best. When comparable policies were implemented, significant challenges emerged, suggesting caution is warranted.",
            'cost_benefit_analysis': f"The opponent emphasizes potential advantages of {topic} but ignores significant drawbacks and resource requirements. A balanced cost-benefit analysis reveals the trade-offs may not justify the proposed approach."
        }

        return strategy_rebuttals.get(strategy, f"The opponent's argument about {topic} has merit but fails to consider important counterarguments and alternative perspectives.")