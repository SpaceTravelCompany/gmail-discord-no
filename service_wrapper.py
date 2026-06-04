"""
Windows 서비스를 위한 래퍼 모듈
pywin32를 사용하여 Windows 서비스로 실행
"""

import sys
import os

# 서비스로 실행할 경우를 위한 임포트
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager

    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False


if WINDOWS_SERVICE_AVAILABLE:

    class GmailMonitorService(win32serviceutil.ServiceFramework):
        _svc_name_ = "GmailDiscordMonitor"
        _svc_display_name_ = "Gmail Discord Monitor Service"
        _svc_description_ = "Gmail 중요 메일을 모니터링하여 Discord로 알림을 전송합니다."

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self.monitor = None

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)
            if self.monitor:
                self.monitor.running = False

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            self.main()

        def main(self):
            # 작업 디렉토리 설정
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

            from main import GmailMonitor

            self.monitor = GmailMonitor()
            if self.monitor.initialize():
                while self.monitor.running:
                    self.monitor._check_new_emails()
                    win32event.WaitForSingleObject(
                        self.stop_event, 60000  # 60초 대기
                    )
                self.monitor._shutdown()


def install_service():
    """서비스 설치"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("pywin32가 설치되지 않았습니다.")
        print("pip install pywin32")
        return

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GmailMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GmailMonitorService)


if __name__ == "__main__":
    install_service()
