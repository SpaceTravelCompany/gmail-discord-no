"""
서비스 중지 스크립트
"""

import os
import sys
import signal

PID_FILE = "gmail_monitor.pid"


def stop():
    """서비스 중지"""
    if not os.path.exists(PID_FILE):
        print("실행 중인 서비스가 없습니다.")
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"서비스 종료됨 (PID: {pid})")
    except OSError:
        print(f"프로세스 {pid}를 찾을 수 없습니다.")

    os.remove(PID_FILE)


if __name__ == "__main__":
    stop()
