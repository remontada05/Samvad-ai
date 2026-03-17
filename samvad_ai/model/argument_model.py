"""
Argument Generator Model — Powered by Gemini AI
Generates compelling, structured arguments for debate topics
"""

import random
import json
from typing import List, Dict, Any
from model.gemini_client import gemini


class ArgumentGenerator:
    def __init__(self):
        """Initialize the argument generator"""
        # Fallback templates (used when Gemini is unavailable)
        self.fallback_templates = {
            'economic': [
                "From an economic perspective, {topic} would {effect} because {reason}.",
                "The financial implications of {topic} suggest that {outcome}.",
                "Economic data shows that {topic} leads to {result}."
            ],
            'social': [
                "Socially, {topic} would {impact} communities by {mechanism}.",
                "The social fabric of society would be {effect} through {topic}.",
                "From a societal standpoint, {topic} represents {significance}."
            ],
            'ethical': [
                "Ethically speaking, {topic} raises important considerations about {issue}.",
                "The moral implications of {topic} center on {principle}.",
                "From an ethical framework, {topic} {judgment}."
            ],
            'practical': [
                "In practical terms, {topic} would {result} because {logic}.",
                "The implementation of {topic} would {outcome}.",
                "Practically speaking, {topic} offers {benefit}."
            ]
        }

        self.supporting_phrases = {
            'for': {
                'effect': ['significantly benefit society', 'create positive change', 'improve outcomes'],
                'impact': ['strengthen', 'enhance', 'positively transform'],
                'result': ['increased prosperity', 'better quality of life', 'enhanced opportunities'],
                'judgment': ['represents progress', 'aligns with justice', 'promotes fairness'],
                'reason': ['it addresses fundamental societal needs', 'evidence supports its effectiveness'],
                'outcome': ['positive societal transformation is likely', 'communities would benefit significantly'],
                'mechanism': ['creating new opportunities for participation', 'fostering collaboration'],
                'significance': ['a crucial step toward progress', 'an opportunity for positive change'],
                'issue': ['individual autonomy and fairness', 'rights and freedoms'],
                'principle': ['the balance between individual and collective good', 'human dignity'],
                'logic': ['it addresses root causes rather than symptoms', 'it builds on proven models'],
                'benefit': ['clear advantages for all stakeholders', 'sustainable solutions']
            },
            'against': {
                'effect': ['harm society', 'create negative consequences', 'worsen conditions'],
                'impact': ['weaken', 'undermine', 'negatively affect'],
                'result': ['economic instability', 'social disruption', 'reduced opportunities'],
                'judgment': ['violates principles', 'creates injustice', 'promotes inequality'],
                'reason': ['it may create unintended consequences', 'the costs outweigh the benefits'],
                'outcome': ['negative consequences may emerge', 'social divisions could deepen'],
                'mechanism': ['disrupting existing structures', 'creating new inequalities'],
                'significance': ['a concerning departure from stability', 'a risky experiment'],
                'issue': ['individual autonomy and choice', 'responsibility and accountability'],
                'principle': ['the importance of stability', 'the duty to prevent harm'],
                'logic': ['alternative solutions are more effective', 'unintended consequences are likely'],
                'benefit': ['minimal benefits compared to risks', 'uncertain outcomes with high costs']
            }
        }

    def generate(self, topic: str, position: str = 'for') -> List[str]:
        """
        Generate arguments for a given topic and position.
        Uses Gemini AI when available, falls back to templates.
        """
        # Try Gemini first
        if gemini.is_available:
            ai_args = self._generate_with_gemini(topic, position)
            if ai_args:
                return ai_args

        # Fallback to template-based generation
        return self._generate_fallback(topic, position)

    def _generate_with_gemini(self, topic: str, position: str) -> List[str]:
        """Generate arguments using Gemini AI"""
        stance = "supporting (FOR)" if position == 'for' else "opposing (AGAINST)"

        prompt = f"""You are an expert debate coach and argumentation specialist. Generate 4 compelling, well-structured arguments {stance} the following debate motion:

"{topic}"

Requirements:
- Each argument should be from a different angle: Economic, Social, Ethical, and Practical
- Each argument should be 2-3 sentences long
- Use specific reasoning, not vague claims
- Be persuasive and include logical reasoning
- Include potential evidence or examples where relevant

Return ONLY a JSON object in this exact format:
{{
    "arguments": [
        "Economic argument here...",
        "Social argument here...",
        "Ethical argument here...",
        "Practical argument here..."
    ]
}}"""

        try:
            result = gemini.generate_json(prompt, temperature=0.8)
            if result and 'arguments' in result:
                args = result['arguments']
                if isinstance(args, list) and len(args) >= 1:
                    return args[:6]  # Return up to 6 arguments
        except Exception as e:
            print(f"Gemini argument generation failed: {e}")

        return None

    def _generate_fallback(self, topic: str, position: str) -> List[str]:
        """Generate arguments using template-based approach"""
        try:
            arguments = []
            categories = ['economic', 'social', 'ethical', 'practical']
            phrases = self.supporting_phrases.get(position, self.supporting_phrases['for'])

            for category in categories:
                template = random.choice(self.fallback_templates[category])
                argument = template.format(
                    topic=topic,
                    effect=random.choice(phrases.get('effect', ['have an impact'])),
                    impact=random.choice(phrases.get('impact', ['affect'])),
                    result=random.choice(phrases.get('result', ['various outcomes'])),
                    judgment=random.choice(phrases.get('judgment', ['has implications'])),
                    reason=random.choice(phrases.get('reason', ['of various factors'])),
                    outcome=random.choice(phrases.get('outcome', ['change is expected'])),
                    mechanism=random.choice(phrases.get('mechanism', ['various means'])),
                    significance=random.choice(phrases.get('significance', ['notable change'])),
                    issue=random.choice(phrases.get('issue', ['key concerns'])),
                    principle=random.choice(phrases.get('principle', ['core values'])),
                    logic=random.choice(phrases.get('logic', ['logical reasoning'])),
                    benefit=random.choice(phrases.get('benefit', ['potential advantages']))
                )
                arguments.append(argument)

            return arguments
        except Exception:
            return [
                f"The implementation of {topic} would have significant implications for society.",
                f"From multiple perspectives, {topic} presents both opportunities and challenges.",
                f"The debate around {topic} involves complex considerations that merit careful analysis.",
                f"Stakeholders should consider the long-term effects of {topic} on various communities."
            ]