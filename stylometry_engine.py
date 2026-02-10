"""
Stylometry Engine - Writing fingerprint analysis

Inspired by: Forensic stylometry used to identify J.K. Rowling as author of "The Cuckoo's Calling"

Every person has unique writing patterns that are hard to fake:
- Function word frequencies
- Sentence length distributions
- Punctuation preferences
- Vocabulary richness
- Formality markers
"""

import re
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import statistics


# Common function words (content-independent, style-revealing)
FUNCTION_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'because', 'as',
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'can', 'will', 'just', 'should', 'now', 'i', 'you', 'he',
    'she', 'it', 'we', 'they', 'what', 'which', 'who', 'this', 'that', 'these',
    'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
    'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'could',
    'should', 'might', 'must', 'shall', 'however', 'therefore', 'thus',
    'hence', 'also', 'yet', 'still', 'already', 'always', 'never', 'ever'
}

# Hedging words (indicate uncertainty, common in deception)
HEDGE_WORDS = {
    'maybe', 'perhaps', 'possibly', 'probably', 'might', 'could', 'may',
    'seem', 'seems', 'appeared', 'appears', 'believe', 'think', 'guess',
    'suppose', 'assume', 'likely', 'unlikely', 'somewhat', 'rather',
    'fairly', 'quite', 'sort of', 'kind of', 'approximately', 'roughly'
}

# Certainty words (overconfidence can indicate deception)
CERTAINTY_WORDS = {
    'definitely', 'certainly', 'absolutely', 'always', 'never', 'must',
    'undoubtedly', 'clearly', 'obviously', 'surely', 'truly', 'really',
    'totally', 'completely', 'entirely', 'positively', 'guaranteed',
    'without doubt', 'no question', 'for sure', 'hundred percent'
}

# Urgency words (common in BEC)
URGENCY_WORDS = {
    'urgent', 'asap', 'immediately', 'right now', 'right away', 'quickly',
    'hurry', 'rush', 'fast', 'time-sensitive', 'deadline', 'critical',
    'important', 'priority', 'emergency', 'today', 'now', 'instant',
    'before end of day', 'eod', 'cob', 'by close of business'
}


@dataclass
class StyleProfile:
    """Writing style fingerprint for an author"""
    author: str
    
    # Lexical features
    avg_word_length: float = 0.0
    vocabulary_richness: float = 0.0  # Type-token ratio
    function_word_freq: Dict[str, float] = field(default_factory=dict)
    
    # Syntactic features  
    avg_sentence_length: float = 0.0
    sentence_length_std: float = 0.0
    
    # Punctuation habits
    comma_rate: float = 0.0
    semicolon_rate: float = 0.0
    exclamation_rate: float = 0.0
    question_rate: float = 0.0
    dash_rate: float = 0.0
    
    # Structural features
    avg_paragraph_length: float = 0.0
    uses_greeting: bool = True
    common_greetings: List[str] = field(default_factory=list)
    common_closings: List[str] = field(default_factory=list)
    
    # Formality markers
    contraction_rate: float = 0.0  # "don't" vs "do not"
    first_person_rate: float = 0.0  # I, me, my
    formality_score: float = 0.5
    
    # Sample count
    sample_count: int = 0
    total_words: int = 0


