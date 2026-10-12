"""
updater.py: Kiểm tra và tự động cập nhật ứng dụng PR Report qua GitHub Releases.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

__version__ = "1.0.0"

REPO_OWNER = "NguyenTuan03"
REPO_NAME = "Summary-Parabol"
API_LATEST_RELEASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"


def parse_version(v: str) -> tuple[int, ...]:
    """Chuyển chuỗi tag 'v1.0.2' -> (1, 0, 2) để so sánh."""
    v = v.lstrip("vV").strip()
    parts = re.split(r"[-+.]", v)
    nums = []
    for p in parts:
        if p.isdigit():
            nums.append(int(p))
        else:
            break
    return tuple(nums) if nums else (0, 0, 0)


def is_newer_version(latest_tag: str, current_version: str) -> bool:
    """Trả về True nếu latest_tag lớn hơn current_version."""
    return parse_version(latest_tag) > parse_version(current_version)


def is_frozen() -> bool:
    """Kiểm tra app có đang chạy dưới dạng bundle PyInstaller hay không."""
    return getattr(sys, "frozen", False)


def get_current_app_bundle() -> str | None:
    """Lấy đường dẫn thư mục .app nếu app đang chạy dưới dạng PyInstaller bundle."""
    if is_frozen():
        # sys.executable: .../PR Report.app/Contents/MacOS/PR Report
        # lùi 2 cấp thư mục: Contents -> PR Report.app
        candidate = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "../.."))
        if candidate.endswith(".app") and os.path.isdir(candidate):
            return candidate
    return None


def check_for_update(current_version: str = __version__) -> dict | None:
    """
    Gọi GitHub API kiểm tra xem có release mới hơn không.
    Trả về dict thông tin nếu có bản mới, ngược lại trả về None.
    """
    try:
        req = urllib.request.Request(
            API_LATEST_RELEASE,
            headers={
                "User-Agent": "PR-Report-Updater",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return None
            data = json.loads(response.read().decode("utf-8"))

        tag_name = data.get("tag_name", "")
        if not tag_name or not is_newer_version(tag_name, current_version):
            return None

        # Tìm asset file .zip trong release
        assets = data.get("assets", [])
        zip_asset = None
        for a in assets:
            name = a.get("name", "")
            if name.endswith(".zip"):
                zip_asset = a
                break

        if not zip_asset:
            return None

        return {
            "version": tag_name,
            "name": data.get("name") or tag_name,
            "download_url": zip_asset.get("browser_download_url"),
            "asset_name": zip_asset.get("name"),
            "size": zip_asset.get("size", 0),
            "html_url": data.get("html_url", ""),
            "body": data.get("body", ""),
        }
    except Exception:
        # Lỗi mạng hoặc rate limit -> bỏ qua trong im lặng
        return None


def download_file(url: str, dest_path: str, progress_callback=None) -> None:
    """Tải file từ URL và lưu vào dest_path với callback cập nhật tiến độ."""
    req = urllib.request.Request(url, headers={"User-Agent": "PR-Report-Updater"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        total_size = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 64 * 1024
        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    progress_callback(percent)


def apply_update(update_info: dict, progress_callback=None) -> None:
    """
    Tải bản cập nhật, giải nén và tự động thay thế app đang chạy.
    """
    download_url = update_info.get("download_url")
    if not download_url:
        raise ValueError("Missing download_url")

    temp_dir = tempfile.mkdtemp(prefix="pr_report_update_")
    zip_path = os.path.join(temp_dir, "update.zip")

    # 1. Tải file zip
    download_file(download_url, zip_path, progress_callback)

    # 2. Giải nén
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)
    shutil.unpack_archive(zip_path, extract_dir)

    # 3. Tìm file .app bên trong thư mục giải nén
    new_app_path = None
    for item in Path(extract_dir).rglob("*.app"):
        new_app_path = str(item)
        break

    if not new_app_path:
        raise RuntimeError("Không tìm thấy file .app trong gói cập nhật")

    current_app = get_current_app_bundle()

    if current_app:
        # Nếu đang chạy dạng .app: Tạo script ngầm để ghi đè và khởi động lại
        pid = os.getpid()
        script_path = os.path.join(temp_dir, "replace_and_restart.sh")
        script_content = f"""#!/bin/bash
# Chờ process cũ tắt hoàn toàn
while kill -0 {pid} 2>/dev/null; do
    sleep 0.2
done

# Thay thế app cũ bằng app mới
rm -rf "{current_app}"
cp -R "{new_app_path}" "{current_app}"

# Gỡ cờ kiểm dịch quarantine của macOS nếu có
xattr -cr "{current_app}" 2>/dev/null || true

# Khởi động lại ứng dụng
open "{current_app}"

# Dọn dẹp thư mục tạm
rm -rf "{temp_dir}"
"""
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)

        # Chạy script độc lập trong session mới
        subprocess.Popen(["/bin/bash", script_path], start_new_session=True, close_fds=True)
        # Thoát process hiện tại ngay lập tức
        os._exit(0)
    else:
        # Nếu đang chạy từ mã nguồn Python (môi trường dev):
        # Mở link GitHub Release và thông báo
        webbrowser.open(update_info.get("html_url", ""))
        raise RuntimeError("Đang chạy từ mã nguồn Python. Vui lòng chạy `git pull` để cập nhật.")
