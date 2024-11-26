import os
import requests
from dotenv import load_dotenv

load_dotenv()
# 환경변수에서 APP_KEY와 APP_SECRET 읽어오기
APP_KEY = os.environ.get('APP_KEY')
APP_SECRET = os.environ.get('APP_SECRET')

# # API 요청 URL
base_url = 'https://openapivts.koreainvestment.com:29443/oauth2/tokenP'

# # 요청 본문 데이터
body_data = {
    'grant_type': 'client_credentials',
    'appkey': APP_KEY,
    'appsecret': APP_SECRET
}

# # 요청 헤더
headers = {
    'Content-Type': 'application/json',
}

# # API 호출
try:
    response = requests.post(base_url, json=body_data, headers=headers)
    response.raise_for_status()  # 요청이 실패하면 예외 발생

    data = response.json()

    if 'access_token' in data:
        access_token = data['access_token']
        print(access_token)

        # 텍스트 파일에 토큰 저장
        with open('/home/ubuntu/token.txt', 'w') as file:
            file.write(access_token)

    else:
        print('토큰을 받을 수 없습니다.')

except requests.exceptions.RequestException as error:
    print(f"API 호출 중 오류 발생: {error}")