class StylometryEngine:
    """
    Builds and compares writing style fingerprints.
    
    Based on forensic linguistics research showing that writing style
    is as unique as a fingerprint - and very hard to fake convincingly.
    """
    
    def __init__(self):
        self.profiles: Dict[str, StyleProfile] = {}
        self.sample_texts: Dict[str, List[str]] = defaultdict(list)
        
    def tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        # Lowercase and extract words
        text = text.lower()
        words = re.findall(r'\b[a-z]+\b', text)
        return words
        
    def get_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
        
    def extract_features(self, text: str) -> Dict:
        """Extract style features from a single text"""
        words = self.tokenize(text)
        sentences = self.get_sentences(text)
        
        if not words:
            return {}
            
        word_count = len(words)
        unique_words = set(words)
        
        features = {}
        
        # Lexical features
        features['avg_word_length'] = sum(len(w) for w in words) / word_count
        features['vocabulary_richness'] = len(unique_words) / word_count
        
        # Function word frequencies
        func_word_counts = Counter(w for w in words if w in FUNCTION_WORDS)
        features['function_words'] = {
            w: count / word_count 
            for w, count in func_word_counts.items()
        }
        
        # Sentence features
        if sentences:
            sent_lengths = [len(self.tokenize(s)) for s in sentences]
            features['avg_sentence_length'] = statistics.mean(sent_lengths)
            if len(sent_lengths) > 1:
                features['sentence_length_std'] = statistics.stdev(sent_lengths)
            else:
                features['sentence_length_std'] = 0
        else:
            features['avg_sentence_length'] = word_count
            features['sentence_length_std'] = 0
            
        # Punctuation rates (per 100 words)
        features['comma_rate'] = text.count(',') / word_count * 100
        features['semicolon_rate'] = text.count(';') / word_count * 100
        features['exclamation_rate'] = text.count('!') / word_count * 100
        features['question_rate'] = text.count('?') / word_count * 100
        features['dash_rate'] = (text.count('-') + text.count('—')) / word_count * 100
        
        # Contractions
        contraction_pattern = r"\b\w+'\w+\b"
        contractions = re.findall(contraction_pattern, text.lower())
        features['contraction_rate'] = len(contractions) / word_count * 100
        
        # First person
        first_person = sum(1 for w in words if w in {'i', 'me', 'my', 'mine', 'myself'})
        features['first_person_rate'] = first_person / word_count * 100
        
        # Formality score (rough heuristic)
        formality = 0.5
        if features['contraction_rate'] > 2:
            formality -= 0.2
        if features['exclamation_rate'] > 1:
            formality -= 0.1
        if features['avg_sentence_length'] > 20:
            formality += 0.2
        features['formality_score'] = max(0, min(1, formality))
        
        # Special word categories
        features['hedge_count'] = sum(1 for w in words if w in HEDGE_WORDS)
        features['certainty_count'] = sum(1 for w in words if w in CERTAINTY_WORDS)
        features['urgency_count'] = sum(
            1 for phrase in URGENCY_WORDS 
            if phrase in text.lower()
        )
        
        return features
        
    def add_sample(self, author: str, text: str):
        """Add a text sample for an author"""
        author = author.lower()
        self.sample_texts[author].append(text)
        
    def build_profile(self, author: str) -> Optional[StyleProfile]:
        """Build a style profile from all samples"""
        author = author.lower()
        samples = self.sample_texts.get(author, [])
        
        if len(samples) < 10:
            return None  # Need minimum samples
            
        profile = StyleProfile(author=author)
        
        # Extract features from all samples
        all_features = [self.extract_features(text) for text in samples]
        all_features = [f for f in all_features if f]  # Remove empty
        
        if not all_features:
            return None
            
        profile.sample_count = len(all_features)
        
        # Average numeric features
        numeric_keys = [
            'avg_word_length', 'vocabulary_richness', 'avg_sentence_length',
            'sentence_length_std', 'comma_rate', 'semicolon_rate', 
            'exclamation_rate', 'question_rate', 'dash_rate',
            'contraction_rate', 'first_person_rate', 'formality_score'
        ]
        
        for key in numeric_keys:
            values = [f[key] for f in all_features if key in f]
            if values:
                setattr(profile, key, statistics.mean(values))
                
        # Merge function word frequencies
        merged_func_words = defaultdict(list)
        for f in all_features:
            for word, freq in f.get('function_words', {}).items():
                merged_func_words[word].append(freq)
                
        profile.function_word_freq = {
            word: statistics.mean(freqs)
            for word, freqs in merged_func_words.items()
        }
        
        # Total words processed
        profile.total_words = sum(
            len(self.tokenize(text)) for text in samples
        )
        
        self.profiles[author] = profile
        return profile
        
    def compare_to_profile(self, text: str, author: str) -> Dict:
        """
        Compare a text to an author's profile.
        
        Returns similarity score and deviation analysis.
        """
        author = author.lower()
        profile = self.profiles.get(author)
        
        if not profile:
            return {
                "author": author,
                "has_profile": False,
                "similarity": 0.5,
                "message": "No style profile available"
            }
            
        features = self.extract_features(text)
        if not features:
            return {
                "author": author,
                "has_profile": True,
                "similarity": 0.5,
                "message": "Text too short to analyze"
            }
            
        deviations = []
        deviation_score = 0.0
        
        # Compare numeric features
        comparisons = [
            ('avg_word_length', 0.5, "word length"),
            ('avg_sentence_length', 3.0, "sentence length"),
            ('comma_rate', 1.0, "comma usage"),
            ('exclamation_rate', 0.5, "exclamation usage"),
            ('contraction_rate', 1.0, "contraction usage"),
            ('formality_score', 0.2, "formality level"),
        ]
        
        for key, threshold, description in comparisons:
            if key in features:
                expected = getattr(profile, key, 0)
                actual = features[key]
                diff = abs(expected - actual)
                
                if diff > threshold:
                    deviations.append(
                        f"{description.upper()}: Expected {expected:.2f}, got {actual:.2f}"
                    )
                    deviation_score += min(diff / (threshold * 2), 0.3)
                    
        # Compare function word distribution (Burrows' Delta method, simplified)
        if profile.function_word_freq and features.get('function_words'):
            func_deviation = 0
            compared_words = 0
            
            for word, expected_freq in profile.function_word_freq.items():
                actual_freq = features['function_words'].get(word, 0)
                diff = abs(expected_freq - actual_freq)
                func_deviation += diff
                compared_words += 1
                
            if compared_words > 0:
                avg_func_deviation = func_deviation / compared_words
                if avg_func_deviation > 0.01:  # 1% difference is notable
                    deviations.append(
                        f"FUNCTION_WORDS: Distribution differs by {avg_func_deviation*100:.1f}%"
                    )
                    deviation_score += min(avg_func_deviation * 10, 0.3)
                    
        # Check for BEC indicators
        if features.get('urgency_count', 0) > 2:
            deviations.append(
                f"URGENCY_SPIKE: {features['urgency_count']} urgency markers detected"
            )
            deviation_score += 0.2
            
        if features.get('hedge_count', 0) > 3:
            deviations.append(
                f"HEDGING: Unusual hedging language ({features['hedge_count']} instances)"
            )
            deviation_score += 0.1
            
        # Calculate similarity (inverse of deviation)
        similarity = max(0, 1 - deviation_score)
        
        return {
            "author": author,
            "has_profile": True,
            "similarity": similarity,
            "deviation_score": deviation_score,
            "deviations": deviations,
            "risk_level": self._risk_level(deviation_score),
            "features_analyzed": len(features)
        }
        
    def _risk_level(self, deviation: float) -> str:
        if deviation >= 0.5:
            return "HIGH"
        elif deviation >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"


