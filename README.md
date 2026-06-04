# Gmail → Discord 중요 메일 알림 서비스

Gmail에서 중요 메일이 도착하면 Discord 웹훅으로 알림을 보내는 서비스입니다.

## 기능

- Gmail API를 사용한 실시간 메일 모니터링
- Gmail의 '중요' 표시를 기반으로 필터링
- Discord 웹훅을 통한 알림 전송
- 이메일 제목, 발신자, 미리보기 포함
- Gmail 링크 제공
- 백그라운드 실행 지원

## 사전 준비

### 1. Discord 웹훅 설정

1. Discord 채널 설정 → 연동 → 웹훅
2. '새 웹훅' 클릭
3. 웹훅 이름 설정 (예: "Gmail 알림")
4. 웹훅 URL 복사

### 2. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **APIs & Services → Library**에서 **Gmail API** 검색 후 사용 설정
4. **APIs & Services → Credentials**에서 **OAuth 2.0 클라이언트 ID** 생성
   - 애플리케이션 유형: **데스크톱 앱**
   - 이름: 원하는 이름 (예: "Gmail Monitor")
5. 생성된 클라이언트의 **JSON 다운로드** → `credentials.json`으로 저장

### 3. OAuth 동의 화면 설정

1. **APIs & Services → OAuth consent screen** 이동
2. **External** 선택 (개인 Gmail인 경우)
3. **Test users** 섹션에서 본인 Gmail 주소 추가
4. 저장

## 설치

```bash
# 1. 저장소 클론 (또는 파일 다운로드)
cd gmail-discord-no

# 2. 가상환경 생성
python -m venv .venv
.venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
copy .env.example .env
# .env 파일을 편집하여 설정
```

## 설정

`.env` 파일을 편집하여 다음 값을 설정하세요:

```env
# Discord 웹훅 URL (필수)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token

# Gmail API credentials 파일 경로
GOOGLE_CREDENTIALS_FILE=credentials.json

# 폴링 간격 (초)
POLL_INTERVAL=60

# 중요 메일만 필터링 (true/false)
IMPORTANT_ONLY=true
```

## 실행

### 콘솔 실행 (Ctrl+C로 종료)

```bash
python main.py
```

### 백그라운드 실행

```bash
# 시작
python start.py

# 중지
python stop.py

# 상태 확인
python status.py
```

## 파일 구조

```
gmail-discord-no/
├── .env                    # 환경 변수
├── .env.example           # 환경 변수 예제
├── credentials.json       # Google OAuth2 credentials
├── token.json            # Gmail API 토큰 (자동 생성)
├── requirements.txt      # Python 의존성
├── config.py            # 설정 모듈
├── gmail_client.py      # Gmail API 클라이언트
├── discord_notifier.py  # Discord 웹훅 모듈
├── main.py              # 메인 실행 스크립트
├── start.py             # 백그라운드 시작
├── stop.py              # 서비스 중지
├── status.py            # 상태 확인
└── gmail_monitor.log    # 로그 파일 (자동 생성)
```

## 알림 형식

Discord 알림에는 다음 정보가 포함됩니다:

- 📧 **제목**: 이메일 제목
- **보낸 사람**: 발신자 이름 및 이메일
- **날짜**: 수신 시간
- **미리보기**: 이메일 내용 미리보기 (200자)
- **링크**: Gmail에서 바로 보기

## 문제 해결

### "credentials.json 파일이 필요합니다"

Google Cloud Console에서 OAuth2 클라이언트 ID를 생성하고 JSON을 다운로드하세요.

### "403 오류: access_denied"

OAuth 동의 화면에서 테스트 사용자를 추가하세요. (사전 준비 3단계 참고)

### "Discord 웹훅 URL이 설정되지 않았습니다"

`.env` 파일에 `DISCORD_WEBHOOK_URL`을 설정하세요.

### 알림이 오지 않음

1. `.env`에서 `IMPORTANT_ONLY=true`로 설정한 경우, Gmail이 중요하다고 판단한 메일만 알림이 갑니다.
2. Gmail에서 수동으로 중요 표시를 한 메일이 있는지 확인하세요.
3. `IMPORTANT_ONLY=false`로 설정하면 모든 메일에 알림이 갑니다.

### 토큰 만료 오류

`token.json` 파일을 삭제하고 다시 실행하세요. 브라우저에서 재인증이 필요합니다.

## 로그 확인

```bash
# 실시간 로그 확인
tail -f gmail_monitor.log

# Windows PowerShell
Get-Content gmail_monitor.log -Wait
```

## 주의사항

- Gmail API에는 일일 사용량 한도가 있습니다 (기본 10억 quota units/day).
- 폴링 간격을 너무 짧게 설정하면 API 한도에 도달할 수 있습니다.
- `credentials.json`과 `token.json`은 민감한 정보이므로 git에 커밋하지 마세요.

## 라이선스

MIT License
