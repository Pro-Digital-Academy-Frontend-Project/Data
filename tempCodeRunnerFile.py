import os

# 환경변수에서 APP_KEY와 APP_SECRET 읽어오기
APP_KEY = os.environ.get('APP_KEY')
APP_SECRET = os.environ.get('APP_SECRET')

print(APP_KEY)
print(APP_SECRET)