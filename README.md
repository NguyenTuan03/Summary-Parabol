<p align="center">
  <img src="icon.png" width="128" height="128" alt="PR Report Logo">
</p>

<h1 align="center">PR Report</h1>

<p align="center">
  <strong>Ứng dụng macOS tự động tổng hợp GitHub Pull Request & báo cáo Daily Standup / Parabol bằng Local AI</strong>
</p>

<p align="center">
  <a href="https://github.com/NguyenTuan03/Summary-Parabol/releases/latest">
    <img src="https://img.shields.io/github/v/release/NguyenTuan03/Summary-Parabol?style=for-the-badge&logo=github&color=7C3AED&logoColor=white" alt="Latest Release">
  </a>
  <img src="https://img.shields.io/badge/Platform-macOS-black?style=for-the-badge&logo=apple&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.11%20|%203.12%20|%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <a href="https://github.com/NguyenTuan03/Summary-Parabol/actions/workflows/release.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/NguyenTuan03/Summary-Parabol/release.yml?style=for-the-badge&label=Build&logo=githubactions&logoColor=white" alt="Build Status">
  </a>
</p>

---

## 💡 Giới thiệu

Mỗi buổi sáng họp **Daily Standup** hoặc viết cập nhật trên **Parabol / Slack / Notion**, các lập trình viên thường mất thời gian mở từng Pull Request trên GitHub để nhớ lại hôm qua mình đã làm những gì.

**PR Report** sinh ra để giải quyết vấn đề đó:
1. **Tự động quét**: Quét tất cả commit và PR của bạn được tạo từ `00:00` sáng hôm nay trên GitHub.
2. **Local AI tóm tắt**: Gửi dữ liệu vào AI CLI có sẵn trên máy (**Claude Code** hoặc **Antigravity**) để tóm tắt thành 3–4 gạch đầu dòng súc tích theo chuẩn standup.
3. **Định dạng sẵn sàng**: Sử dụng ký tự bullet chuẩn (`•`), tự động sao chép vào bộ nhớ tạm (Clipboard) và kích hoạt tab **Parabol** trên trình duyệt để bạn chỉ việc nhấn dán (`⌘V`).

---

## ✨ Tính năng nổi bật

* ⚡ **Quét GitHub tự động**: Sử dụng GitHub CLI (`gh`) để lấy danh sách commit từ các PR do bạn tạo hoặc cập nhật trong ngày.
* 🤖 **Tóm tắt bằng Local AI (Zero Token Cost)**:
  * Ưu tiên dùng **Claude Code CLI** (`claude`), tự động fallback sang **Antigravity CLI** (`agy`).
  * Sử dụng phiên đăng nhập có sẵn trên máy — **không cần cấu hình API key**, không phát sinh chi phí token.
* 📋 **Đồng bộ Clipboard & Định dạng chuẩn**:
  * Nội dung tóm tắt được chuẩn hóa với bullet point (`•`), sẵn sàng dán trực tiếp vào Parabol, Slack, Discord.
  * Tự động chuyển tab Parabol đang mở trên trình duyệt (Brave / Chrome / Safari) hoặc mở tab mới nếu chưa có.
* ⚙️ **Cửa sổ Settings & Quản lý Cập nhật (`⌘,`)**:
  * Xem thông tin phiên bản hiện tại.
  * Nút **Check for Updates** kiểm tra phiên bản mới từ GitHub Releases.
  * Xem trước ghi chú phát hành (Changelog) định dạng Markdown ngay trong app.
* 🔄 **In-App Auto Update (Cập nhật 1-Click qua DMG)**:
  * Tự động kiểm tra phiên bản mới ngầm mỗi khi khởi động hoặc làm mới (`⌘R`).
  * Khi có bản mới, hiển thị nút `⬆ Update vX.X.X` nổi bật trên Header.
  * Tải trực tiếp file `.dmg`, tự động mount ngầm, thay thế file `.app` và khởi động lại chỉ với 1 cú click.
* 🎨 **Giao diện macOS hiện đại**: Thiết kế với các nút bo tròn (*Pill Buttons*), bảng màu tím thời thượng, hỗ trợ phím tắt và thao tác mượt mà.

---

## 🚀 Tải về & Cài đặt

### Cách 1: Tải ứng dụng đã đóng gói sẵn (Khuyên dùng)

