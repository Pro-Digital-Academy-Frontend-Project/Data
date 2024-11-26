import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

print("Starting update_chat_room.py process...", flush=True)

# 환경 변수 로드
load_dotenv()
try:
    # MySQL 연결 설정
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),  # MySQL 호스트
        user=os.environ.get('DB_USER'),  # MySQL 사용자명
        password=os.environ.get('DB_PASSWORD'),  # MySQL 비밀번호
        database=os.environ.get('DB_DATABASE')  # 데이터베이스 이름
    )

    cursor = connection.cursor()

    # 전체 키워드 랭킹 조회 TOP 10
    query = """
        SELECT keyword
        FROM Keyword
        GROUP BY keyword
        ORDER BY SUM(weight) DESC
        LIMIT 10;
    """

    cursor.execute(query)

    # 결과를 가져오기
    results = cursor.fetchall()

    # 각 keyword에 대해, Chat_Room에 존재하는지 확인하고, 존재하지 않으면 삽입
    for row in results:
        keyword = row[0]
        
        # Chat_Room에 keyword가 존재하는지 확인하는 쿼리
        check_query = "SELECT 1 FROM Chat_Room WHERE name = %s"
        cursor.execute(check_query, (keyword,))
        existing_keyword = cursor.fetchone()
        
        if existing_keyword:
            print(f"{keyword} is Exist", flush=True)
        else :
            # 존재하지 않으면 삽입
            insert_query = "INSERT INTO Chat_Room (name, created_at) VALUES (%s, %s)"
            cursor.execute(insert_query, (keyword, datetime.now()))
            print(f"{keyword} added to Chat_Room", flush=True)
    connection.commit()  # 변경 사항 커밋

    # 결과 출력
    print(f"Successfully added keywords to Chat_Room.", flush=True)

except mysql.connector.Error as err:
    print(f"Error: {err}", flush=True)
    connection.rollback()  # 롤백 처리

finally:
    # 연결 종료
    if cursor:
        cursor.close()
    if connection:
        connection.close()

print("update_chat_room.py complted...", flush=True)
