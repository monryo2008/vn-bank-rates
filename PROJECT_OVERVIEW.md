# 🏦 VN Bank Exchange Rate Aggregator — Project Overview

## Mục tiêu dự án

Build một hệ thống tự động scrape tỷ giá ngoại tệ (mua/bán) từ **8 ngân hàng lớn tại Việt Nam**, lưu kết quả vào `rates.json`, và serve file này qua **jsDelivr CDN** để website frontend có thể fetch hiển thị — toàn bộ **miễn phí, không cần server**.

---

## Kiến trúc hệ thống

```
GitHub Actions (cron: 1 lần/ngày, 7:00 sáng GMT+7)
  └─► scraper.py (Python)
        ├─► Vietcombank   — XML API công khai
        ├─► VietinBank    — HTML scrape
        ├─► BIDV          — HTML scrape
        ├─► Techcombank   — HTML scrape
        ├─► MB Bank       — HTML scrape
        ├─► ACB           — HTML scrape
        ├─► VPBank        — HTML scrape
        └─► Sacombank     — HTML scrape
  └─► rates.json (commit vào repo)
  └─► jsDelivr CDN tự cache → Web frontend fetch
```

---

## Cấu trúc thư mục dự án

```
vn-bank-rates/
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions workflow
├── scraper.py                  # Script scrape chính
├── rates.json                  # Output tự động sinh (đừng sửa tay)
├── requirements.txt            # requests, beautifulsoup4, lxml
└── README.md
```

---

## Chi tiết từng nguồn dữ liệu

| # | Ngân hàng | Phương thức | Endpoint đã biết | Ghi chú |
|---|-----------|-------------|-----------------|---------|
| 1 | **Vietcombank** | XML API | `https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10` | Endpoint công khai, stable nhất |
| 2 | **VietinBank** | HTML scrape | `https://www.vietinbank.vn/en/doanh-nghiep/ty-gia-khdn` | Parse HTML table |
| 3 | **BIDV** | HTML scrape | `https://bidv.com.vn/wps/portal/Home/tỷ-giá` | Parse HTML table |
| 4 | **Techcombank** | HTML scrape | `https://techcombank.com/cong-cu-tien-ich/ty-gia` | Có thể render JS |
| 5 | **MB Bank** | HTML scrape | `https://www.mbbank.com.vn/ty-gia-ngoai-te` | Parse HTML table |
| 6 | **ACB** | HTML scrape | `https://acb.com.vn/cong-cu/ty-gia` | Parse HTML table |
| 7 | **VPBank** | HTML scrape | `https://www.vpbank.com.vn/ca-nhan/tien-ich/ty-gia-ngoai-te` | Parse HTML table |
| 8 | **Sacombank** | HTML scrape | `https://www.sacombank.com.vn/ty-gia.html` | Parse HTML table |

> ⚠️ **Lưu ý quan trọng:** Các endpoint HTML scrape cần được **verify thực tế** khi bắt đầu làm — URL và CSS selector có thể đã thay đổi. Claude Code cần fetch từng trang, inspect HTML, rồi mới viết selector chính xác.

---

## Định dạng output `rates.json`

```json
{
  "updated_at": "2025-01-15T07:00:00+07:00",
  "banks": {
    "vietcombank": {
      "name": "Vietcombank",
      "rates": [
        { "currency": "USD", "buy_cash": 25350, "buy_transfer": 25380, "sell": 25680 },
        { "currency": "EUR", "buy_cash": 26100, "buy_transfer": 26150, "sell": 27100 },
        { "currency": "JPY", "buy_cash": 163,   "buy_transfer": 164,   "sell": 172  }
      ]
    },
    "bidv": {
      "name": "BIDV",
      "rates": [
        { "currency": "USD", "buy_cash": 25340, "buy_transfer": 25370, "sell": 25670 }
      ]
    }
  }
}
```

**Các currency cần lấy (tối thiểu):** USD, EUR, JPY, GBP, AUD, CAD, SGD, CNY, KRW, THB

---

## Yêu cầu kỹ thuật

### Python dependencies (`requirements.txt`)
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

> Không dùng Selenium/Playwright — GitHub Actions free tier không hỗ trợ tốt browser automation. Nếu ngân hàng nào render JS, tìm network request ẩn (thường có JSON API nội bộ) thay vì dùng headless browser.

### GitHub Actions workflow (`scrape.yml`)
- **Trigger:** `schedule: cron: '0 0 * * *'` (0:00 UTC = 7:00 sáng GMT+7)
- **Trigger thủ công:** `workflow_dispatch` (để test)
- **Python version:** 3.11
- **Commit message:** `chore: update rates [timestamp]`
- **Permissions:** cần `contents: write` để commit rates.json

### Error handling
- Mỗi ngân hàng scrape trong **try/except riêng biệt** — 1 ngân hàng lỗi không làm crash cả script
- Nếu scrape lỗi: giữ nguyên data cũ của ngân hàng đó, thêm field `"error": true, "error_msg": "..."`
- Log rõ ràng để dễ debug trong GitHub Actions

---

## Hướng dẫn fetch từ frontend (sau khi deploy)

Sau khi repo có `rates.json`, frontend fetch qua jsDelivr:

```javascript
// Thay YOUR_GITHUB_USERNAME và YOUR_REPO_NAME
const url = 'https://cdn.jsdelivr.net/gh/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME@main/rates.json';

fetch(url)
  .then(res => res.json())
  .then(data => {
    console.log(data.updated_at);
    console.log(data.banks.vietcombank.rates);
  });
```

> jsDelivr cache ~12 giờ. Thêm `?v=` + timestamp nếu cần bust cache:
> `https://cdn.jsdelivr.net/gh/.../rates.json?v=20250115`

---

## Thứ tự thực hiện (cho Claude Code)

1. **Verify endpoints** — fetch từng URL ngân hàng, kiểm tra HTML thực tế, xác nhận cấu trúc table tỷ giá
2. **Viết scraper từng ngân hàng** — bắt đầu từ Vietcombank (XML, dễ nhất), rồi đến các ngân hàng HTML
3. **Test scraper locally** — chạy `python scraper.py`, kiểm tra `rates.json` output
4. **Viết GitHub Actions workflow**
5. **Setup repo & push** — hướng dẫn user tạo GitHub repo, push code, bật Actions
6. **Test workflow thủ công** — trigger `workflow_dispatch` lần đầu để xác nhận chạy được
7. **Cấp quyền write cho Actions** — Settings → Actions → Workflow permissions → Read and write

---

## Ngữ cảnh người dùng

- **Không chuyên về kỹ thuật** — cần giải thích rõ từng bước, tránh assume kiến thức
- **Hệ điều hành:** Windows, dùng Claude Desktop + Claude Code
- **Mục tiêu cuối:** có `rates.json` tự động cập nhật 1 lần/ngày để embed vào website có sẵn
- **Ngân sách:** $0 — chỉ dùng free tier

---

## Lưu ý khi scrape

- Thêm `User-Agent` header vào mọi request để tránh bị block
- Timeout mỗi request: 15 giây
- Nếu ngân hàng trả về 403/block: thử thêm header `Referer` là trang chủ ngân hàng đó
- Một số ngân hàng có thể có **JSON API nội bộ** ẩn — kiểm tra Network tab trong DevTools trước khi scrape HTML
