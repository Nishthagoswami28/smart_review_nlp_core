import re

def clean_raw_reviews(raw_text):
    """
    Cleans raw review text typically scraped or pasted from online sources.
    Filters out star ratings, buyer tags, names, dates, and read-more links.
    Groups into distinct reviews based on sentence punctuation.
    """
    # Step 1: Remove numeric IDs and standalone star ratings
    cleaned = re.sub(r'^\d{6,}$', '', raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r'^\s*[1-5]\s*$', '', cleaned, flags=re.MULTILINE)

    # Step 2: Remove names, dates, certified buyer lines
    cleaned = re.sub(r'^Certified Buyer.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(
        r'^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
        r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*,?\s*\d{4}$',
        '', cleaned, flags=re.MULTILINE)

    # Step 3: Remove cut-off markers like READ MORE
    cleaned = re.sub(r'READ\s*MORE', '', cleaned, flags=re.IGNORECASE)

    # Step 4: Group meaningful review lines
    lines = cleaned.strip().splitlines()
    grouped = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if buffer.endswith(('.', '!', '?')):
            grouped.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line
    if buffer:
        grouped.append(buffer.strip())

    # Step 5: Remove duplicates
    unique_reviews = list(dict.fromkeys(grouped))

    return unique_reviews


def parse_reviews_only_text(text):
    """
    Parses and extracts reviews from raw input by detecting star ratings as review boundaries.
    Stops when it encounters Certified Buyer, dates, or name-like lines.
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    reviews = []
    current_review = []

    for line in lines:
        if line in {'1', '2', '3', '4', '5'}:
            if current_review:
                reviews.append(current_review)
            current_review = []
        else:
            current_review.append(line)
    if current_review:
        reviews.append(current_review)

    review_texts = []
    for review in reviews:
        body_lines = []
        for line in review:
            if line.startswith("Certified Buyer") or \
               re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec),? \d{4}$', line) or \
               line.isdigit():
                break
            elif re.match(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)+$', line):  # likely a name
                continue
            else:
                body_lines.append(line)
        if body_lines:
            review_texts.append(" ".join(body_lines))

    return review_texts
