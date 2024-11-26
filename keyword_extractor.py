from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv()
# Naver API 설정
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

HEADERS = {
    'X-Naver-Client-Id': NAVER_CLIENT_ID,
    'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
}

def load_stopwords(filepath):
    """stopwords-ko.txt 파일을 불러와서 불용어 세트로 반환합니다."""
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().splitlines())
    return stopwords

def fetch_and_extract_keywords(stock_name, stopwords_filepath):
    """지정된 주식명에 대해 키워드를 추출하는 함수."""
    korean_stopwords = load_stopwords(stopwords_filepath)
    query = f"{stock_name}"
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=100&sort=date"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching news for {stock_name}: {response.status_code}")
        return []

    articles = response.json().get('items', [])
    content_list = []
    today = datetime.now().strftime("%Y-%m-%d")

    for article in articles:
        pub_date = article.get('pubDate', '')
        pub_date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        pub_date_str = pub_date_obj.strftime("%Y-%m-%d")

        if today == pub_date_str:
            title = article['title']
            description = article['description']
            content = title + ' ' + description
            content = content.replace('<b>', '').replace('</b>', '')
            content_list.append(content)

    if not content_list:
        print(f"No news found for {stock_name} on {today}.")
        return []

    kiwi = Kiwi()
    filtered_documents = []
    for content in content_list:
        tokens = kiwi.analyze(content)
        filtered_tokens = [
            word for tokenized_text, _ in tokens for word, pos, _, _ in tokenized_text
            if pos in {'NNG', 'NNP'} and word not in korean_stopwords and word != stock_name
        ]
        filtered_documents.append(' '.join(filtered_tokens))

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(filtered_documents)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.sum(axis=0).A1
    tfidf_dict = dict(zip(feature_names, tfidf_scores))

    sorted_keywords = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)
    seen = set()
    unique_sorted_keywords = [(k, v) for k, v in sorted_keywords if not (k in seen or seen.add(k))][:30]
    
    return unique_sorted_keywords