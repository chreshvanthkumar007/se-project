import re

class SentimentService:
    """
    Robust rule-based and lexicon sentiment analysis engine for academic feedback.
    Analyzes sentiment polarity, handles negation, contrastive conjunctions (mixed sentiment),
    and produces normalized scores (-1.0 to +1.0).
    """

    POSITIVE_WORDS = {
        'excellent': 2.0, 'outstanding': 2.0, 'exceptional': 2.0, 'superb': 1.8, 'brilliant': 1.8,
        'great': 1.5, 'good': 1.0, 'clear': 1.2, 'clearly': 1.2, 'helpful': 1.4, 'supportive': 1.5,
        'engaging': 1.4, 'interactive': 1.3, 'enriching': 1.5, 'proactive': 1.4, 'friendly': 1.2,
        'approachable': 1.3, 'knowledgeable': 1.4, 'patient': 1.2, 'well-structured': 1.4,
        'insightful': 1.3, 'inspiring': 1.5, 'organized': 1.2, 'punctual': 1.2, 'responsive': 1.3,
        'improved': 1.0, 'satisfactory': 0.8, 'decent': 0.7, 'comfortable': 1.2, 'modern': 1.3,
        'smooth': 1.1, 'efficient': 1.4, 'high-speed': 1.2, 'fast': 1.1, 'clean': 1.2, 'best': 1.8,
        'praised': 1.3, 'wonderful': 1.6, 'productive': 1.3, 'valuable': 1.3, 'adequate': 0.6,
        'updated': 1.1, 'innovative': 1.4, 'comprehensive': 1.2, 'practical': 1.3
    }

    NEGATIVE_WORDS = {
        'terrible': -2.0, 'horrible': -2.0, 'worst': -2.0, 'awful': -1.8, 'useless': -1.8,
        'poor': -1.4, 'bad': -1.2, 'outdated': -1.5, 'broken': -1.6, 'defective': -1.6,
        'delayed': -1.3, 'slow': -1.2, 'unhelpful': -1.5, 'unresponsive': -1.5, 'strict': -0.8,
        'harsh': -1.3, 'unfair': -1.5, 'confusing': -1.3, 'disorganized': -1.4, 'boring': -1.2,
        'monotonous': -1.1, 'inefficient': -1.4, 'insufficient': -1.3, 'lacking': -1.2,
        'limited': -0.9, 'expensive': -1.1, 'dirty': -1.4, 'noisy': -1.2, 'cramped': -1.1,
        'unavailable': -1.2, 'failing': -1.5, 'waste': -1.7, 'problem': -1.1, 'issues': -1.0,
        'complaint': -1.2, 'shortage': -1.3, 'blinking': -1.0, 'rigid': -1.0, 'tough': -0.8,
        'difficult': -0.7, 'rude': -1.6, 'uncomfortable': -1.3, 'cluttered': -1.0, 'cumbersome': -1.2,
        'hard': -0.6, 'flawed': -1.3, 'glitchy': -1.3, 'frustrating': -1.5
    }

    NEGATORS = {'not', "n't", 'no', 'never', 'hardly', 'barely', 'scarcely', 'seldom', 'without', 'lack', 'lacks'}
    CONTRASTIVE_CONJUNCTIONS = {'but', 'however', 'although', 'though', 'yet', 'while', 'whereas', 'nevertheless'}
    INTENSIFIERS = {'very': 1.3, 'extremely': 1.5, 'greatly': 1.4, 'really': 1.3, 'highly': 1.4, 'quite': 1.1, 'too': 1.2}

    @classmethod
    def analyze(cls, text: str):
        if not text or not text.strip():
            return {
                'sentiment': 'Neutral',
                'sentiment_score': 0.0,
                'pos_count': 0,
                'neg_count': 0,
                'is_contrastive': False
            }

        text_lower = text.lower()
        words = re.findall(r"\b[\w'-]+\b", text_lower)
        
        # Check for contrastive markers (e.g., "Faculty is great BUT lab equipment is outdated")
        has_contrast = any(c in words for c in cls.CONTRASTIVE_CONJUNCTIONS)

        total_score = 0.0
        pos_words_found = []
        neg_words_found = []

        window_size = 3
        for i, word in enumerate(words):
            # Check previous words for negator
            start = max(0, i - window_size)
            prev_context = words[start:i]
            is_negated = any(neg in prev_context for neg in cls.NEGATORS)
            
            # Check for intensifier
            intensity = 1.0
            for w in prev_context:
                if w in cls.INTENSIFIERS:
                    intensity = cls.INTENSIFIERS[w]
                    break

            if word in cls.POSITIVE_WORDS:
                base = cls.POSITIVE_WORDS[word] * intensity
                if is_negated:
                    total_score -= base
                    neg_words_found.append(f"not {word}")
                else:
                    total_score += base
                    pos_words_found.append(word)

            elif word in cls.NEGATIVE_WORDS:
                base = cls.NEGATIVE_WORDS[word] * intensity
                if is_negated:
                    total_score += abs(base) * 0.7  # "not bad" is mildly positive
                    pos_words_found.append(f"not {word}")
                else:
                    total_score += base
                    neg_words_found.append(word)

        # Normalize score into [-1.0, 1.0] range
        normalized_score = 0.0
        word_count = len(words)
        if word_count > 0:
            raw = total_score / (len(pos_words_found) + len(neg_words_found) + 1.0)
            normalized_score = max(-1.0, min(1.0, round(raw, 2)))

        # Determine sentiment classification
        pos_count = len(pos_words_found)
        neg_count = len(neg_words_found)

        # Mixed sentiment detection: text has both positive & negative aspects + contrastive conjunction
        if has_contrast and pos_count >= 1 and neg_count >= 1:
            sentiment = 'Mixed'
        elif normalized_score >= 0.20 or (pos_count >= 2 and neg_count == 0):
            sentiment = 'Positive'
        elif normalized_score <= -0.20 or (neg_count >= 2 and pos_count == 0):
            sentiment = 'Negative'
        elif pos_count > 0 and neg_count > 0:
            sentiment = 'Mixed'
        else:
            sentiment = 'Neutral'

        return {
            'sentiment': sentiment,
            'sentiment_score': normalized_score,
            'pos_count': pos_count,
            'neg_count': neg_count,
            'is_contrastive': has_contrast,
            'pos_words': pos_words_found,
            'neg_words': neg_words_found
        }
