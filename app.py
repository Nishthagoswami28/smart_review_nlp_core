from flask import Flask, request, jsonify
from textblob import TextBlob
from rake_nltk import Rake
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return "Smart Review Analyzer API is running! Use /analyze to POST reviews."

# Sentiment Analysis
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

# Keyword Extraction
def extract_keywords(text):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:5]

# API Route
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    reviews = data.get('reviews', [])

    results = []
    for review in reviews:
        sentiment = get_sentiment(review)
        keywords = extract_keywords(review)
        results.append({
            'review': review,
            'sentiment': sentiment,
            'keywords': keywords
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
