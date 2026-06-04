"""
Discord 웹훅 알림 모듈
"""

import requests
from datetime import datetime
from typing import Optional

from config import DISCORD_WEBHOOK_URL


class DiscordNotifier:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or DISCORD_WEBHOOK_URL
        if not self.webhook_url:
            raise ValueError(
                "Discord 웹훅 URL이 설정되지 않았습니다.\n"
                ".env 파일에 DISCORD_WEBHOOK_URL을 설정하세요."
            )

    def send_email_notification(self, email_data: dict) -> bool:
        """
        메일 알림 전송

        Args:
            email_data: 메일 정보 딕셔너리

        Returns:
            전송 성공 여부
        """
        try:
            embed = self._create_email_embed(email_data)
            payload = {
                "content": "📬 **새로운 중요 메일이 도착했습니다!**",
                "embeds": [embed],
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 204:
                print(f"Discord 알림 전송 성공: {email_data.get('subject', '')}")
                return True
            else:
                print(f"Discord 알림 전송 실패: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Discord 알림 전송 오류: {e}")
            return False

    def _create_email_embed(self, email_data: dict) -> dict:
        """Discord 임베드 생성"""
        # 발신자 파싱
        sender = email_data.get("from", "(발신자 없음)")
        if "<" in sender and ">" in sender:
            sender_name = sender.split("<")[0].strip()
            sender_email = sender.split("<")[1].rstrip(">").strip()
        else:
            sender_name = sender
            sender_email = sender

        # 날짜 포맷팅
        date_str = email_data.get("date", "")
        try:
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(date_str)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            formatted_date = date_str

        # 스니펫 (미리보기)
        snippet = email_data.get("snippet", "")
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."

        embed = {
            "title": f"📧 {email_data.get('subject', '(제목 없음)')}",
            "color": 0x00FF00,  # 초록색
            "fields": [
                {"name": "보낸 사람", "value": f"{sender_name}\n`{sender_email}`", "inline": True},
                {"name": "날짜", "value": formatted_date, "inline": True},
                {"name": "미리보기", "value": snippet if snippet else "(내용 없음)", "inline": False},
            ],
            "footer": {"text": "Gmail Important Mail Monitor"},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Gmail 링크 추가
        message_id = email_data.get("id", "")
        if message_id:
            embed["fields"].append(
                {
                    "name": "링크",
                    "value": f"[Gmail에서 보기](https://mail.google.com/mail/u/0/#inbox/{message_id})",
                    "inline": False,
                }
            )

        return embed

    def send_status_message(self, message: str) -> bool:
        """상태 메시지 전송"""
        try:
            payload = {"content": message}
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            return response.status_code == 204
        except Exception as e:
            print(f"상태 메시지 전송 오류: {e}")
            return False