def demo():
    """Demonstrate stylometry analysis"""
    engine = StylometryEngine()
    
    print("=== Stylometry Engine Demo ===\n")
    print("Training on CEO's writing samples...")
    
    # Simulate CEO's writing style - formal, long sentences, few exclamations
    ceo_samples = [
        "Thank you for your email regarding the quarterly projections. I have reviewed the materials and believe we should proceed with caution given the current market conditions. Please schedule a meeting with the finance team to discuss further.",
        "I wanted to follow up on our conversation from last week. The board has approved the budget allocation, and we should move forward with the implementation plan. Let me know if you have any questions.",
        "After careful consideration of the proposal, I think we should explore alternative vendors before making a final decision. The timeline seems aggressive, and I would prefer to have more options on the table.",
        "Per our discussion, I am approving the contract with minor modifications. Please ensure legal reviews the updated terms before we proceed. I appreciate your attention to detail on this matter.",
        "I have reviewed the personnel changes you recommended. While I understand the rationale, I believe we should take a more measured approach. Let us discuss this during our next one-on-one meeting.",
        "Thank you for bringing this to my attention. The situation requires careful handling, and I suggest we coordinate with the relevant stakeholders before taking any action. Your judgment on this matter is appreciated.",
        "I am pleased to inform you that the board has endorsed our strategic initiative. This represents a significant milestone for the organization, and I want to commend the team for their dedication.",
        "Following up on the acquisition discussion: I have concerns about the valuation methodology. Perhaps we should engage an independent advisor to provide a second opinion before proceeding.",
        "The regulatory filing needs to be submitted by end of month. Please coordinate with external counsel to ensure all requirements are properly addressed. This is a priority item.",
        "I appreciate the comprehensive analysis you provided. Your recommendations align with our long-term objectives, and I believe we should proceed as outlined in section three of your report.",
        "After reflecting on our conversation, I want to emphasize the importance of maintaining strong relationships with our key partners. Please ensure the account team is properly briefed.",
        "The financial projections look reasonable given the assumptions. However, I would like to see a sensitivity analysis before we present to the investment committee next week.",
    ]
    
    for sample in ceo_samples:
        engine.add_sample("ceo@acme.com", sample)
        
    profile = engine.build_profile("ceo@acme.com")
    
    print(f"\nCEO Style Profile Built:")
    print(f"  Samples analyzed: {profile.sample_count}")
    print(f"  Avg word length: {profile.avg_word_length:.2f}")
    print(f"  Avg sentence length: {profile.avg_sentence_length:.1f} words")
    print(f"  Formality score: {profile.formality_score:.2f}")
    print(f"  Contraction rate: {profile.contraction_rate:.2f}%")
    print(f"  Exclamation rate: {profile.exclamation_rate:.2f}%")
    
    print("\n" + "="*50)
    
    print("\n--- Scenario 1: Legitimate CEO Email ---")
    legit_email = """
    Thank you for the update on the vendor negotiations. I have reviewed the proposed terms 
    and believe we should proceed with the recommended approach. Please coordinate with 
    procurement to finalize the agreement before end of quarter.
    """
    result1 = engine.compare_to_profile(legit_email, "ceo@acme.com")
    print(f"Similarity: {result1['similarity']:.2f}")
    print(f"Risk Level: {result1['risk_level']}")
    
    print("\n--- Scenario 2: BEC Attack - Different Writing Style ---")
    bec_email = """
    Hey!! I need you to wire $50,000 to this account ASAP!!! Its super urgent and I cant 
    explain right now. Just do it quick before the deal falls thru. Dont tell anyone 
    about this ok? I'll explain later. HURRY!!!
    """
    result2 = engine.compare_to_profile(bec_email, "ceo@acme.com")
    print(f"Similarity: {result2['similarity']:.2f}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Deviations: {result2['deviations']}")
    
    print("\n--- Scenario 3: Sophisticated BEC - Mimicking Formality ---")
    sophisticated_bec = """
    I need you to process an urgent wire transfer immediately. This is time-sensitive 
    and must be completed before close of business today. The amount is $75,000 to 
    the account details I will send separately. Please confirm receipt of this message 
    and proceed without delay. Do not discuss this with other team members.
    """
    result3 = engine.compare_to_profile(sophisticated_bec, "ceo@acme.com")
    print(f"Similarity: {result3['similarity']:.2f}")
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Deviations: {result3['deviations']}")


if __name__ == "__main__":
    demo()
