"""
Bias Detector Utility
Detects potential bias in judge scoring and debate evaluation
"""

from typing import Dict, List, Any, Tuple
import re

class BiasDetector:
    def __init__(self):
        """Initialize bias detection with various bias patterns"""
        self.bias_patterns = {
            'length_bias': {
                'description': 'Favoring longer speeches regardless of quality',
                'threshold': 0.3
            },
            'vocabulary_bias': {
                'description': 'Favoring complex vocabulary over clear communication',
                'threshold': 0.25
            },
            'position_bias': {
                'description': 'Systematic preference for proposition or opposition',
                'threshold': 0.2
            },
            'evidence_bias': {
                'description': 'Over-weighting evidence quantity vs. quality',
                'threshold': 0.3
            },
            'style_bias': {
                'description': 'Favoring particular speaking or writing styles',
                'threshold': 0.25
            }
        }
        
        self.bias_indicators = {
            'emotional_language': [
                'terrible', 'horrible', 'amazing', 'fantastic', 'outrageous',
                'brilliant', 'stupid', 'ridiculous', 'perfect', 'awful'
            ],
            'absolute_terms': [
                'always', 'never', 'all', 'none', 'every', 'completely',
                'totally', 'absolutely', 'definitely', 'impossible'
            ],
            'loaded_words': [
                'obviously', 'clearly', 'undoubtedly', 'certainly', 'naturally',
                'of course', 'without question', 'beyond doubt'
            ]
        }

    def check_bias(self, debate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for various types of bias in debate evaluation
        
        Args:
            debate_data: Dictionary containing debate information and scores
            
        Returns:
            Dictionary containing bias analysis results
        """
        try:
            bias_results = {
                'has_bias': False,
                'bias_types': [],
                'bias_score': 0.0,
                'recommendations': [],
                'message': ''
            }
            
            # Extract debate components
            proposition = debate_data.get('proposition', '')
            opposition = debate_data.get('opposition', '')
            motion = debate_data.get('motion', '')
            
            # Check for different types of bias
            length_bias = self._check_length_bias(proposition, opposition)
            vocabulary_bias = self._check_vocabulary_bias(proposition, opposition)
            emotional_bias = self._check_emotional_bias(proposition, opposition)
            absolute_bias = self._check_absolute_language_bias(proposition, opposition)
            
            # Compile bias results
            biases_found = []
            total_bias_score = 0
            
            if length_bias['detected']:
                biases_found.append('length_bias')
                total_bias_score += length_bias['severity']
                bias_results['recommendations'].append(
                    "Consider speech quality over length when evaluating."
                )
            
            if vocabulary_bias['detected']:
                biases_found.append('vocabulary_bias')
                total_bias_score += vocabulary_bias['severity']
                bias_results['recommendations'].append(
                    "Focus on clarity and communication effectiveness rather than vocabulary complexity."
                )
            
            if emotional_bias['detected']:
                biases_found.append('emotional_bias')
                total_bias_score += emotional_bias['severity']
                bias_results['recommendations'].append(
                    "Be aware of emotional language that may influence judgment."
                )
            
            if absolute_bias['detected']:
                biases_found.append('absolute_language_bias')
                total_bias_score += absolute_bias['severity']
                bias_results['recommendations'].append(
                    "Watch for absolute statements that may oversimplify complex issues."
                )
            
            # Determine overall bias status
            bias_results['bias_types'] = biases_found
            bias_results['bias_score'] = total_bias_score / 4  # Average across checks
            bias_results['has_bias'] = bias_results['bias_score'] > 0.2
            
            # Generate message
            if bias_results['has_bias']:
                bias_results['message'] = self._generate_bias_message(biases_found, bias_results['bias_score'])
            else:
                bias_results['message'] = "No significant bias detected in the evaluation."
            
            return bias_results
            
        except Exception as e:
            return {
                'has_bias': False,
                'bias_types': [],
                'bias_score': 0.0,
                'recommendations': [],
                'message': 'Bias detection analysis could not be completed.'
            }

    def _check_length_bias(self, prop_speech: str, opp_speech: str) -> Dict[str, Any]:
        """Check for bias based on speech length"""
        prop_words = len(prop_speech.split())
        opp_words = len(opp_speech.split())
        
        if prop_words == 0 and opp_words == 0:
            return {'detected': False, 'severity': 0.0}
        
        total_words = prop_words + opp_words
        if total_words == 0:
            return {'detected': False, 'severity': 0.0}
        
        length_ratio = abs(prop_words - opp_words) / total_words
        
        return {
            'detected': length_ratio > self.bias_patterns['length_bias']['threshold'],
            'severity': min(length_ratio, 1.0),
            'details': {
                'prop_words': prop_words,
                'opp_words': opp_words,
                'ratio': length_ratio
            }
        }

    def _check_vocabulary_bias(self, prop_speech: str, opp_speech: str) -> Dict[str, Any]:
        """Check for bias based on vocabulary complexity"""
        prop_complexity = self._calculate_vocabulary_complexity(prop_speech)
        opp_complexity = self._calculate_vocabulary_complexity(opp_speech)
        
        if prop_complexity == 0 and opp_complexity == 0:
            return {'detected': False, 'severity': 0.0}
        
        avg_complexity = (prop_complexity + opp_complexity) / 2
        if avg_complexity == 0:
            return {'detected': False, 'severity': 0.0}
        
        complexity_diff = abs(prop_complexity - opp_complexity) / avg_complexity
        
        return {
            'detected': complexity_diff > self.bias_patterns['vocabulary_bias']['threshold'],
            'severity': min(complexity_diff, 1.0),
            'details': {
                'prop_complexity': prop_complexity,
                'opp_complexity': opp_complexity,
                'difference': complexity_diff
            }
        }

    def _check_emotional_bias(self, prop_speech: str, opp_speech: str) -> Dict[str, Any]:
        """Check for emotional language bias"""
        prop_emotional = self._count_emotional_words(prop_speech)
        opp_emotional = self._count_emotional_words(opp_speech)
        
        prop_words = len(prop_speech.split())
        opp_words = len(opp_speech.split())
        
        if prop_words == 0 or opp_words == 0:
            return {'detected': False, 'severity': 0.0}
        
        prop_ratio = prop_emotional / prop_words
        opp_ratio = opp_emotional / opp_words
        
        emotional_diff = abs(prop_ratio - opp_ratio)
        
        return {
            'detected': emotional_diff > 0.02,  # 2% difference threshold
            'severity': min(emotional_diff * 10, 1.0),  # Scale to 0-1
            'details': {
                'prop_emotional_ratio': prop_ratio,
                'opp_emotional_ratio': opp_ratio,
                'difference': emotional_diff
            }
        }

    def _check_absolute_language_bias(self, prop_speech: str, opp_speech: str) -> Dict[str, Any]:
        """Check for absolute language bias"""
        prop_absolute = self._count_absolute_terms(prop_speech)
        opp_absolute = self._count_absolute_terms(opp_speech)
        
        prop_words = len(prop_speech.split())
        opp_words = len(opp_speech.split())
        
        if prop_words == 0 or opp_words == 0:
            return {'detected': False, 'severity': 0.0}
        
        prop_ratio = prop_absolute / prop_words
        opp_ratio = opp_absolute / opp_words
        
        absolute_diff = abs(prop_ratio - opp_ratio)
        
        return {
            'detected': absolute_diff > 0.015,  # 1.5% difference threshold
            'severity': min(absolute_diff * 15, 1.0),  # Scale to 0-1
            'details': {
                'prop_absolute_ratio': prop_ratio,
                'opp_absolute_ratio': opp_ratio,
                'difference': absolute_diff
            }
        }

    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Calculate vocabulary complexity score"""
        words = text.lower().split()
        if not words:
            return 0.0
        
        # Count unique words
        unique_words = len(set(words))
        
        # Count long words (>6 characters)
        long_words = sum(1 for word in words if len(word) > 6)
        
        # Calculate complexity as combination of diversity and long words
        diversity = unique_words / len(words)
        long_word_ratio = long_words / len(words)
        
        return (diversity + long_word_ratio) / 2

    def _count_emotional_words(self, text: str) -> int:
        """Count emotional words in text"""
        text_lower = text.lower()
        count = 0
        
        for word in self.bias_indicators['emotional_language']:
            count += text_lower.count(word)
        
        return count

    def _count_absolute_terms(self, text: str) -> int:
        """Count absolute terms in text"""
        text_lower = text.lower()
        count = 0
        
        for term in self.bias_indicators['absolute_terms']:
            count += text_lower.count(term)
        
        return count

    def _generate_bias_message(self, bias_types: List[str], bias_score: float) -> str:
        """Generate a message describing detected bias"""
        if not bias_types:
            return "No significant bias detected."
        
        severity = "moderate" if bias_score < 0.5 else "significant"
        
        bias_descriptions = {
            'length_bias': "speech length preferences",
            'vocabulary_bias': "vocabulary complexity preferences",
            'emotional_bias': "emotional language influence",
            'absolute_language_bias': "absolute statement preferences"
        }
        
        detected_biases = [bias_descriptions.get(bias, bias) for bias in bias_types]
        
        if len(detected_biases) == 1:
            return f"Detected {severity} bias related to {detected_biases[0]}."
        else:
            bias_list = ", ".join(detected_biases[:-1]) + f" and {detected_biases[-1]}"
            return f"Detected {severity} bias related to {bias_list}."

    def suggest_improvements(self, bias_results: Dict[str, Any]) -> List[str]:
        """Suggest improvements based on bias detection results"""
        suggestions = []
        
        if not bias_results.get('has_bias', False):
            suggestions.append("Continue maintaining objective evaluation standards.")
            return suggestions
        
        bias_types = bias_results.get('bias_types', [])
        
        if 'length_bias' in bias_types:
            suggestions.append("Focus on argument quality rather than speech length.")
            suggestions.append("Consider implementing word count guidelines for fairness.")
        
        if 'vocabulary_bias' in bias_types:
            suggestions.append("Prioritize clear communication over complex vocabulary.")
            suggestions.append("Evaluate ideas and logic rather than linguistic sophistication.")
        
        if 'emotional_bias' in bias_types:
            suggestions.append("Be aware of emotional language that may cloud judgment.")
            suggestions.append("Focus on factual content and logical reasoning.")
        
        if 'absolute_language_bias' in bias_types:
            suggestions.append("Recognize that complex issues rarely have absolute answers.")
            suggestions.append("Value nuanced arguments over black-and-white statements.")
        
        suggestions.append("Consider using structured evaluation rubrics for consistency.")
        suggestions.append("Regular bias awareness training can help maintain objectivity.")
        
        return suggestions