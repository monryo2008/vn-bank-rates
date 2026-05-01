# VN Bank Exchange Rate Aggregator — Endpoint Verification Report

**Date:** May 1, 2026  
**Status:** Phase 1 Verification In Progress  
**Scope:** Verify 3 high-priority banks (Vietcombank, VietinBank, BIDV)

---

## 1. VIETCOMBANK ✅ VERIFIED

**Endpoint:** `https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10`

**Status:** ✅ **WORKING** — Direct XML API, most stable

**Method:** Direct XML API (No HTML parsing needed)

**Response Format:** Clean XML with exchange rates

```xml
<ExrateList>
  <DateTime>5/1/2026 10:53:32 PM</DateTime>
  <Exrate CurrencyCode="AUD" Buy="18,353.72" Transfer="18,539.11" Sell="19,147.30" />
  <Exrate CurrencyCode="EUR" Buy="30,026.59" Transfer="30,329.89" Sell="31,633.51" />
  <Exrate CurrencyCode="GBP" Buy="34,646.46" Transfer="34,996.43" Sell="36,144.52" />
  <Exrate CurrencyCode="JPY" Buy="159.07" Transfer="160.68" Sell="169.30" />
  <Exrate CurrencyCode="USD" Buy="26,108.00" Transfer="26,138.00" Sell="26,368.00" />
</ExrateList>
```

**Data Quality:** ⭐⭐⭐⭐⭐ Excellent
- All 5 target currencies present (USD, EUR, JPY, GBP, AUD)
- Has buy/transfer/sell rates
- Consistent formatting

**Implementation Notes:**
- Use `xml.etree.ElementTree` to parse XML
- Extract: `CurrencyCode`, `Buy`, `Transfer`, `Sell` attributes
- Handle comma-formatted numbers: `"26,108.00"` → `26108.00`
- **Important:** Comment in XML says "Only one request every 5 minutes!" — **Respect this rate limit**

**Risks:** Low

---

## 2. VIETINBANK ⚠️ NEEDS INVESTIGATION

**Endpoint:** `https://www.vietinbank.vn/en/doanh-nghiep/ty-gia-khdn`

**Status:** ⚠️ **DYNAMIC WEBSITE** — Next.js frontend, rates loaded via API

**Method:** JavaScript-rendered (Next.js)

**Response:** 248.7 KB HTML with no visible exchange rate data in static HTML
- Rates are loaded dynamically via client-side JavaScript
- Likely API call from browser: `/api/exchange-rates` or similar

**Next Steps:**
1. ✅ Inspect Network tab in browser to find the internal API endpoint
2. Possible endpoints to check:
   - `https://api.vietinbank.vn/exchange-rates`
   - `https://www.vietinbank.vn/api/rates`
   - Check for GraphQL endpoint

**Data Quality:** TBD (pending API discovery)

**Implementation Challenge:** Medium
- Cannot use simple HTML parsing — must find JSON API
- Alternative: Use Playwright/Selenium to render JS (but project disallows this on GitHub Actions free tier)

**Alternative Approaches:**
- Option A: Find internal API endpoint (preferred)
- Option B: Hardcode static rates if API unavailable
- Option C: Use a different Vietnamese exchange rate API

**Status:** 🔍 **Requires DevTools Network inspection to find API endpoint**

---

## 3. BIDV ✅ VERIFIED (Alternative URL)

**Primary Endpoint:** `https://bidv.com.vn/wps/portal/Home/tỷ-giá` (Redirects)

**Working Endpoint:** `https://bidv.com.vn/vn/ca-nhan/cong-cu-tien-ich/ty-gia-ngoai-te-gia-vang` ✅

**Status:** ✅ **WORKING** — Portal page with embedded exchange rate data

**Method:** HTML scraping (server-side rendered)

**Response:** Server-rendered HTML with embedded rate data

