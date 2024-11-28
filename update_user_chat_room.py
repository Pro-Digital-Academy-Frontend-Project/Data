import requests
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime
import os

print(f'Today -> {datetime.now()}', flush=True)
print("Starting update_chat_room.py process...", flush=True)

try:
    # 환경 변수 로드
    load_dotenv()
    
    response = requests.get("http://localhost:3000/api/chat/weight/rankings")

    top5 = response.json()['results']
    print(top5)
    
    # MySQL 연결 설정
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),  # MySQL 호스트
        user=os.environ.get('DB_USER'),  # MySQL 사용자명
        password=os.environ.get('DB_PASSWORD'),  # MySQL 비밀번호
        database=os.environ.get('DB_DATABASE')  # 데이터베이스 이름
    )
    
    cursor = connection.cursor()

    for row in top5:
        keyword = row['keyword']

        check_query = "SELECT 1 FROM Chat_Room WHERE name = %s"
        cursor.execute(check_query, (keyword,))
        existing_keyword = cursor.fetchone()
        
        if existing_keyword:
            print(f"{keyword} is Exist", flush=True)
        else:
            insert_query = "INSERT INTO Chat_Room (name, created_at) VALUES (%s, %s)"
            cursor.execute(insert_query, (keyword, datetime.now()))
            print(f"{keyword} added to Chat_Room", flush=True)
    connection.commit()  # 변경 사항 커밋

    # 결과 출력
    print(f"Successfully added User Like Keywords to Chat_Room.", flush=True)
    
except mysql.connector.Error as err:
    print(f"Error: {err}", flush=True)
    connection.rollback()  # 롤백 처리
    
finally:
    # 연결 종료
    if cursor:
        cursor.close()
        print("Cursor Close", flush=True)
    if connection:
        connection.close()
        print("Connetcion Close", flush=True)

print("update_chat_room.py complted...", flush=True)