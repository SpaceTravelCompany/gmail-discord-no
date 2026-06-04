"""
Gmail 중요 메일 모니터링 서비스
- 주기적으로 Gmail 확인
- 중요 메일 감지 시 Discord 웹훅으로 알림
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime, timedelta
from typing import Set

from config import POLL_INTERVAL, IMPORTANT_ONLY
from gmail_client import GmailClient
from discord_notifier import DiscordNotifier

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("gmail_monitor.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class GmailMonitor:
    def __init__(self):
        self.gmail_client = None
        self.discord_notifier = None
        self.processed_ids: Set[str] = set()
        self.last_check_time = None
        self.running = True

        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        # Windows 전용 시그널
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """시그널 핸들러 (그레이스풀 셧다운)"""
        logger.info("종료 시그널 수신. 안전하게 종료합니다...")
        self.running = False

    def initialize(self):
        """초기화"""
        logger.info("=" * 50)
        logger.info("Gmail 중요 메일 모니터링 서비스 시작")
        logger.info("=" * 50)

        try:
            logger.info("Gmail API 인증 중...")
            self.gmail_client = GmailClient()
            logger.info("Gmail API 인증 완료")

            logger.info("Discord 웹훅 연결 중...")
            self.discord_notifier = DiscordNotifier()
            logger.info("Discord 웹훅 연결 완료")

            # 시작 메시지 전송
            self.discord_notifier.send_status_message(
                "🟢 **Gmail 모니터링 서비스가 시작되었습니다!**\n"
                f"- 폴링 간격: {POLL_INTERVAL}초\n"
                f"- 중요 메일만: {'예' if IMPORTANT_ONLY else '아니오'}"
            )

            # 초기 메일 ID 로드 (기존 메일은 무시)
            self._load_initial_messages()

            return True

        except FileNotFoundError as e:
            logger.error(f"설정 파일 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"초기화 실패: {e}")
            return False

    def _load_initial_messages(self):
        """초기 메일 ID 로드 (시작 시점의 메일은 무시)"""
        logger.info("기존 메일 로드 중...")

        if IMPORTANT_ONLY:
            messages = self.gmail_client.get_important_messages(max_results=100)
        else:
            messages = self.gmail_client.get_recent_messages(max_results=100)

        for msg in messages:
            self.processed_ids.add(msg["id"])

        logger.info(f"기존 메일 {len(messages)}개 로드 완료 (이 메일들은 무시됩니다)")

        # 마지막 체크 시간 설정
        self.last_check_time = datetime.utcnow()
        logger.info(f"모니터링 시작 시간: {self.last_check_time.isoformat()}Z")

    def run(self):
        """메인 실행 루프"""
        if not self.initialize():
            logger.error("초기화 실패. 프로그램을 종료합니다.")
            sys.exit(1)

        logger.info(f"모니터링 시작. 폴링 간격: {POLL_INTERVAL}초")

        while self.running:
            try:
                self._check_new_emails()
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                time.sleep(POLL_INTERVAL)

        self._shutdown()

    def _check_new_emails(self):
        """새 메일 확인"""
        try:
            # 마지막 체크 시간을 Unix 타임스탬프로 변환
            after_ts = None
            if self.last_check_time:
                after_ts = str(int(self.last_check_time.timestamp()))

            # 메일 가져오기
            if IMPORTANT_ONLY:
                messages = self.gmail_client.get_important_messages(
                    after_timestamp=after_ts
                )
            else:
                messages = self.gmail_client.get_recent_messages(
                    after_timestamp=after_ts
                )

            # 새 메일 필터링
            new_messages = [
                msg for msg in messages if msg["id"] not in self.processed_ids
            ]

            if new_messages:
                logger.info(f"새 메일 {len(new_messages)}개 발견!")

                for msg in new_messages:
                    # 중요 메일만 필터링하는 경우, 중요 표시 확인
                    if IMPORTANT_ONLY and not msg.get("is_important", False):
                        logger.debug(f"중요하지 않은 메일 무시: {msg.get('subject', '')}")
                        self.processed_ids.add(msg["id"])
                        continue

                    # Discord 알림 전송
                    success = self.discord_notifier.send_email_notification(msg)
                    if success:
                        logger.info(f"알림 전송 완료: {msg.get('subject', '')}")

                    # 처리 완료 표시
                    self.processed_ids.add(msg["id"])

                    # API 제한 방지를 위한 딜레이
                    time.sleep(1)
            else:
                logger.debug("새 메일 없음")

            # 마지막 체크 시간 업데이트
            self.last_check_time = datetime.utcnow()

        except Exception as e:
            logger.error(f"메일 확인 중 오류: {e}")

    def _shutdown(self):
        """그레이스풀 셧다운"""
        logger.info("서비스 종료 중...")

        if self.discord_notifier:
            self.discord_notifier.send_status_message(
                "🔴 **Gmail 모니터링 서비스가 종료되었습니다.**"
            )

        logger.info("서비스 종료 완료")


def main():
    """메인 함수"""
    monitor = GmailMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
