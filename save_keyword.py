import mysql.connector
from dotenv import load_dotenv
import os
from keyword_extractor import fetch_and_extract_keywords

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

for stock_id, stock_name in stocks:
    keywords = fetch_and_extract_keywords(stock_name, stopwords_filepath)
    for keyword, weight in keywords:
        cursor.execute(
            "INSERT INTO Keyword (stock_id, keyword, weight) VALUES (%s, %s, %s)",
            (stock_id, keyword, float(weight))  # weight 값을 float으로 변환
        )
    connection.commit()
    print(f"Keywords for {stock_name} saved successfully.", flush=True)

# 연결 닫기
cursor.close()
connection.close()

print("save_keyword.py complted...", flush=True)