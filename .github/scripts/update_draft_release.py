#!/usr/bin/env python3
"""
Tự động tính toán phiên bản tiếp theo và tạo/cập nhật bản Draft Release
bao gồm cả Pull Requests lẫn tất cả commit push trực tiếp vào main.
"""

import json
import os
import re
import subprocess
import sys


def run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}\nStderr: {res.stderr}")
        raise subprocess.CalledProcessError(res.returncode, cmd, res.stdout, res.stderr)
    return res.stdout.strip()


def main() -> None:
    # 1. Lấy tag release gần nhất
    try:
        run(["git", "fetch", "--tags", "--force"])
        latest_tag = run(["git", "describe", "--tags", "--abbrev=0"])
    except Exception:
        latest_tag = "v1.0.0"

    print(f"📌 Latest tag: {latest_tag}")

    # 2. Lấy toàn bộ commits kể từ tag gần nhất (không lấy merge commits)
    commits_raw = run([
        "git", "log", f"{latest_tag}..HEAD",
        "--no-merges",
        "--pretty=format:%h|%an|%s"
    ])

    if not commits_raw.strip():
        print("ℹ️ Không có commit mới kể từ tag gần nhất.")
        return

    commits = [line.split("|", 2) for line in commits_raw.splitlines() if line.strip()]

    # 3. Tính toán phiên bản tiếp theo theo SemVer
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", latest_tag)
    if m:
        major, minor, patch = map(int, m.groups())
    else:
        major, minor, patch = (1, 0, 0)

    has_major = any("BREAKING" in c[2] or "feat!:" in c[2] for c in commits)
    has_minor = any(c[2].startswith("feat") for c in commits)

    if has_major:
        next_tag = f"v{major + 1}.0.0"
    elif has_minor:
        next_tag = f"v{major}.{minor + 1}.0"
    else:
        next_tag = f"v{major}.{minor}.{patch + 1}"

    print(f"🎯 Target version: {next_tag}")

    # 4. Phân nhóm thay đổi
    features = []
    fixes = []
    maintenance = []

    for h, author, msg in commits:
        line = f"* {msg} by @{author} ({h})"
        msg_lower = msg.lower()
        if msg_lower.startswith("feat"):
            features.append(line)
        elif msg_lower.startswith("fix"):
            fixes.append(line)
        else:
            maintenance.append(line)

    body_parts = ["## What's Changed"]
    if features:
        body_parts.append("\n### 🚀 Features")
        body_parts.extend(features)
    if fixes:
        body_parts.append("\n### 🐛 Bug Fixes")
        body_parts.extend(fixes)
    if maintenance:
        body_parts.append("\n### 🧰 Maintenance & Updates")
        body_parts.extend(maintenance)

    repo = os.environ.get("GITHUB_REPOSITORY", "NguyenTuan03/Summary-Parabol")
    body_parts.append(f"\n\n**Full Changelog**: https://github.com/{repo}/compare/{latest_tag}...{next_tag}")
    body = "\n".join(body_parts)

    # 5. Kiểm tra và cập nhật bản nháp (Draft Release)
    releases_json = run(["gh", "release", "list", "--json", "isDraft,tagName,name"])
    try:
        releases = json.loads(releases_json)
    except Exception:
        releases = []

    existing_draft = next((r for r in releases if r.get("isDraft")), None)

    if existing_draft:
        draft_tag = existing_draft["tagName"]
        print(f"🔄 Đang cập nhật bản nháp có sẵn ({draft_tag}) -> {next_tag}...")
        run([
            "gh", "release", "edit", draft_tag,
            "--tag", next_tag,
            "--title", next_tag,
            "--notes", body
        ])
    else:
        print(f"✨ Đang tạo bản nháp mới ({next_tag})...")
        run([
            "gh", "release", "create", next_tag,
            "--draft",
            "--title", next_tag,
            "--notes", body
        ])

    print("✅ Cập nhật Draft Release thành công!")


if __name__ == "__main__":
    main()
