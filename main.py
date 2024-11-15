from pykrx import stock
import mysql.connector
import requests
import time

# MySQL 연결 설정
connection = mysql.connector.connect(
    host="localhost",  # MySQL 호스트
    user="root",       # MySQL 사용자명
    password="1234",   # MySQL 비밀번호
    database="stockey",  # 데이터베이스 이름
    charset="utf8mb4"   # utf8mb4 인코딩 설정
)

cursor = connection.cursor()

# 테이블 생성 (테이블이 없는 경우 실행)
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10),
    name VARCHAR(255),
    market VARCHAR(10)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")

# 기존 데이터 삭제
cursor.execute("SET SQL_SAFE_UPDATES = 0")

# 기존 데이터 삭제
cursor.execute("DELETE FROM stock_data")

# Safe Update Mode 다시 활성화 (선택 사항)
cursor.execute("SET SQL_SAFE_UPDATES = 1")

# 변경사항 저장 (기존 데이터 삭제 후)
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
            ticker = item['symbolCode'][1:]  # 'A' 제거
            name = item['name']
            market = "KOSPI"  # 시장 이름 고정

            # MySQL에 데이터 삽입
            cursor.execute("INSERT INTO stock_data (ticker, name, market) VALUES (%s, %s, %s)",
                           (ticker, name, market))

        # 변경사항 저장
        connection.commit()
    else:
        print(f"Error fetching page {page}, Status Code: {response.status_code}")

    # 1초간 대기
    time.sleep(1)

# 연결 닫기
cursor.close()
connection.close()