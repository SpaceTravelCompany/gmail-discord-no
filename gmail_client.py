"""
Gmail API 클라이언트
- OAuth2 인증
- 중요 메일 모니터링
"""

import os
import json
import base64
from datetime import datetime
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GMAIL_SCOPES


class GmailClient:
    def __init__(self):
        self.service = None
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        """Gmail API 인증"""
        if os.path.exists(GOOGLE_TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(
                GOOGLE_TOKEN_FILE, GMAIL_SCOPES
            )

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"{GOOGLE_CREDENTIALS_FILE} 파일이 필요합니다.\n"
                        "Google Cloud Console에서 OAuth2 클라이언트 ID를 다운로드하세요.\n"
                        "https://console.cloud.google.com/apis/credentials"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_FILE, GMAIL_SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open(GOOGLE_TOKEN_FILE, "w") as token:
                token.write(self.creds.to_json())

        self.service = build("gmail", "v1", credentials=self.creds)

    def get_important_messages(
        self, after_timestamp: Optional[str] = None, max_results: int = 50
    ) -> list:
        """
        중요 메일 가져오기

        Args:
            after_timestamp: 이 시간 이후 메일만 (Unix timestamp)
            max_results: 최대 결과 수

        Returns:
            메일 정보 리스트
        """
        query = "is:important"

        if after_timestamp:
            query += f" after:{after_timestamp}"

        try:
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    maxResults=max_results,
                    labelIds=["INBOX"],
                )
                .execute()
            )

            messages = results.get("messages", [])
            detailed_messages = []

            for msg in messages:
                message_detail = self._get_message_detail(msg["id"])
                if message_detail:
                    detailed_messages.append(message_detail)

            return detailed_messages

        except Exception as e:
            print(f"Gmail API 오류: {e}")
            return []

    def get_recent_messages(
        self, after_timestamp: Optional[str] = None, max_results: int = 50
    ) -> list:
        """
        최근 메일 가져오기 (중요 표시 무시)

        Args:
            after_timestamp: 이 시간 이후 메일만
            max_results: 최대 결과 수

        Returns:
            메일 정보 리스트
        """
        query = ""
        if after_timestamp:
            query = f"after:{after_timestamp}"

        try:
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    maxResults=max_results,
                    labelIds=["INBOX"],
                )
                .execute()
            )

            messages = results.get("messages", [])
            detailed_messages = []

            for msg in messages:
                message_detail = self._get_message_detail(msg["id"])
                if message_detail:
                    detailed_messages.append(message_detail)

            return detailed_messages

        except Exception as e:
            print(f"Gmail API 오류: {e}")
            return []

    def _get_message_detail(self, message_id: str) -> Optional[dict]:
        """메일 상세 정보 가져오기"""
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="metadata")
                .execute()
            )

            headers = message.get("payload", {}).get("headers", [])
            header_dict = {h["name"]: h["value"] for h in headers}

            labels = message.get("labelIds", [])
            is_important = "IMPORTANT" in labels

            return {
                "id": message_id,
                "subject": header_dict.get("Subject", "(제목 없음)"),
                "from": header_dict.get("From", "(발신자 없음)"),
                "to": header_dict.get("To", ""),
                "date": header_dict.get("Date", ""),
                "snippet": message.get("snippet", ""),
                "is_important": is_important,
                "labels": labels,
            }

        except Exception as e:
            print(f"메일 상세 정보 가져오기 실패 ({message_id}): {e}")
            return None

    @staticmethod
    def parse_date_to_timestamp(date_str: str) -> str:
        """날짜 문자열을 Unix 타임스탬프로 변환"""
        try:
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(date_str)
            return str(int(dt.timestamp()))
        except Exception:
            return ""