1. Tải file **`PR-Report-vX.Y.Z.dmg`** từ trang phát hành mới nhất:  
   👉 **[Tải bản mới nhất từ GitHub Releases](https://github.com/NguyenTuan03/Summary-Parabol/releases/latest)**
2. Mở file `.dmg` và kéo biểu tượng **`PR Report`** vào thư mục **`Applications`** (kéo thả cài đặt trực tiếp, không cần giải nén).
3. Mở app từ **Spotlight (`⌘ Space`)** hoặc **Launchpad**.

> [!NOTE]
> **Xử lý cảnh báo mở app lần đầu trên macOS (Gatekeeper):**  
> Vì app là mã nguồn mở độc lập chưa đăng ký chứng chỉ trả phí với Apple Developer, nếu macOS hiện thông báo *"Ứng dụng không thể mở vì chưa xác minh nhà phát triển"*, bạn chỉ cần mở **Terminal** và chạy lệnh sau một lần:
> ```bash
> xattr -cr "/Applications/PR Report.app"
> ```

---

## ⚙️ Yêu cầu trước khi dùng (Prerequisites)

Để ứng dụng có thể lấy dữ liệu GitHub và tóm tắt qua AI, máy Mac của bạn cần có:

1. **GitHub CLI (`gh`)**:
   * Cài đặt qua Homebrew:
     ```bash
     brew install gh
     ```
   * Đăng nhập tài khoản GitHub:
     ```bash
     gh auth login
     ```
2. **AI CLI (Claude Code hoặc Antigravity CLI)**:
   * **Claude Code** (Khuyên dùng):
     ```bash
     npm install -g @anthropic-ai/claude-code
     claude
     ```
   * *Hoặc* **Antigravity CLI** (`agy`).

---

## ⌨️ Phím tắt & Thao tác

| Thao tác | Phím tắt / Vị trí | Mô tả |
| :--- | :--- | :--- |
| **Fetch PRs** | <kbd>⌘</kbd> + <kbd>R</kbd> | Quét và tải lại toàn bộ PR & commit trong ngày từ GitHub |
| **Settings** | <kbd>⌘</kbd> + <kbd>,</kbd> *(hoặc nút ⚙)* | Mở cửa sổ Cài đặt: xem phiên bản, check update và đọc Changelog |
| **Copy summary** | Nút trên giao diện | Sao chép tóm tắt AI (các dòng bullet `•`) vào Clipboard |
| **Copy list** | Nút trên giao diện | Sao chép danh sách tiêu đề commit thô |
| **⬆ Update vX.X.X** | Nút nổi bật trên Header | Tải và tự động nâng cấp ứng dụng lên bản mới nhất |

---

## 📂 Cấu trúc dự án (Architecture)

```text
PR-report/
├── daily_report.py        # Giao diện chính (Tkinter), luồng fetch GitHub, AI tóm tắt & Settings
├── updater.py             # Engine tự động kiểm tra, tải DMG, mount và thay thế app
├── make_icon.py           # Script tạo icon ứng dụng (icon.png & icon.icns)
├── PR Report.spec         # Cấu hình đóng gói PyInstaller cho macOS bundle
└── .github/
    ├── workflows/
    │   ├── release.yml             # CI/CD: Tự động build và phát hành PR-Report-vX.Y.Z.dmg
    │   └── release-drafter.yml     # CI/CD: Tự động duy trì bản nháp Release & phân loại commit
    └── scripts/
        └── update_draft_release.py # Script hỗ trợ tổng hợp changelog và bump semantic version
```

---

## 🛠️ Dành cho Lập trình viên (Chạy từ mã nguồn)

Nếu bạn muốn tùy chỉnh mã nguồn hoặc tự build ứng dụng:

### 1. Khởi chạy trực tiếp
```bash
# Clone repository
git clone https://github.com/NguyenTuan03/Summary-Parabol.git
cd Summary-Parabol

# Đảm bảo Python có hỗ trợ Tkinter (trên Homebrew Python)
brew install python-tk@3.14

# Chạy ứng dụng
python3 daily_report.py
```

### 2. Tự đóng gói thành ứng dụng macOS (`.app` / `.dmg`)
```bash
# Cài đặt công cụ build
pip install pyinstaller pillow

# Tạo icon ứng dụng
python make_icon.py

# Đóng gói với PyInstaller
pyinstaller "PR Report.spec" --noconfirm --clean

# Tạo file DMG cài đặt kéo thả
cd dist
mkdir -p dmg_staging
cp -R "PR Report.app" dmg_staging/
ln -s /Applications dmg_staging/Applications
hdiutil create -volname "PR Report" -srcfolder dmg_staging -ov -format UDZO "PR-Report-local.dmg"
rm -rf dmg_staging
```

---

## 📦 Quy trình Tự động Hóa (CI/CD)

Dự án được cấu hình tự động hóa toàn diện với **GitHub Actions**:

* 📝 **Tự động soạn thảo Bản nháp (Release Drafter)**:
  * Mỗi khi có commit mới hoặc PR được merge vào nhánh `main`, workflow sẽ tự động gom các thay đổi vào bản nháp tiếp theo.
  * Tự động phân loại theo danh mục: **🚀 Features**, **🐛 Bug Fixes**, **📝 Documentation**, **🔧 Maintenance**.
  * Tự động dự đoán phiên bản semantic version tiếp theo (ví dụ: `v1.2.1` -> `v1.3.0`).
* 🚀 **Tự động đóng gói & Xuất bản (Release Pipeline)**:
  * Khi bấm **Publish release** trên GitHub, máy ảo macOS runner sẽ tự động build ứng dụng, tiêm số phiên bản vào mã nguồn và đóng gói thành tệp duy nhất **`PR-Report-vX.Y.Z.dmg`**.
  * Đính kèm trực tiếp vào trang GitHub Release trong vòng ~1 phút.

---

<p align="center">
  Được phát triển với ❤️ dành cho các developer muốn tiết kiệm thời gian mỗi buổi sáng.
</p>
