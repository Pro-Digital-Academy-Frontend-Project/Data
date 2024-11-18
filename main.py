from pykrx import stock
import mysql.connector
import requests
import time
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

# MySQL 연결 설정
connection = mysql.connector.connect(
    host=os.environ.get('DB_HOST'),  # MySQL 호스트
    user=os.environ.get('DB_USER'),  # MySQL 사용자명
    password=os.environ.get('DB_PASSWORD'),  # MySQL 비밀번호
    database=os.environ.get('DB_DATABASE')  # 데이터베이스 이름
)

cursor = connection.cursor()

# 테이블 생성 (테이블이 없는 경우 실행)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30),
    stock_name VARCHAR(255),
    market VARCHAR(10)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")

# 기존 데이터 삭제
cursor.execute("SET SQL_SAFE_UPDATES = 0")
cursor.execute("DELETE FROM Stock")  # stock 테이블에서 삭제
cursor.execute("SET SQL_SAFE_UPDATES = 1")

# 변경사항 저장
connection.commit()

# API 요청 및 데이터 저장
for page in range(1, 11):
    url = f"https://finance.daum.net/api/trend/market_capitalization?page={page}&perPage=30&fieldName=marketCap&order=desc&market=KOSPI&pagination=true"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://finance.daum.net/'
    }

    # API 요청 보내기
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get('data', [])
        for item in data:
            code = item['symbolCode'][1:]  # 'A' 제거
            stock_name = item['name']
            market = "KOSPI"  # 시장 이름 고정

            # MySQL에 데이터 삽입
            cursor.execute("INSERT INTO Stock (code, stock_name, market) VALUES (%s, %s, %s)",
                           (code, stock_name, market))

        # 변경사항 저장
        connection.commit()
        print("DB 삽입 성공")
    else:
        print(f"Error fetching page {page}, Status Code: {response.status_code}")

    # 1초간 대기
    time.sleep(1)

# 연결 닫기
cursor.close()
connection.close()
