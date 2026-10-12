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
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <a href="https://github.com/NguyenTuan03/Summary-Parabol/actions/workflows/release.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/NguyenTuan03/Summary-Parabol/release.yml?style=for-the-badge&label=Build&logo=githubactions&logoColor=white" alt="Build Status">
  </a>
</p>

---

## 💡 Giới thiệu

Mỗi buổi sáng họp **Daily Standup** hoặc viết cập nhật trên **Parabol / Notion**, các lập trình viên thường mất thời gian mở từng Pull Request trên GitHub để nhớ lại hôm qua mình đã làm những gì.

**PR Report** sinh ra để giải quyết vấn đề đó:
1. Tự động quét tất cả các commit và PR của bạn được tạo từ `00:00` sáng hôm nay.
2. Gửi dữ liệu vào AI CLI có sẵn trên máy (**Claude Code** hoặc **Antigravity**) để tóm tắt thành 3–4 dòng súc tích theo chuẩn standup.
3. Tự động copy nội dung vào clipboard và mở sẵn tab **Parabol** trên trình duyệt để bạn chỉ việc dán (`⌘V`).

---

## ✨ Tính năng nổi bật

* ⚡ **Quét GitHub tự động**: Sử dụng GitHub CLI (`gh`) để lấy danh sách commit từ các PR do chính bạn tạo/cập nhật trong ngày.
* 🤖 **Tóm tắt bằng Local AI**:
  * Ưu tiên dùng **Claude Code CLI** (`claude`), dự phòng chuyển sang **Antigravity CLI** (`agy`).
  * Sử dụng session tài khoản AI đã đăng nhập sẵn trên máy — **không cần cấu hình API key**, không tốn chi phí token phát sinh.
* 📋 **Đồng bộ Clipboard & Parabol**:
  * Tự động sao chép kết quả tóm tắt vào bộ nhớ tạm.
  * Tự động nhảy tới tab Parabol đang mở trên trình duyệt (Brave / Chrome) hoặc mở tab mới nếu chưa có.
* 🔄 **In-App Auto Update (Tự cập nhật 1-Click)**:
  * Ứng dụng tự động kiểm tra phiên bản mới từ GitHub Releases khi khởi động.
  * Khi có bản mới, nút `⬆ Update vX.X.X` sẽ xuất hiện trên Header. Bấm vào là app tự tải về, thay thế và khởi động lại.
* 🎨 **Giao diện macOS hiện đại**: Thiết kế với các nút bo tròn (*Pill Buttons*), bảng màu tím thời thượng, hỗ trợ phím tắt `⌘R`.

---

## 🚀 Tải về & Cài đặt

### Cách 1: Tải ứng dụng đã đóng gói sẵn (Khuyên dùng)

1. Tải file **`PR-Report.dmg`** từ phiên bản mới nhất tại:  
   👉 **[Tải bản mới nhất từ GitHub Releases](https://github.com/NguyenTuan03/Summary-Parabol/releases/latest)**
2. Mở file `.dmg` và kéo biểu tượng **`PR Report`** vào thư mục **`Applications`** (không cần giải nén).
3. Mở app từ **Spotlight (⌘ Space)** hoặc **Launchpad**.

> [!NOTE]
> **Xử lý cảnh báo mở app lần đầu trên macOS (Gatekeeper):**  
> Vì app là mã nguồn mở độc lập chưa đăng ký chứng chỉ trả phí với Apple, nếu macOS hiện thông báo *"Ứng dụng không thể mở vì chưa xác minh nhà phát triển"*, bạn chỉ cần mở **Terminal** và chạy lệnh sau một lần duy nhất:
> ```bash
> xattr -cr "/Applications/PR Report.app"
> ```

---

## ⚙️ Yêu cầu trước khi dùng (Prerequisites)

Để ứng dụng hoạt động trơn tru, máy Mac của bạn cần có:

1. **GitHub CLI (`gh`)**:
   * Cài đặt qua Homebrew: `brew install gh`
   * Đăng nhập tài khoản GitHub:
     ```bash
     gh auth login
     ```
2. **AI CLI (Claude Code hoặc Antigravity CLI)**:
   * **Claude Code**: Cài đặt `npm install -g @anthropic-ai/claude-code` và chạy lệnh `claude` để đăng nhập.
   * *Hoặc* **Antigravity CLI** (`agy`).

---

## ⌨️ Phím tắt & Thao tác

| Thao tác | Mô tả |
| :--- | :--- |
| <kbd>⌘</kbd> + <kbd>R</kbd> | Tải lại toàn bộ PR và commit trong ngày từ GitHub |
| **Copy summary** | Sao chép nội dung tóm tắt (3–4 gạch đầu dòng AI) vào Clipboard |
| **Copy list** | Sao chép danh sách tiêu đề commit thô |
| **⬆ Update vX.X.X** | Cập nhật ứng dụng lên phiên bản mới nhất |

---

## 🛠️ Dành cho Lập trình viên (Chạy từ mã nguồn)

Nếu bạn muốn chỉnh sửa mã nguồn hoặc tự build app:

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

### 2. Tự đóng gói thành ứng dụng macOS (`.app`)
```bash
# Cài đặt công cụ build
pip install pyinstaller pillow

# Tạo icon ứng dụng
python make_icon.py

# Đóng gói với PyInstaller
pyinstaller "PR Report.spec" --noconfirm --clean
```
File ứng dụng sau khi build sẽ nằm tại thư mục `dist/PR Report.app`.

---

## 📦 Quy trình Tự động Hóa (CI/CD)

Dự án được cấu hình quy trình CI/CD chuyên nghiệp với **GitHub Actions**:
* **Release Drafter**: Mỗi khi PR được merge vào nhánh `main`, hệ thống tự động soạn sẵn một bản nháp Release tiếp theo kèm theo danh sách thay đổi (Changelog).
* **Auto Build & Release**: Khi bấm **Publish release** trên GitHub, máy ảo macOS sẽ tự động build ứng dụng, đóng gói file `.zip` và đính kèm vào trang Release trong vòng ~1 phút.

---

<p align="center">
  Được phát triển với ❤️ dành cho các developer muốn tiết kiệm thời gian mỗi buổi sáng.
</p>
