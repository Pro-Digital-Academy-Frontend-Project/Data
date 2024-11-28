import mysql.connector
from dotenv import load_dotenv
import os
from keyword_extractor import fetch_and_extract_keywords
from datetime import datetime
from extract_keyword_kr_wordrank import fetch_and_process_news_with_keywords

print(f'Today -> {datetime.now()}', flush=True)
print("Starting save_keyword.py process...", flush=True)

# MySQL 연결 설정
load_dotenv()

connection = mysql.connector.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    database=os.environ.get('DB_DATABASE')
)
cursor = connection.cursor()

print("DB Connected...", flush=True)

# 키워드 테이블 생성 (테이블이 없는 경우 실행)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Keyword (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    keyword VARCHAR(255),
    weight FLOAT,
    FOREIGN KEY (stock_id) REFERENCES stock(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
print("Keyword 테이블 생성 확인 완료.")

# 기존 데이터 삭제
cursor.execute("SET SQL_SAFE_UPDATES = 0")
cursor.execute("DELETE FROM Keyword")  # stock 테이블에서 삭제
cursor.execute("SET SQL_SAFE_UPDATES = 1")

print("DB Clear...", flush=True)

cursor.execute("SELECT COUNT(*) FROM Keyword")
count = cursor.fetchone()[0]  # 첫 번째 값(데이터 개수)을 가져옵니다.

print(f"Remaining data in Keyword table: {count}", flush=True)

# Stock 테이블에서 데이터를 가져와 키워드 추출 및 저장
cursor.execute("SELECT id, stock_name FROM Stock")
stocks = cursor.fetchall()
stopwords_filepath = '/home/ubuntu/Data/stopwords-ko.txt'  # 불용어 파일 경로
print(f"Stock 테이블에서 {len(stocks)}개의 데이터를 가져왔습니다.")

for stock_id, stock_name in stocks:
    print(f"\n[처리 시작] stock_id: {stock_id}, stock_name: {stock_name}")
    keywords = fetch_and_process_news_with_keywords(stock_name, stopwords_filepath)
    if not keywords:  # 키워드가 없는 경우
        print(f"  - {stock_name}에 대한 키워드를 찾을 수 없습니다. 건너뜁니다.")
        continue

    print(f"  - {len(keywords)}개의 키워드 추출됨: {keywords}")
    for keyword, weight in keywords:
        # 기존 키워드가 존재하는지 확인
        cursor.execute(
            "SELECT weight FROM Keyword WHERE stock_id = %s AND keyword = %s",
            (stock_id, keyword)
        )
        existing = cursor.fetchone()
        
        if existing:  # 키워드가 이미 존재하는 경우
            old_weight = existing[0]  # 기존 weight 값
            new_weight = old_weight * 0.5 + float(weight)  # 새로운 weight 계산
            cursor.execute(
                "UPDATE Keyword SET weight = %s WHERE stock_id = %s AND keyword = %s",
                (new_weight, stock_id, keyword)
            )
            print(f"    > 기존 키워드 '{keyword}' 업데이트: old_weight={old_weight}, new_weight={new_weight}")
        else:  # 키워드가 존재하지 않는 경우
            cursor.execute(
                "INSERT INTO Keyword (stock_id, keyword, weight) VALUES (%s, %s, %s)",
                (stock_id, keyword, float(weight))
            )
            print(f"    > 새로운 키워드 '{keyword}' 삽입: weight={weight}")

    connection.commit()

    print(f"  - {stock_name} 키워드 처리 완료.", flush=True)

# 연결 닫기
cursor.close()
connection.close()

print("\n모든 작업 완료. MySQL 연결이 종료되었습니다.", flush=True)