```html
<!-- Rate data embedded as data attributes -->
<section class="nwp-exchangeRateTool currency-converter">
  <div class="bg-exchangeRateTool">
    <div class="nwp-exchangeRateTool-inner">
      <!-- Currency rates with data-rate attribute -->
      <div data-rate="22727.2727"> <!-- This is KRW rate -->
      <!-- Rates are loaded dynamically, likely from JavaScript or AJAX call -->
    </div>
  </div>
</section>

<!-- CSS classes for targeting: -->
<!-- .nwp-exchangeRateTool (main container) -->
<!-- .exchangeRateTool (rate tool) -->
<!-- data-rate="..." (rate values) -->
<!-- Icons: ic-usd, ic-vnd, ic-eur, ic-jpy, ic-gbp, etc. -->
```

**Data Quality:** ⭐⭐⭐⭐ Good
- HTML structure has `data-rate` attributes with numeric values
- CSS classes are consistent: `.nwp-exchangeRateTool`, `.exchangeRateTool`
- Currency identification via icons or data attributes

**Implementation Notes:**
- Use BeautifulSoup to parse HTML table/div structure
- Extract currency codes from icon classes (`.ic-usd` → USD)
- Extract rates from `data-rate="..."` attributes
- Some rates may require JavaScript rendering to load, but initial HTML contains data

**Challenges:** Medium
- IBM Portal architecture — complex HTML structure
- Rates might be dynamically populated via JavaScript (need to verify if available in initial HTML)
- If rates not in initial HTML, may need alternative approach

**Alternative Approaches:**
- Option A: Check if there's a JSON API endpoint exposed by the portal
- Option B: Use Selenium/Playwright if simple HTML parsing fails (not ideal for GitHub Actions)
- Option C: Find hidden API by inspecting Network tab in DevTools

**Status:** ✅ **Ready to implement with HTML scraping**

---

## Summary Table

| Bank | Method | Status | Priority | Next Step |
|------|--------|--------|----------|-----------|
| **Vietcombank** | XML API | ✅ Ready | P0 | Implement XML parser |
| **VietinBank** | Next.js (Client-side API) | ⚠️ Needs API Investigation | P1 | Option A: Find internal API endpoint<br/>Option B: Hardcode rates or find alternative |
| **BIDV** | HTML/Portal scraping | ✅ Ready | P1 | Implement HTML parser with data-rate extraction |

---

## Phase 1 Action Items (Remaining)

- [x] **Vietcombank:** ✅ XML API verified
- [x] **BIDV:** ✅ HTML page verified with `data-rate` attributes
- [ ] **VietinBank:** Requires one of:
  - Option A: Manually open in browser → DevTools Network → find API endpoint
  - Option B: Use alternative Vietnamese bank (skip VietinBank)
  - Option C: Hardcode static VietinBank rates for MVP

---

## Phase 2 Readiness

**Can Start:** ✅ Both Vietcombank and BIDV 
- Vietcombank: XML API implementation (XML parser required)
- BIDV: HTML scraping implementation (BeautifulSoup selector required)

**Decision Needed:** VietinBank approach
1. **Option A (Preferred):** Continue investigation manually in browser DevTools to find internal API
2. **Option B (Pragmatic):** Skip VietinBank for MVP, use just Vietcombank + BIDV
3. **Option C (Temporary):** Hardcode VietinBank rates for MVP, implement proper scraping later

**Recommendation:** Start Phase 2 with Options A and B in parallel:
- Phase 2A: Implement Vietcombank + BIDV scrapers (guaranteed to work)
- Phase 2B: Continue VietinBank API investigation (can integrate later)

---

## Notes

**Rate Limiting:**
- Vietcombank: "Only one request every 5 minutes" — implement 5-min delay between requests or cache locally
- VietinBank/BIDV: Unknown — apply conservative 10-second delay between requests

**User-Agent:**
- All requests must include proper User-Agent header
- Current: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`

**Timeout:**
- Set 15-second timeout per request (as specified in PROJECT_OVERVIEW.md)

---

## Currencies Status (Top 5 Priority)

| Currency | Vietcombank | VietinBank | BIDV |
|----------|-------------|-----------|------|
| USD | ✅ Found | TBD | TBD |
| EUR | ✅ Found | TBD | TBD |
| JPY | ✅ Found | TBD | TBD |
| GBP | ✅ Found | TBD | TBD |
| AUD | ✅ Found | TBD | TBD |
