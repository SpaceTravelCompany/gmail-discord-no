"""
백그라운드 실행 스크립트
- 콘솔 없이 백그라운드에서 실행
- PID 파일로 프로세스 관리
"""

import os
import sys
import subprocess
import signal
import psutil

PID_FILE = "gmail_monitor.pid"


def is_process_running(pid):
    """프로세스 실행 여부 확인"""
    try:
        return psutil.Process(pid).is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def start():
    """백그라운드에서 서비스 시작"""
    # PID 파일이 있으면 프로세스 확인
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            if is_process_running(pid):
                print(f"이미 실행 중입니다 (PID: {pid})")
                return
            else:
                os.remove(PID_FILE)
        except (ValueError, FileNotFoundError):
            os.remove(PID_FILE)

    # 스크립트 경로
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    # pythonw.exe 경로 (가상환경 우선)
    venv_pythonw = os.path.join(script_dir, ".venv", "Scripts", "pythonw.exe")
    if os.path.exists(venv_pythonw):
        pythonw = venv_pythonw
    else:
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")

    # 로그 파일
    log_file = os.path.join(script_dir, "gmail_monitor.log")

    # 백그라운드 실행
    process = subprocess.Popen(
        [pythonw, main_script],
        stdout=open(log_file, "a"),
        stderr=subprocess.STDOUT,
        cwd=script_dir,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
    )

    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))

    print(f"서비스 시작됨 (PID: {process.pid})")
    print(f"로그: {log_file}")
    print(f"종료: python stop.py")


def stop():
    """서비스 중지"""
    if not os.path.exists(PID_FILE):
        print("실행 중인 서비스가 없습니다.")
        return

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
    except (ValueError, FileNotFoundError):
        os.remove(PID_FILE)
        print("PID 파일이 손상되어 삭제했습니다.")
        return

    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
        print(f"서비스 종료됨 (PID: {pid})")
    except psutil.NoSuchProcess:
        print(f"프로세스 {pid}를 찾을 수 없습니다.")
    except psutil.TimeoutExpired:
        proc.kill()
        print(f"서비스 강제 종료됨 (PID: {pid})")
    except Exception as e:
        print(f"종료 실패: {e}")

    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop()
    else:
        start()
