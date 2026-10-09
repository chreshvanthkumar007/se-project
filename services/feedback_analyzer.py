import re
import requests
from config import Config
from services.sentiment_service import SentimentService

class FeedbackAnalyzer:
    """
    Core AI & NLP Feedback Analyzer engine.
    Extracts sentiment, keywords, topics, strengths, problems, and actionable recommendations.
    Works 100% offline using rule-based and lexicon NLP, with optional Google Gemini enhancement.
    """

    STOP_WORDS = {
        'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't",
        'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
        'can', "can't", 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
        'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself',
        'his', 'how', 'i', 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 'just', 'me',
        'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or',
        'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some',
        'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
        'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were',
        'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you', 'your'
    }

    TOPIC_DICTIONARY = {
        'Teaching': ['teach', 'teaching', 'pedagogy', 'lecture', 'lectures', 'explain', 'explains', 'explanation', 'method', 'slide', 'notes', 'pedagogical'],
        'Faculty': ['faculty', 'professor', 'professors', 'teacher', 'instructor', 'mentor', 'mentorship', 'office hours', 'sir', 'maam', 'staff'],
        'Laboratory': ['laboratory', 'lab', 'labs', 'equipment', 'oscilloscope', 'hardware', 'pc', 'computers', 'experiment', 'experiments', 'practical', 'practicals'],
        'Infrastructure': ['infrastructure', 'projector', 'ac', 'air conditioning', 'fan', 'light', 'chair', 'benches', 'wifi', 'wi-fi', 'internet', 'classroom', 'hall', 'building', 'power'],
        'Library': ['library', 'books', 'textbook', 'textbooks', 'journal', 'journals', 'reading room', 'ieee', 'digital portal', 'catalog'],
        'Course Curriculum': ['course', 'curriculum', 'syllabus', 'subject', 'modules', 'nosql', 'devops', 'legacy', 'topics', 'content', 'academic'],
        'Exams & Grading': ['exam', 'exams', 'quiz', 'quizzes', 'assignment', 'assignments', 'grading', 'marks', 'score', 'internal', 'rubric', 'evaluation'],
        'Campus Facilities': ['campus', 'cafeteria', 'canteen', 'food', 'garden', 'grounds', 'hostel', 'sports', 'parking', 'cleanliness', 'hygiene'],
        'Student Services': ['student services', 'office', 'admin', 'scholarship', 'counter', 'placement', 'training', 'cell', 'helpdesk', 'grievance', 'fees']
    }

    RECOMMENDATION_TEMPLATES = {
        'Laboratory': "Audit laboratory equipment and replace obsolete hardware with modern functional instruments.",
        'Infrastructure': "Issue maintenance orders to fix classroom utilities (projectors, air conditioning, and electrical sockets).",
        'Library': "Procure additional copies of high-demand reference texts and optimize digital repository off-campus credentials.",
        'Faculty': "Institute standardized email turnaround guidelines and regular student mentorship office hours.",
        'Course Curriculum': "Recommend curriculum review to the Board of Studies to align syllabus with modern industry practices.",
        'Teaching': "Encourage pedagogical workshops focused on interactive problem-solving and formative assessments.",
        'Exams & Grading': "Enforce transparent evaluation criteria and ensure timely grading feedback within two weeks.",
        'Campus Facilities': "Review cafeteria pricing and meal variety while sustaining campus landscape maintenance.",
        'Student Services': "Streamline administrative service requests and establish a transparent tracking timeline."
    }

    @classmethod
    def analyze_feedback(cls, text: str, category: str = 'Overall Experience', rating: int = 3):
        """
        Performs end-to-end feedback analysis.
        Returns a structured dictionary with sentiment, score, keywords, topics, strengths, problems, and recommendations.
        """
        # 1. Base Sentiment Analysis
        sentiment_res = SentimentService.analyze(text)
        sentiment = sentiment_res['sentiment']
        sentiment_score = sentiment_res['sentiment_score']

        # Adjust sentiment if rating contradicts heavily (e.g. rating=1 with ambiguous text)
        if rating <= 2 and sentiment == 'Positive':
            sentiment = 'Mixed'
            sentiment_score = -0.20
        elif rating >= 4 and sentiment == 'Negative':
            sentiment = 'Mixed'
            sentiment_score = 0.20
        elif rating == 1 and sentiment == 'Neutral':
            sentiment = 'Negative'
            sentiment_score = -0.50
        elif rating == 5 and sentiment == 'Neutral':
            sentiment = 'Positive'
            sentiment_score = 0.75

        # 2. Extract Keywords
        keywords = cls._extract_keywords(text)

        # 3. Detect Topics
        topics = cls._detect_topics(text, category)

        # 4. Extract Strengths and Problems (Aspect-based breakdown)
        strengths, problems = cls._extract_aspects(text, sentiment, rating, sentiment_res)

        # 5. Formulate Actionable Recommendations
        recommendations = cls._generate_recommendations(category, topics, problems, strengths, sentiment)

        return {
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'keywords': keywords,
            'topics': topics,
            'strengths': strengths,
            'problems': problems,
            'recommendations': recommendations
        }

    @classmethod
    def _extract_keywords(cls, text: str):
        cleaned = re.sub(r'[^\w\s-]', ' ', text.lower())
        tokens = [w.strip() for w in cleaned.split() if len(w) > 3 and w not in cls.STOP_WORDS]
        
        # Rank by frequency while preserving distinct order
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1

        sorted_tokens = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
        return sorted_tokens[:6] if sorted_tokens else [category_token for category_token in ['general', 'experience']]

    @classmethod
    def _detect_topics(cls, text: str, default_category: str):
        text_lower = text.lower()
        detected = []

        for topic, keywords in cls.TOPIC_DICTIONARY.items():
            for kw in keywords:
                if kw in text_lower:
                    if topic not in detected:
                        detected.append(topic)
                    break

        if not detected and default_category:
            detected.append(default_category)

        return detected[:4]

    @classmethod
    def _extract_aspects(cls, text: str, sentiment: str, rating: int, sentiment_res: dict):
        strengths = []
        problems = []

        # Split into sentences or clauses separated by punctuation and conjunctions
        clauses = re.split(r'[,;.\n]|(?:\b(?:but|however|although|while|whereas)\b)', text, flags=re.IGNORECASE)
        clean_clauses = [c.strip() for c in clauses if len(c.strip()) > 8]

        pos_words = set(sentiment_res.get('pos_words', []))
        neg_words = set(sentiment_res.get('neg_words', []))

        for clause in clean_clauses:
            clause_lower = clause.lower()
            c_words = set(re.findall(r"\b[\w'-]+\b", clause_lower))
            has_pos = any(w in c_words for w in pos_words) or any(w in clause_lower for w in ['good', 'great', 'clear', 'helpful', 'excellent', 'supportive', 'well', 'engaging', 'modern'])
            has_neg = any(w in c_words for w in neg_words) or any(w in clause_lower for w in ['outdated', 'broken', 'slow', 'poor', 'delayed', 'unhelpful', 'bad', 'issue', 'problem', 'flawed', 'insufficient', 'shortage'])

            capitalized = clause[0].upper() + clause[1:]
            if has_pos and not has_neg:
                if capitalized not in strengths:
                    strengths.append(capitalized)
            elif has_neg:
                if capitalized not in problems:
                    problems.append(capitalized)

        # Fallback if no specific clause isolated
        if not strengths and sentiment in ('Positive', 'Mixed') and rating >= 3:
            strengths.append("Commended overall quality and positive learning environment.")
        
        if not problems and sentiment in ('Negative', 'Mixed') and rating <= 3:
            problems.append("Identified operational or pedagogical deficiencies requiring attention.")

        return strengths[:3], problems[:3]

    @classmethod
    def _generate_recommendations(cls, category: str, topics: list, problems: list, strengths: list, sentiment: str):
        recommendations = []

        # If sentiment is purely positive and no problem
        if sentiment == 'Positive' and not problems:
            return ["Sustain high pedagogical/facility standards and recognize contributing faculty and departments for commendable performance."]

        # Prioritize primary category recommendation
        if category in cls.RECOMMENDATION_TEMPLATES:
            recommendations.append(cls.RECOMMENDATION_TEMPLATES[category])

        # Then check detected topics
        for topic in topics:
            if topic in cls.RECOMMENDATION_TEMPLATES:
                rec = cls.RECOMMENDATION_TEMPLATES[topic]
                if rec not in recommendations:
                    recommendations.append(rec)

        if not recommendations:
            recommendations = ["Review student inputs in regular departmental meetings and implement progressive enhancements."]

        return recommendations[:2]
