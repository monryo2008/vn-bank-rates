# CLAUDE.md — Hướng dẫn dự án VN Bank Exchange Rates

## Quy trình làm việc (BẮT BUỘC)

- Mọi phân tích/điều chỉnh phải đưa plan + giải pháp tóm gọn trước
- Chờ user xác nhận bằng đúng câu **"Confirmed ✓"** mới được thực hiện
- Không ghi đúng câu này thì chỉ tiếp tục trao đổi/phân tích

---

## Tổng quan dự án

Scraper tự động lấy tỷ giá từ ngân hàng Việt Nam, lưu vào `rates.json`, serve qua jsDelivr CDN — **hoàn toàn miễn phí**.

**CDN URL:**
```
https://cdn.jsdelivr.net/gh/monryo2008/vn-bank-rates@main/rates.json
```

---

## Cấu trúc files

```
vn-bank-rates/
├── scraper.py                     # Script scrape chính
├── requirements.txt               # Python dependencies
├── rates.json                     # Output (auto-generated)
├── .github/workflows/scrape.yml   # GitHub Actions (chạy 7AM hàng ngày)
├── CLAUDE.md                      # File này
├── CHANGELOG.md                   # Lịch sử thay đổi
├── LESSON_LEARNED.md              # Bài học kinh nghiệm
├── ENDPOINT_VERIFICATION_REPORT.md # Kết quả verify endpoints
└── PROJECT_OVERVIEW.md            # Overview dự án gốc
```

---

## Trạng thái hiện tại (2026-05-01)

| Bank | Method | Trạng thái | Ghi chú |
|------|--------|-----------|---------|
| Vietcombank | XML API | ✅ Hoạt động | 5 currencies |
| BIDV | HTML scraping | ❌ SSL error | Cần fix `verify_ssl` |
| VietinBank | JSON API | ⏳ Chưa làm | Next.js, cần tìm API ẩn |
| Techcombank | HTML | ⏳ Chưa làm | — |
| MB Bank | HTML | ⏳ Chưa làm | — |
| ACB | HTML | ⏳ Chưa làm | — |
| VPBank | HTML | ⏳ Chưa làm | — |
| Sacombank | HTML | ⏳ Chưa làm | — |

**Currencies MVP:** USD, EUR, JPY, GBP, AUD

---

## Việc cần làm tiếp theo

1. **Fix BIDV** — SSL vẫn lỗi dù đã `verify=False`, cần debug thêm
2. **Thêm VietinBank** — tìm JSON API ẩn qua DevTools Network tab
3. **Mở rộng currencies** — thêm CAD, SGD, CNY, KRW, THB
4. **Mở rộng banks** — Techcombank, MB Bank, ACB, VPBank, Sacombank

---

## Lưu ý kỹ thuật quan trọng

- **GitHub Actions** chạy `cron: '0 0 * * *'` = 7AM GMT+7 hàng ngày
- **Vietcombank rate limit:** 1 request / 5 phút
- **SSL legacy banks:** Một số bank VN dùng TLS cũ → cần `verify=False`
- **JS-rendered pages:** Dùng DevTools Network để tìm API ẩn thay vì scrape HTML
- **Error handling:** Mỗi bank trong `try/except` riêng — 1 lỗi không crash cả script
- **Workflow commit:** Phải `git add` trước rồi mới `git diff --cached`

---

## GitHub repo

- **Repo:** https://github.com/monryo2008/vn-bank-rates
- **Actions:** https://github.com/monryo2008/vn-bank-rates/actions
- **rates.json raw:** https://raw.githubusercontent.com/monryo2008/vn-bank-rates/main/rates.json
- **CDN:** https://cdn.jsdelivr.net/gh/monryo2008/vn-bank-rates@main/rates.json
