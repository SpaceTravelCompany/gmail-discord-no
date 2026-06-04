import os
from dotenv import load_dotenv

load_dotenv()

# Discord 설정
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Gmail API 설정
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# 폴링 간격 (초)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))

# 중요 메일만 필터링
IMPORTANT_ONLY = os.getenv("IMPORTANT_ONLY", "true").lower() == "true"

# Gmail API 스코프
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
