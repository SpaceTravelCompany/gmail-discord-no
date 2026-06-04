"""
서비스 상태 확인 스크립트
"""

import os
import sys
import psutil


PID_FILE = "gmail_monitor.pid"


def check_status():
    """서비스 실행 상태 확인"""
    print("=" * 40)
    print("Gmail 모니터링 서비스 상태")
    print("=" * 40)
    
    # PID 파일 확인
    if not os.path.exists(PID_FILE):
        print("상태: 미실행 (PID 파일 없음)")
        return False
    
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())
    
    # 프로세스 확인
    try:
        proc = psutil.Process(pid)
        if proc.is_running():
            print(f"상태: 실행 중")
            print(f"PID: {pid}")
            print(f"시작 시간: {proc.create_time()}")
            print(f"메모리: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
            print(f"CPU: {proc.cpu_percent(interval=1)}%")
            
            # 로그 파일 확인
            log_file = "gmail_monitor.log"
            if os.path.exists(log_file):
                size = os.path.getsize(log_file) / 1024
                print(f"로그 파일: {size:.1f} KB")
            
            return True
        else:
            print(f"상태: 프로세스 종료됨 (PID: {pid})")
            os.remove(PID_FILE)
            return False
            
    except psutil.NoSuchProcess:
        print(f"상태: 프로세스 없음 (PID: {pid})")
        os.remove(PID_FILE)
        return False
    except Exception as e:
        print(f"상태 확인 오류: {e}")
        return False


if __name__ == "__main__":
    check_status()
