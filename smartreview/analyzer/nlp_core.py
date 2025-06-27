import pandas as pd
from rake_nltk import Rake
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Download required NLTK resources silently
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def get_sentiment(text):
    """
    Classify the sentiment of the given text using VADER.
    """
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'


def extract_keywords(text):
    """
    Extract keywords using RAKE and filter to retain key Nouns/Adjectives.
    """
    rake = Rake()
    rake.extract_keywords_from_text(text)
    raw_keywords = rake.get_ranked_phrases()

    filtered_keywords = []
    for phrase in raw_keywords[:10]:  # Only consider top 10 phrases
        tokens = nltk.word_tokenize(phrase)
        tagged = nltk.pos_tag(tokens)
        if any(tag.startswith('NN') or tag.startswith('JJ') for _, tag in tagged):
            filtered_keywords.append(phrase)
    return filtered_keywords[:5]  # Limit to top 5


def analyze_reviews(reviews):
    """
    Analyze a list of reviews and return:
    - Summary with sentiment distribution
    - List of individual results (review, sentiment, keywords)
    """
    results = []
    sentiment_counts = {'Positive': 0, 'Neutral': 0, 'Negative': 0}

    for review in reviews:
        sentiment = get_sentiment(review)
        keywords = extract_keywords(review)
        sentiment_counts[sentiment] += 1

        results.append({
            'review': review,
            'sentiment': sentiment,
            'keywords': keywords
        })

    total = len(reviews)
    summary = {
        'total_reviews': total,
        'sentiment_distribution': sentiment_counts,
        'positive_pct': round(sentiment_counts['Positive'] / total * 100, 2) if total else 0,
        'negative_pct': round(sentiment_counts['Negative'] / total * 100, 2) if total else 0,
        'neutral_pct': round(sentiment_counts['Neutral'] / total * 100, 2) if total else 0,
    }

    return summary, results


def parse_uploaded_file(file):
    """
    Accepts a .csv or .txt file and returns a list of cleaned review strings.
    CSV must contain a column named 'review'.
    """
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
        if 'review' not in df.columns:
            raise ValueError("CSV must contain a 'review' column.")
        return df['review'].dropna().tolist()

    elif file.name.endswith('.txt'):
        content = file.read().decode('utf-8')
        return [line.strip() for line in content.split('\n') if line.strip()]

    else:
        raise ValueError("Unsupported file type. Please upload a .csv or .txt file.")
