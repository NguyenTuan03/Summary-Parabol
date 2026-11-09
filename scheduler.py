"""
scheduler.py: Quản lý lịch tự động chạy ứng dụng PR Report lúc 17:15 hàng ngày.
Hỗ trợ cả 2 cơ chế:
1. macOS LaunchAgent (khi app đang tắt): tự động mở ứng dụng lúc 17:15.
2. In-App Watcher (khi app đang mở sẵn): kích hoạt fetch, AI summarize, copy clipboard và mở tab mới.
"""

from __future__ import annotations

import json
import os
import plistlib
import subprocess
import sys
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path

# Cấu hình mặc định
DEFAULT_HOUR = 17
DEFAULT_MINUTE = 15
LAUNCH_AGENT_LABEL = "com.tuan.prreport.scheduler"
PLIST_FILENAME = f"{LAUNCH_AGENT_LABEL}.plist"
PARABOL_URL = "https://action.parabol.co"


class ScheduleStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class TabMode(Enum):
    ALWAYS_NEW = "always_new"
    REUSE_EXISTING = "reuse_existing"


class BrowserType(Enum):
    BRAVE = "Brave Browser"
    CHROME = "Google Chrome"
    DEFAULT = "Default Browser"


class TriggerSource(Enum):
    STARTUP = "startup"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


def get_config_dir() -> Path:
    """Thư mục lưu cấu hình trong Application Support, fallback sang ~/.pr_report hoặc thư mục cục bộ nếu bị chặn quyền."""
    base = Path.home() / "Library" / "Application Support" / "PR Report"
    try:
        base.mkdir(parents=True, exist_ok=True)
        return base
    except OSError:
        pass

    fallback = Path.home() / ".pr_report"
    try:
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
    except OSError:
        pass

    local_fallback = Path(__file__).resolve().parent / ".config"
    local_fallback.mkdir(parents=True, exist_ok=True)
    return local_fallback


def get_config_path() -> Path:
    return get_config_dir() / "schedule_config.json"


def get_launch_agents_dir() -> Path:
    """Thư mục LaunchAgents của người dùng macOS."""
    path = Path.home() / "Library" / "LaunchAgents"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return path


def get_plist_path() -> Path:
    return get_launch_agents_dir() / PLIST_FILENAME


def get_default_config() -> dict:
    return {
        "enabled": True,
        "hour": DEFAULT_HOUR,
        "minute": DEFAULT_MINUTE,
        "tab_mode": TabMode.ALWAYS_NEW.value,
        "last_run_date": "",
    }


def load_config() -> dict:
    config_path = get_config_path()
    if not config_path.exists():
        return get_default_config()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Điền giá trị mặc định nếu thiếu key
            default = get_default_config()
            default.update(data)
            return default
    except Exception:
        return get_default_config()


def save_config(config: dict) -> bool:
    try:
        config_path = get_config_path()
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def has_run_today(last_run_date: str) -> bool:
    if not last_run_date:
        return False
    today_str = datetime.now().strftime("%Y-%m-%d")
    return last_run_date == today_str


def mark_run_today() -> None:
    config = load_config()
    config["last_run_date"] = datetime.now().strftime("%Y-%m-%d")
    save_config(config)


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_app_bundle_path() -> str | None:
    """Tìm đường dẫn bundle .app của PR Report."""
    if is_frozen():
        candidate = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "../.."))
        if candidate.endswith(".app") and os.path.isdir(candidate):
            return candidate

    standard_app = "/Applications/PR Report.app"
    if os.path.isdir(standard_app):
        return standard_app

    user_app = os.path.expanduser("~/Applications/PR Report.app")
    if os.path.isdir(user_app):
        return user_app

    dist_app = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist", "PR Report.app"))
    if os.path.isdir(dist_app):
        return dist_app

    return None


def get_launch_command() -> list[str]:
    """Tạo câu lệnh để macOS LaunchAgent kích hoạt app."""
    app_path = get_app_bundle_path()
    if app_path:
        return ["/usr/bin/open", "-a", app_path]

    # Dự phòng môi trường dev (chạy bằng python script)
    python_bin = sys.executable or "/opt/homebrew/bin/python3"
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "daily_report.py"))
    return [python_bin, script_path]


def generate_plist_dict(hour: int, minute: int) -> dict:
    """Tạo cấu trúc dictionary cho launchd plist."""
    cmd = get_launch_command()
    return {
        "Label": LAUNCH_AGENT_LABEL,
        "ProgramArguments": cmd,
        "StartCalendarInterval": {
            "Hour": hour,
            "Minute": minute,
        },
        "RunAtLoad": False,
        "StandardOutPath": "/tmp/pr_report_scheduler.log",
        "StandardErrorPath": "/tmp/pr_report_scheduler.err",
    }


def is_launch_agent_installed() -> bool:
    return get_plist_path().exists()


