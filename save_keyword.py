import mysql.connector
from dotenv import load_dotenv
import os
from keyword_extractor import fetch_and_extract_keywords

# MySQL 연결 설정
load_dotenv()

connection = mysql.connector.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    database=os.environ.get('DB_DATABASE')
)
cursor = connection.cursor()

# 키워드 테이블 생성 (테이블이 없는 경우 실행)
cursor.execute("""
CREATE TABLE IF NOT EXISTS keyword (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    keyword VARCHAR(255),
    weight FLOAT,
    FOREIGN KEY (stock_id) REFERENCES stock(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")

# Stock 테이블에서 데이터를 가져와 키워드 추출 및 저장
cursor.execute("SELECT id, stock_name FROM stock")
stocks = cursor.fetchall()
stopwords_filepath = 'stopwords-ko.txt'  # 불용어 파일 경로

for stock_id, stock_name in stocks:
    keywords = fetch_and_extract_keywords(stock_name, stopwords_filepath)
    for keyword, weight in keywords:
        cursor.execute(
            "INSERT INTO keyword (stock_id, keyword, weight) VALUES (%s, %s, %s)",
            (stock_id, keyword, float(weight))  # weight 값을 float으로 변환
        )
    connection.commit()
    print(f"Keywords for {stock_name} saved successfully.")

# 연결 닫기
cursor.close()
connection.close()