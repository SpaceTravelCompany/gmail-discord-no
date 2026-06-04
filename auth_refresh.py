"""
Gmail API 토큰 재발급 (scope: modify + settings.basic)
"""
from google_auth_oauthlib.flow import InstalledAppFlow

# 확인하고 수정
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.settings.basic",
]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

with open("token.json", "w") as f:
    f.write(creds.to_json())

print("✅ 새 token.json 생성 완료!")
print(f"Scope: gmail.modify + gmail.settings.basic")
