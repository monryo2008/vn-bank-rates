# vn-bank-rates

Exchange rate data for Vietnamese banks, updated daily at 7:00 AM Vietnam time.

## CDN URL

```
https://cdn.jsdelivr.net/gh/monryo2008/vn-bank-rates@main/rates.json
```

## Data Format

```json
{
  "updated_at": "2026-05-02T07:00:00+07:00",
  "banks": {
    "vietcombank": {
      "name": "Vietcombank",
      "rates": [
        { "currency": "USD", "buy_cash": 26108, "buy_transfer": 26138, "sell": 26368 },
        { "currency": "EUR", "buy_cash": 30026, "buy_transfer": 30329, "sell": 31633 },
        { "currency": "JPY", "buy_cash": 159, "buy_transfer": 160, "sell": 169 },
        { "currency": "GBP", "buy_cash": 34646, "buy_transfer": 34996, "sell": 36144 },
        { "currency": "AUD", "buy_cash": 18353, "buy_transfer": 18539, "sell": 19147 }
      ],
      "error": false
    }
  }
}
```

## Usage

```javascript
fetch('https://cdn.jsdelivr.net/gh/monryo2008/vn-bank-rates@main/rates.json')
  .then(res => res.json())
  .then(data => {
    console.log(data.updated_at);
    console.log(data.banks.vietcombank.rates);
  });
```

> jsDelivr caches for ~12 hours. Add `?v=timestamp` to bypass cache if needed.

---

*Scraper code is private. Data updates automatically every day.*
