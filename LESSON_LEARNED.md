# Lesson Learned

## Git & GitHub

### ❌ Sai username gây "Repository not found"
**Vấn đề:** Push liên tục báo `fatal: repository not found` dù repo đã tạo.  
**Nguyên nhân:** Username nhập sai (`moryo2008`, `moryo2088`) thay vì đúng (`monryo2008`).  
**Bài học:** Luôn copy-paste username/URL thẳng từ trang GitHub — đừng gõ tay.

### ❌ `git diff` không detect file mới tạo lần đầu
**Vấn đề:** Workflow chạy thành công nhưng `rates.json` không được commit.  
**Nguyên nhân:** `git diff rates.json` chỉ detect thay đổi của file đã tracked. File mới tạo chưa được `git add` thì `git diff` bỏ qua hoàn toàn.  
**Bài học:** Luôn dùng `git add <file>` trước, rồi check `git diff --cached` thay vì `git diff`.

### ❌ GitHub CLI không nhận ra sau khi cài
**Vấn đề:** `gh` báo "not recognized" ngay sau khi cài thành công.  
**Nguyên nhân:** PATH chưa được cập nhật trong PowerShell session hiện tại.  
**Bài học:** Sau khi cài GitHub CLI (hoặc bất kỳ CLI tool nào), phải **đóng và mở lại PowerShell** mới dùng được.

---

## Web Scraping

### ❌ BIDV SSL legacy error
**Vấn đề:** `SSLError: UNSAFE_LEGACY_RENEGOTIATION_DISABLED` khi fetch BIDV.  
**Nguyên nhân:** Server BIDV dùng TLS cũ không được Python 3.10+ cho phép mặc định.  
**Fix tạm:** `requests.get(url, verify=False)` + `urllib3.disable_warnings()`.  
**Bài học:** Các ngân hàng Việt Nam thường dùng SSL/TLS cũ — cần test SSL trước khi code.

### ❌ HTML scraping không hiệu quả với trang render bằng JavaScript
**Vấn đề:** VietinBank dùng Next.js — `requests` chỉ lấy được HTML shell, không có dữ liệu tỷ giá.  
**Nguyên nhân:** Rates được load bằng JS sau khi trang render.  
**Bài học:** Trước khi scrape HTML, mở DevTools → Network tab → filter XHR/Fetch để tìm API ẩn. Nếu có JSON API thì dùng API thay vì parse HTML.

### ✅ Vietcombank XML API là chuẩn nhất
**Ghi chú:** Vietcombank có XML API công khai, structured, stable. Đây là pattern lý tưởng.  
**Bài học:** Luôn tìm API hoặc XML feed trước, chỉ fallback sang HTML scraping nếu không có.

---

## GitHub Actions

### ❌ `git diff` trong workflow cần `git add` trước
**Vấn đề:** Step "Check if rates.json changed" luôn báo `has_changes=false` với file mới.  
**Fix:** Gộp `git add rates.json` vào trước khi check `git diff --cached`.  
**Bài học:** Trong CI/CD, luôn stage files trước khi check diff.

---

## Quy trình chung

### ✅ Verify endpoint trước khi code
**Bài học:** Luôn thực hiện bước verify endpoint (fetch thực tế, xem HTML) trước khi viết scraper. Tiết kiệm thời gian debug sau này.

### ✅ Dùng try/except riêng cho từng bank
**Bài học:** Mỗi bank scrape trong block `try/except` riêng biệt. Một bank lỗi không được làm crash toàn bộ script.
