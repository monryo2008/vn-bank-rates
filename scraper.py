#!/usr/bin/env python3
"""
VN Bank Exchange Rate Aggregator
Scrapes exchange rates from Vietnamese banks and saves to rates.json
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import logging
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Vietnam timezone (UTC+7)
VN_TZ = timezone(timedelta(hours=7))


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """
    Fetch content from URL with error handling.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Response text or None if error
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def parse_number(value: str) -> Optional[float]:
    """Parse Vietnamese formatted number (comma as thousand separator)."""
    if not value or value == '-':
        return None
    try:
        # Remove commas and convert to float
        return float(value.replace(',', ''))
    except ValueError:
        return None


def scrape_vietcombank() -> Dict[str, Any]:
    """
    Scrape Vietcombank exchange rates from XML API.

    **Important:** Vietcombank limits to 1 request per 5 minutes.
    """
    logger.info("Scraping Vietcombank...")

    url = 'https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10'

    result = {
        'name': 'Vietcombank',
        'rates': [],
        'error': False,
        'error_msg': None
    }

    content = fetch_url(url)
    if not content:
        result['error'] = True
        result['error_msg'] = 'Failed to fetch XML data'
        return result

    try:
        root = ET.fromstring(content)

        # Target currencies for MVP
        target_currencies = {'USD', 'EUR', 'JPY', 'GBP', 'AUD'}

        for exrate in root.findall('Exrate'):
            code = exrate.get('CurrencyCode', '').strip()

            if code not in target_currencies:
                continue

            buy_cash = parse_number(exrate.get('Buy', ''))
            buy_transfer = parse_number(exrate.get('Transfer', ''))
            sell = parse_number(exrate.get('Sell', ''))

            if buy_cash is not None and sell is not None:
                result['rates'].append({
                    'currency': code,
                    'buy_cash': buy_cash,
                    'buy_transfer': buy_transfer,
                    'sell': sell
                })

        logger.info(f"Vietcombank: extracted {len(result['rates'])} currencies")

    except ET.ParseError as e:
        logger.error(f"Failed to parse Vietcombank XML: {e}")
        result['error'] = True
        result['error_msg'] = f'XML parse error: {str(e)}'

    return result


def scrape_bidv() -> Dict[str, Any]:
    """
    Scrape BIDV exchange rates from HTML page with data-rate attributes.
    """
    logger.info("Scraping BIDV...")

    url = 'https://bidv.com.vn/vn/ca-nhan/cong-cu-tien-ich/ty-gia-ngoai-te-gia-vang'

    result = {
        'name': 'BIDV',
        'rates': [],
        'error': False,
        'error_msg': None
    }

    content = fetch_url(url)
    if not content:
        result['error'] = True
        result['error_msg'] = 'Failed to fetch HTML page'
        return result

    try:
        soup = BeautifulSoup(content, 'lxml')

        # Currency to icon class mapping for BIDV
        currency_map = {
            'ic-usd': 'USD',
            'ic-eur': 'EUR',
            'ic-jpy': 'JPY',
            'ic-gbp': 'GBP',
            'ic-aud': 'AUD'
        }

        # Find all rate elements with data-rate attribute
        rate_elements = soup.find_all(attrs={'data-rate': True})

        if not rate_elements:
            logger.warning("BIDV: No rate elements found")
            result['error'] = True
            result['error_msg'] = 'No rate data found in HTML'
            return result

        # Try to match currency from parent element classes
        for elem in rate_elements:
            # Look for parent with currency class
            parent = elem.parent
            while parent and parent.name != 'section':
                class_list = parent.get('class', [])
                for class_name in class_list:
                    for icon_class, currency in currency_map.items():
                        if icon_class in class_name:
                            try:
                                rate = float(elem.get('data-rate', 0))
                                if rate > 0:
                                    result['rates'].append({
                                        'currency': currency,
                                        'buy': rate,
                                        'buy_transfer': rate,  # BIDV shows single rate
                                        'sell': rate
                                    })
                            except ValueError:
                                pass
                            break
                parent = parent.parent

        logger.info(f"BIDV: extracted {len(result['rates'])} currencies")

    except Exception as e:
        logger.error(f"Failed to scrape BIDV HTML: {e}")
        result['error'] = True
        result['error_msg'] = f'HTML parse error: {str(e)}'

    return result


def aggregate_rates(vietcombank_data: Dict, bidv_data: Dict) -> Dict[str, Any]:
    """
    Aggregate exchange rates from all banks into final JSON format.
    """
    # Get current time in Vietnam timezone
    now_vn = datetime.now(VN_TZ)

    data = {
        'updated_at': now_vn.isoformat(),
        'banks': {
            'vietcombank': vietcombank_data,
            'bidv': bidv_data
        }
    }

    return data


def main():
    """Main scraper orchestration."""
    logger.info("Starting exchange rate scraper...")

    # Scrape all banks
    vietcombank_data = scrape_vietcombank()
    bidv_data = scrape_bidv()

    # Aggregate data
    rates = aggregate_rates(vietcombank_data, bidv_data)

    # Save to JSON file
    output_file = 'rates.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rates, f, ensure_ascii=False, indent=2)
        logger.info(f"Successfully saved rates to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write {output_file}: {e}")
        return False

    # Log summary
    vietcom_count = len(vietcombank_data.get('rates', []))
    bidv_count = bidv_data.get('rates', [])

    logger.info(f"Scraping complete: Vietcombank ({vietcom_count} currencies), BIDV ({len(bidv_count)} currencies)")

    if vietcombank_data.get('error'):
        logger.warning(f"Vietcombank error: {vietcombank_data.get('error_msg')}")

    if bidv_data.get('error'):
        logger.warning(f"BIDV error: {bidv_data.get('error_msg')}")

    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
