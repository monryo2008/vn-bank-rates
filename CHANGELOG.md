# Changelog

## [0.2.0] — 2026-05-01

### Fixed
- **BIDV SSL error**: Thêm `verify_ssl=False` vào `fetch_url()` để bypass legacy SSL của BIDV (`UNSAFE_LEGACY_RENEGOTIATION_DISABLED`)
- **Workflow không commit `rates.json`**: Đổi từ `git diff rates.json` sang `git add rates.json` trước rồi check `git diff --cached` — fix trường hợp file mới tạo lần đầu chưa được tracked

### Changed
- `scraper.py`: Thêm `urllib3`, `ssl` imports; thêm param `verify_ssl` vào `fetch_url()`
- `.github/workflows/scrape.yml`: Bỏ bước "Check if rates.json changed" riêng, gộp vào "Commit and push updates"

---

## [0.1.0] — 2026-05-01

### Added
- **Endpoint Verification Report** (`ENDPOINT_VERIFICATION_REPORT.md`): Kết quả verify 3 banks
  - Vietcombank XML API ✅
  - BIDV HTML scraping ✅ (URL mới)
  - VietinBank ⚠️ deferred (Next.js dynamic)
- **`scraper.py`**: Scraper cho Vietcombank (XML) và BIDV (HTML)
  - `fetch_url()`: HTTP request với User-Agent header, timeout 15s
  - `scrape_vietcombank()`: Parse XML API, extract 5 currencies
  - `scrape_bidv()`: Parse HTML với `data-rate` attributes
  - `aggregate_rates()`: Gộp kết quả, thêm timestamp UTC+7
- **`requirements.txt`**: `requests`, `beautifulsoup4`, `lxml`
- **`.github/workflows/scrape.yml`**: GitHub Actions chạy hàng ngày 7AM GMT+7
- **`README.md`**: Hướng dẫn setup và sử dụng
- **`.gitignore`**: Loại bỏ temp HTML files, `.claude/`, `__pycache__`

### Notes
- MVP: Vietcombank (5 currencies: USD, EUR, JPY, GBP, AUD) hoạt động
- BIDV: vẫn lỗi SSL sau fix — cần điều tra thêm
- VietinBank: defer sang phase sau
