from pykrx import stock
import mysql.connector

jusicDate = "20240919"
# MySQL 연결 설정
connection = mysql.connector.connect(
    host="127.0.0.1",  # Docker 컨테이너가 로컬에서 실행 중이므로 localhost 사용
    user="root",
    password="1234",
    database="stockey",
    charset="utf8mb4"
)

cursor = connection.cursor()
cursor.execute("SET NAMES utf8mb4;")  # 세션 인코딩 설정

# 테이블이 없으면 생성하는 코드
create_table_query = """
CREATE TABLE IF NOT EXISTS stock_data (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    market VARCHAR(10) NOT NULL
) CHARACTER SET utf8mb4;
"""
cursor.execute(create_table_query)

# 기존 데이터를 전부 삭제하는 코드
cursor.execute("DELETE FROM stock_data")
print("기존 데이터를 모두 삭제했습니다.")

# 데이터를 삽입할 함수 정의
def insert_stock_data(ticker, name, market):
    try:
        sql = "INSERT INTO stock_data (ticker, name, market) VALUES (%s, %s, %s)"
        cursor.execute(sql, (ticker, name, market))
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# KRX에서 데이터 가져와 MySQL에 삽입
for ticker in stock.get_market_ticker_list(jusicDate, market="KOSPI"):
    name = stock.get_market_ticker_name(ticker)
    insert_stock_data(ticker, name, "KOSPI")

for ticker in stock.get_market_ticker_list(jusicDate, market="KOSDAQ"):
    name = stock.get_market_ticker_name(ticker)
    insert_stock_data(ticker, name, "KOSDAQ")

for ticker in stock.get_market_ticker_list(jusicDate, market="KONEX"):
    name = stock.get_market_ticker_name(ticker)
    insert_stock_data(ticker, name, "KONEX")

# 데이터베이스 변경 사항 커밋 및 연결 종료
connection.commit()
cursor.close()
connection.close()
print("새로운 데이터를 모두 삽입했습니다.")