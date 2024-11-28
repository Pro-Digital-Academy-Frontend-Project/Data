import requests
from datetime import datetime
from krwordrank.word import summarize_with_keywords
from itertools import combinations
import os

from dotenv import load_dotenv

load_dotenv()
# Naver API 설정
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

HEADERS = {
    'X-Naver-Client-Id': NAVER_CLIENT_ID,
    'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
}

def extend_stopwords(stock_name, filepath='stopwords-ko.txt'):
    """기존 불용어에 도메인 전용 불용어와 종목명을 구성하는 모든 조합을 추가합니다."""
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().splitlines())
    domain_stopwords = {"뉴스", "발표", "보도", "증권사"}
    
    # 종목명을 구성하는 단어 분리
    stock_name_parts = stock_name.split()
    
    # 종목명 부분 문자열 조합 생성
    for i in range(1, len(stock_name_parts) + 1):
        for combo in combinations(stock_name_parts, i):
            domain_stopwords.add(''.join(combo))  # "신한" + "투자" -> "신한투자"
    
    # 전체 종목명도 추가
    domain_stopwords.add(stock_name)
    stopwords.update(domain_stopwords)
    return stopwords

def fetch_news(stock_name):
    query = f"{stock_name}"
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=100&sort=date"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    articles = response.json().get('items', [])
    content_list = []
    today = datetime.now().strftime("%Y-%m-%d")
    for article in articles:
        pub_date = article.get('pubDate', '')
        pub_date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        pub_date_str = pub_date_obj.strftime("%Y-%m-%d")
        if today == pub_date_str:
            title = article['title'].replace('<b>', '').replace('</b>', '')
            description = article['description'].replace('<b>', '').replace('</b>', '')
            content_list.append(title + ' ' + description)
    return content_list

def extract_keywords_with_krwordrank(content_list, stopwords):
    """
    KR-WordRank로 키워드 추출 (Kiwi 형태소 분석 및 특수 문자 필터링 포함)
    """
    from kiwipiepy import Kiwi
    import re

    # 형태소 분석기로 명사, 형용사 추출 및 불용어 제거
    kiwi = Kiwi()
    filtered_texts = []
    for content in content_list:
        tokens = kiwi.analyze(content)
        filtered_tokens = []
        for tokenized_text, _ in tokens:
            for word, pos, _, _ in tokenized_text:
                if (
                    pos in {'NNG', 'NNP', 'VA'}
                    and word not in stopwords
                    and not re.match(r'^[^가-힣a-zA-Z0-9]', word)
                ):
                    filtered_tokens.append(word)
        if filtered_tokens:
            filtered_texts.append(' '.join(filtered_tokens))
    
    if not filtered_texts:
        print("Filtered texts are empty after stopword removal. Skipping...")
        return {}

    text = "\n".join(filtered_texts)

    # 최소 텍스트 길이 확인
    if len(text.split()) < 2:  # 최소 단어 조건
        print("Not enough valid words for keyword extraction. Skipping...")
        return {}

    # KR-WordRank로 키워드 추출
    try:
        keywords = summarize_with_keywords(
            texts=text.split("\n"),
            min_count=2,
            max_length=10,
            beta=0.85,
            max_iter=10,
            stopwords=stopwords
        )
    except ValueError as e:
        print(f"Error during keyword extraction: {e}")
        return {}
    
    return keywords


def fetch_and_process_news_with_keywords(stock_name, stopwords_filepath):
    """
    뉴스 데이터 처리 및 KR-WordRank 기반 키워드와 가중치 출력
    """
    stopwords = extend_stopwords(stock_name, stopwords_filepath)
    content_list = fetch_news(stock_name)
    if not content_list:
        print("관련 뉴스가 없습니다.")
        return
    
    # 키워드 추출 및 필터링 동시 수행
    keywords_dict = extract_keywords_with_krwordrank(content_list, stopwords)

    # 상위 키워드 추출
    top_keywords = sorted(keywords_dict.items(), key=lambda x: x[1], reverse=True)[:30]
    
    # 키워드와 가중치를 반환
    return top_keywords