def install_launch_agent(hour: int = DEFAULT_HOUR, minute: int = DEFAULT_MINUTE) -> tuple[ScheduleStatus, str]:
    """Cài đặt và nạp file plist vào launchd của macOS."""
    plist_path = get_plist_path()
    plist_data = generate_plist_dict(hour, minute)

    try:
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_data, f)
    except Exception as e:
        return ScheduleStatus.ERROR, f"Không thể ghi file plist: {e}"

    # Unload trước nếu đã từng đăng ký để cập nhật mới
    subprocess.run(["launchctl", "unload", str(plist_path)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    res = subprocess.run(["launchctl", "load", "-w", str(plist_path)],
                         capture_output=True, text=True)
    if res.returncode != 0:
        return ScheduleStatus.ERROR, f"Lỗi nạp launchctl: {res.stderr.strip()}"

    return ScheduleStatus.ENABLED, f"Đã lên lịch thành công lúc {hour:02d}:{minute:02d}"


def remove_launch_agent() -> tuple[ScheduleStatus, str]:
    """Hủy lịch và xóa file LaunchAgent plist."""
    plist_path = get_plist_path()
    if not plist_path.exists():
        return ScheduleStatus.DISABLED, "Lịch chưa được cài đặt."

    subprocess.run(["launchctl", "unload", "-w", str(plist_path)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        plist_path.unlink()
    except Exception as e:
        return ScheduleStatus.ERROR, f"Không thể xóa file plist: {e}"

    return ScheduleStatus.DISABLED, "Đã hủy lịch tự động chạy."


def sync_launch_agent() -> tuple[ScheduleStatus, str]:
    """Đồng bộ trạng thái LaunchAgent theo file config."""
    config = load_config()
    enabled = config.get("enabled", True)
    if not enabled:
        return remove_launch_agent()

    hour = config.get("hour", DEFAULT_HOUR)
    minute = config.get("minute", DEFAULT_MINUTE)
    return install_launch_agent(hour, minute)


def open_parabol_in_browser(mode: TabMode = TabMode.ALWAYS_NEW) -> None:
    """
    Mở Parabol trên trình duyệt (ưu tiên Brave Browser, fallback Chrome, fallback Default Browser).
    - TabMode.ALWAYS_NEW: luôn tạo tab mới.
    - TabMode.REUSE_EXISTING: tìm tab đã mở, nếu không có mới tạo mới.
    """
    script_always_new_brave = f'''
tell application "Brave Browser"
    activate
    if (count of windows) = 0 then
        make new window
        set URL of active tab of window 1 to "{PARABOL_URL}"
    else
        tell window 1 to make new tab with properties {{URL:"{PARABOL_URL}"}}
    end if
end tell
'''

    script_reuse_brave = f'''
tell application "Brave Browser"
    activate
    set found to false
    repeat with w in windows
        set i to 0
        repeat with t in tabs of w
            set i to i + 1
            if URL of t contains "parabol.co" then
                set active tab index of w to i
                set index of w to 1
                set found to true
                exit repeat
            end if
        end repeat
        if found then exit repeat
    end repeat
    if not found then
        if (count of windows) = 0 then make new window
        tell window 1 to make new tab with properties {{URL:"{PARABOL_URL}"}}
    end if
end tell
'''

    script_always_new_chrome = f'''
tell application "Google Chrome"
    activate
    if (count of windows) = 0 then
        make new window
        set URL of active tab of window 1 to "{PARABOL_URL}"
    else
        tell window 1 to make new tab with properties {{URL:"{PARABOL_URL}"}}
    end if
end tell
'''

    selected_brave_script = script_always_new_brave if mode == TabMode.ALWAYS_NEW else script_reuse_brave

    def _worker():
        # 1. Thử Brave Browser
        res = subprocess.run(["osascript", "-e", selected_brave_script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return

        # 2. Thử Google Chrome
        res_chrome = subprocess.run(["osascript", "-e", script_always_new_chrome],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res_chrome.returncode == 0:
            return

        # 3. Fallback trình duyệt mặc định hệ thống
        subprocess.run(["open", PARABOL_URL],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=_worker, daemon=True).start()


class DailySchedulerWatcher:
    """Luồng theo dõi ngầm trong app để kích hoạt đúng giờ khi app đang mở sẵn."""

    def __init__(self, on_trigger_callback) -> None:
        self.on_trigger_callback = on_trigger_callback
        self.running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.running = False

    def _run_loop(self) -> None:
        while self.running:
            time.sleep(20)  # Kiểm tra mỗi 20 giây
            if not self.running:
                return

            config = load_config()
            if not config.get("enabled", True):
                continue

            last_run = config.get("last_run_date", "")
            if has_run_today(last_run):
                continue

            target_hour = config.get("hour", DEFAULT_HOUR)
            target_minute = config.get("minute", DEFAULT_MINUTE)

            now = datetime.now()
            # Kích hoạt khi đồng hồ đạt target_hour và target_minute trở đi
            if now.hour == target_hour and now.minute >= target_minute:
                mark_run_today()
                try:
                    self.on_trigger_callback(TriggerSource.SCHEDULED)
                except Exception:
                    pass
