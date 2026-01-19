"""Sina Finance API service for fetching stock data."""

import requests
import json
import re
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from urllib.parse import quote
from models.quote import Quote
from models.profile import Profile
from models.financial import Financial
from models.structure import Structure, Shareholder
from models.dividend import Dividend
from models.press import Press
from lib.logging import get_logger


logger = get_logger(__name__)


class SinaFinanceService:
    """Service for interacting with Sina Finance APIs."""

    def __init__(self):
        """Initialize Sina Finance service."""
        # Simple session setup like rains - just referer header and proper SSL
        self.session = requests.Session()
        self.session.headers.update({
            'Referer': 'https://finance.sina.com.cn',  # Same as rains
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Enable SSL verification but handle certificate issues gracefully
        self.session.verify = True

    def _configure_ssl(self):
        """Configure SSL settings to handle certificate issues."""
        import urllib3
        import warnings
        import ssl
        import os

        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')

        # Set environment variables
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''

        # Try to create unverified context (this might not work for all cases)
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except Exception as e:
            logger.warning(f"Could not set unverified SSL context: {e}")

        # Monkey patch urllib3 to disable SSL verification
        try:
            import urllib3
            original_init = urllib3.PoolManager.__init__

            def patched_init(self, *args, **kwargs):
                kwargs['cert_reqs'] = 'CERT_NONE'
                # Remove assert_hostname as it's not supported in newer urllib3 versions
                kwargs.pop('assert_hostname', None)
                return original_init(self, *args, **kwargs)

            urllib3.PoolManager.__init__ = patched_init
            logger.info("Successfully patched urllib3 PoolManager to disable SSL verification")
        except Exception as e:
            logger.warning(f"Could not patch urllib3: {e}")

    def _configure_akshare_ssl(self):
        """Configure SSL settings specifically for akshare."""
        try:
            # Set environment variables to disable SSL verification
            import os
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['SSL_CERT_FILE'] = ''

            # Try to disable SSL verification in requests (if akshare uses it)
            try:
                import requests
                # Create a custom adapter that ignores SSL
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry

                class SSLIgnoreAdapter(HTTPAdapter):
                    def init_poolmanager(self, *args, **kwargs):
                        kwargs['cert_reqs'] = 'CERT_NONE'
                        kwargs['assert_hostname'] = False
                        return super().init_poolmanager(*args, **kwargs)

                # Monkey patch requests to use our adapter
                original_session = requests.Session
                def patched_session(*args, **kwargs):
                    session = original_session(*args, **kwargs)
                    session.mount('https://', SSLIgnoreAdapter())
                    session.verify = False
                    return session

                requests.Session = patched_session
                logger.debug("Configured akshare to ignore SSL certificates")

            except ImportError:
                logger.warning("requests not available for akshare SSL configuration")

        except Exception as e:
            logger.warning(f"Could not configure akshare SSL settings: {e}")

    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks by code, name, or pinyin.

        Args:
            query: Search query (code, name, or pinyin)

        Returns:
            List of stock search results with code, name, market info
        """
        try:
            # Sina search API - exact same as rains
            url = f"https://suggest3.sinajs.cn/suggest/type=11,12,15,21,22,23,24,25,26,31,33,41&key={quote(query)}"

            # Simple requests call like rains
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Handle gb2312 encoding for Sina
            if response.encoding != 'utf-8':
                response.encoding = 'gb2312'
                content = response.text
            else:
                content = response.text

            results = []

            # Extract JSON content using regex (exact same as rains)
            import re
            json_match = re.search(r'"([^"]*)"', content)
            if json_match:
                matched = json_match.group(1)
                if matched:
                    # Parse the CSV data (exact same logic as rains)
                    stocks_data = matched.split(';')
                    for stock_str in stocks_data:
                        if not stock_str.strip():
                            continue
                        parts = stock_str.split(',')
                        if len(parts) >= 9:  # Need at least 9 fields like rains
                            # Extract data like rains does
                            market_type = parts[1]
                            code = parts[2]
                            full_code = parts[3].upper()  # This is the symbol field
                            name = parts[4]
                            display_code = parts[0]  # This is used for display

                            # Skip if not in market (like rains checks)
                            if parts[8] != "1":
                                continue

                            # Construct symbol like rains does
                            symbol = full_code
                            if market_type in ["31", "33"]:  # Hong Kong
                                symbol = f"HK{full_code}"
                            elif market_type == "41":  # US stock
                                if not full_code.startswith('$'):
                                    symbol = f"${full_code}"

                            results.append({
                                'full_code': symbol,
                                'name': name,
                                'code': code,
                                'market_type': market_type
                            })

            return results

        except Exception as e:
            logger.error(f"Failed to search stocks for query '{query}': {e}")
            return []

    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote for a stock using direct Sina Finance API like rains.

        Args:
            symbol: Stock symbol (e.g., '000001' or 'SH000001')

        Returns:
            Quote object or None if failed
        """
        try:
            # Use direct Sina Finance API like rains does
            # Normalize symbol to remove exchange prefix
            code = symbol.lstrip('SH').lstrip('SZ').lstrip('BJ').zfill(6)
            # Add exchange prefix back for Sina API
            exchange = self._get_exchange_from_code(code)
            full_symbol = f"{exchange}{code}"

            # Sina quote API - same as rains
            url = f"https://hq.sinajs.cn/list={full_symbol.lower()}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Handle gb2312 encoding for Sina
            if response.encoding != 'utf-8':
                response.encoding = 'gb2312'
                content = response.text
            else:
                content = response.text

            # Parse quote data like rains does - simple regex extraction
            quote_data = self._parse_sina_quote_simple(content, full_symbol)
            if quote_data:
                return quote_data

            logger.warning(f"No quote data found for symbol {symbol}")
            return None

        except Exception as e:
            logger.error(f"Failed to get quote for symbol {symbol}: {e}")
            return None

    def _parse_sina_quote_simple(self, content: str, symbol: str) -> Optional[Quote]:
        """Parse Sina Finance quote data like rains does - simple regex extraction.

        Args:
            content: Raw response content from Sina API
            symbol: Stock symbol

        Returns:
            Quote object or None if parsing failed
        """
        try:
            # Extract quote data using regex like rains does
            import re
            pattern = rf'hq_str_{re.escape(symbol.lower())}="([^"]*)"'
            match = re.search(pattern, content)

            if not match:
                logger.debug(f"No quote data found in response for {symbol}")
                return None

            quote_str = match.group(1)
            logger.debug(f"Extracted quote string: {quote_str}")

            # Parse CSV data like rains does (quote_from_str function)
            values = quote_str.split(',')
            if len(values) < 32:  # Need at least 32 fields
                logger.warning(f"Incomplete quote data for {symbol}: {len(values)} fields")
                return None

            # Extract data like rains (quote_from_str function)
            name = values[0]  # 股票名称
            open_price = self._safe_float(values[1])  # 今开
            close_price = self._safe_float(values[2])  # 昨收
            price = self._safe_float(values[3])  # 当前价格 (最新价)
            high_price = self._safe_float(values[4])  # 最高
            low_price = self._safe_float(values[5])  # 最低
            volume = self._safe_int(values[8])  # 成交量
            turnover = self._safe_float(values[9])  # 成交额

            # Calculate change and change rate
            price_change = None
            price_change_rate = None
            if price is not None and close_price is not None and close_price != 0:
                price_change = price - close_price
                price_change_rate = (price_change / close_price) * 100

            # Extract date and time (not used in Quote model but keep for future)
            date_str = values[30] if len(values) > 30 else None
            time_str = values[31] if len(values) > 31 else None

            market_status = "trading"

            quote = Quote(
                symbol=symbol,
                name=name,
                price=price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                turnover=turnover,
                price_change=price_change,
                price_change_rate=price_change_rate,
                timestamp=datetime.now(),  # Use datetime instead of pd.Timestamp
                market_status=market_status
            )

            logger.info(f"Parsed Sina quote for {symbol}: price={price}")
            return quote

        except Exception as e:
            logger.error(f"Failed to parse Sina quote data for {symbol}: {e}")
            return None

    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int."""
        try:
            return int(float(value)) if value and value != '0' else None
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float."""
        try:
            return float(value) if value and value != '0' and value != '0.0' else None
        except (ValueError, TypeError):
            return None

    def _parse_sina_quote_info(self, content: str, code: str) -> Optional[Dict[str, Any]]:
        """Parse Sina quote info data like rains does for profile method."""
        try:
            result = {}

            # Parse quote data (first part)
            quote_match = re.search(rf'hq_str_{re.escape(code.lower())}="([^"]*)"', content)
            if quote_match:
                quote_str = quote_match.group(1)
                values = quote_str.split(',')
                if len(values) >= 4:
                    result['price'] = self._safe_float(values[3])  # Current price

            # Parse info data (second part with _i suffix)
            info_match = re.search(rf'hq_str_{re.escape(code.lower())}_i="([^"]*)"', content)
            if info_match:
                info_str = info_match.group(1)
                info_values = info_str.split(',')
                if len(info_values) >= 20:
                    # Extract financial data like rains does
                    vps = self._safe_float(info_values[5])  # 每股净资产
                    cap = self._safe_float(info_values[7])   # 总股本
                    traded_cap = self._safe_float(info_values[8])  # 流通市值
                    profit = self._safe_float(info_values[18])  # 净利润

                    price = result.get('price')
                    if price is not None and vps is not None and vps > 0:
                        pb_ratio = price / vps
                        if pb_ratio != float('inf') and not math.isnan(pb_ratio):
                            result['pb_ratio'] = round(pb_ratio, 2)
                        else:
                            result['pb_ratio'] = None

                    # Market cap calculation
                    if price is not None and cap is not None:
                        result['market_cap'] = price * cap * 10000.0  # Convert to yuan

                    if price is not None and traded_cap is not None:
                        result['traded_market_cap'] = price * traded_cap * 10000.0  # Convert to yuan

                    # PE ratio calculation
                    market_cap = result.get('market_cap')
                    if profit is not None and profit > 0 and market_cap is not None:
                        pe_ratio = market_cap / profit / 100000000.0
                        if pe_ratio != float('inf') and not math.isnan(pe_ratio):
                            result['pe_ratio'] = round(pe_ratio, 2)
                        else:
                            result['pe_ratio'] = None

                    # Extract category/industry
                    if len(info_values) > 34:
                        result['category'] = info_values[34]

            return result if result else None

        except Exception as e:
            logger.error(f"Failed to parse Sina quote info for {code}: {e}")
            return None

    def get_profile(self, symbol: str) -> Optional[Profile]:
        """Get company profile information using rains-style simple approach.

        Args:
            symbol: Stock symbol

        Returns:
            Profile object or None if failed
        """
        try:
            # Use the same approach as rains - simple Sina data collection
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            profile_data = {
                'symbol': symbol,
                'name': symbol,  # Default to symbol, will be updated
                'used_name': None,
                'listing_date': None,
                'listing_price': None,
                'industry': None,
                'business': None,
                'address': None,
                'website': None,
                'price': None,
                'pb_ratio': None,
                'pe_ratio': None,
                'market_cap': None,
                'traded_market_cap': None,
            }

            # Get profile data from Sina HTML page like rains does
            self._get_sina_profile_data_simple(code, profile_data)

            # If we couldn't get the company name from HTML, try to get it from quote
            if profile_data['name'] == symbol:
                try:
                    quote = self.get_quote(symbol)
                    if quote and quote.name:
                        profile_data['name'] = quote.name
                        logger.debug(f"Using company name from quote: {profile_data['name']}")
                except Exception as e:
                    logger.warning(f"Failed to get company name from quote: {e}")

            # Create Profile object
            profile = Profile(
                symbol=profile_data['symbol'],
                name=profile_data['name'],
                english_name=None,
                used_name=profile_data['used_name'],
                listing_date=profile_data['listing_date'],
                listing_price=profile_data['listing_price'],
                industry=profile_data['industry'],
                business=profile_data['business'],
                market_cap=profile_data['market_cap'],
                traded_market_cap=profile_data['traded_market_cap'],
                pe_ratio=profile_data['pe_ratio'],
                pb_ratio=profile_data['pb_ratio'],
                eps=None,
                bps=None,
                total_shares=None,
                circulating_shares=None,
                website=profile_data['website'],
                address=profile_data['address'],
                phone=None
            )

            return profile

        except Exception as e:
            logger.error(f"Failed to get profile for symbol {symbol}: {e}")
            return None

    def _get_sina_profile_data_simple(self, code: str, profile_data: Dict[str, Any]) -> None:
        """Get profile data from Sina HTML page using simple regex parsing like rains."""
        try:
            # Sina company profile page (same as rains)
            corp_url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{code}.phtml"

            response = requests.get(corp_url, timeout=10)
            response.raise_for_status()

            # Handle gb2312 encoding for Sina pages
            if response.encoding != 'utf-8':
                response.encoding = 'gb2312'
                html_content = response.text
            else:
                html_content = response.text

            # Simple regex extraction like rains does - much faster than BeautifulSoup
            # Extract company name - updated pattern for Sina's current HTML structure
            name_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*公司名称\s*：</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if name_match:
                profile_data['name'] = name_match.group(1).strip()
                logger.debug(f"Found company name: {profile_data['name']}")
            else:
                logger.warning("Company name regex did not match")
                # Try a broader pattern
                alt_name_match = re.search(r'公司名称[：:]\s*([^<\n]+)', html_content)
                if alt_name_match:
                    profile_data['name'] = alt_name_match.group(1).strip()
                    logger.debug(f"Found company name with alt pattern: {profile_data['name']}")
                else:
                    logger.warning("Company name not found with any pattern")

            # Extract listing date (position 7 in rains)
            date_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*上市日期\s*：</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if date_match:
                try:
                    from datetime import datetime
                    date_str = date_match.group(1).strip()
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    profile_data['listing_date'] = parsed_date
                except (ValueError, TypeError):
                    pass

            # Extract IPO price (position 9 in rains)
            price_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*发行价格\s*：</td>\s*<td[^>]*>([0-9.]+)</td>', html_content)
            if price_match:
                try:
                    profile_data['listing_price'] = float(price_match.group(1))
                except (ValueError, TypeError):
                    pass

            # Extract website (position 35 in rains)
            website_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*公司网址\s*：</td>\s*<td[^>]*><a[^>]*href="([^"]+)"', html_content)
            if website_match:
                profile_data['website'] = website_match.group(1).strip()

            # Extract used name/company name history (position 41 in rains)
            used_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*简称历史\s*：</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if used_match:
                used_name = used_match.group(1).strip()
                if used_name and used_name != '暂无数据':
                    profile_data['used_name'] = used_name

            # Extract business address (position 45 in rains)
            addr_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*办公地址\s*：</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if addr_match:
                profile_data['address'] = addr_match.group(1).strip()

            # Extract main business (position 49 in rains)
            business_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*主营业务\s*：</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if business_match:
                profile_data['business'] = business_match.group(1).strip()

            # Extract industry/category
            industry_match = re.search(r'<td[^>]*class="ct"[^>]*>\s*行业分类\s*：</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if industry_match:
                profile_data['industry'] = industry_match.group(1).strip()

            # Get quote info for financial ratios (like rains does)
            full_symbol = f"sh{code}"  # Add exchange prefix
            info_url = f"https://hq.sinajs.cn/list={full_symbol},{full_symbol}_i"

            try:
                info_response = requests.get(info_url, timeout=10, headers={
                    'Referer': 'https://finance.sina.com.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                info_response.raise_for_status()

                if info_response.encoding != 'utf-8':
                    info_response.encoding = 'gb2312'
                    info_content = info_response.text
                else:
                    info_content = info_response.text

                # Parse quote data like rains does
                quote_data = self._parse_sina_quote_info(info_content, full_symbol)
                if quote_data:
                    profile_data['price'] = quote_data.get('price')
                    profile_data['pb_ratio'] = quote_data.get('pb_ratio')
                    profile_data['pe_ratio'] = quote_data.get('pe_ratio')
                    profile_data['market_cap'] = quote_data.get('market_cap')
                    profile_data['traded_market_cap'] = quote_data.get('traded_market_cap')

            except Exception as e:
                logger.warning(f"Failed to get quote info for {code}: {e}")
                # Try to get current price from basic quote API instead
                try:
                    quote = self.get_quote(f"SH{code}")
                    if quote:
                        profile_data['price'] = quote.price
                        # We can't get financial ratios without the _i API, so leave them as None
                except Exception as e2:
                    logger.warning(f"Failed to get basic quote for {code}: {e2}")

        except Exception as e:
            logger.warning(f"Failed to get Sina profile data for {code}: {e}")

    def _get_financial_data_from_akshare(self, symbol: str, profile_data: Dict[str, Any]) -> None:
        """Get financial data from akshare instead of Sina CSV API.

        Args:
            symbol: Stock symbol
            profile_data: Profile data dictionary to update
        """
        try:
            # Use akshare for reliable financial data
            import akshare as ak

            # Get PB ratio
            try:
                pb_df = ak.stock_zh_valuation_baidu(symbol.replace('SH', '').replace('SZ', '').replace('BJ', ''), '市净率')
                if not pb_df.empty:
                    profile_data['pb_ratio'] = float(pb_df.iloc[0]['value'])
            except Exception as e:
                logger.warning(f"Failed to get PB ratio for {symbol}: {e}")

            # Get PE ratio (TTM)
            try:
                pe_df = ak.stock_zh_valuation_baidu(symbol.replace('SH', '').replace('SZ', '').replace('BJ', ''), '市盈率(TTM)')
                if not pe_df.empty:
                    profile_data['pe_ratio'] = float(pe_df.iloc[0]['value'])
            except Exception as e:
                logger.warning(f"Failed to get PE ratio for {symbol}: {e}")

            # Get current price as fallback
            try:
                price_df = ak.stock_zh_valuation_baidu(symbol.replace('SH', '').replace('SZ', '').replace('BJ', ''), '最新价')
                if not price_df.empty:
                    profile_data['price'] = float(price_df.iloc[0]['value'])
            except Exception as e:
                logger.warning(f"Failed to get current price for {symbol}: {e}")

        except Exception as e:
            logger.warning(f"Failed to get akshare financial data for {symbol}: {e}")

    def _calculate_financial_ratios(self, profile_data: Dict[str, Any]) -> None:
        """Calculate financial ratios like rains does."""
        try:
            # Calculate market capitalization if we have the data
            # This is a simplified version - rains has more sophisticated calculations
            if profile_data['price'] and profile_data['total_shares']:
                profile_data['market_cap'] = profile_data['price'] * profile_data['total_shares']

            if profile_data['price'] and profile_data['circulating_shares']:
                profile_data['traded_market_cap'] = profile_data['price'] * profile_data['circulating_shares']

            # PE ratio calculation would require profit data
            # This is simplified - rains does more complex calculations

            logger.debug("Calculated financial ratios")

        except Exception as e:
            logger.warning(f"Failed to calculate financial ratios: {e}")

    def get_financials(self, symbol: str) -> List[Financial]:
        """Get financial data for a stock using same approach as rains.

        Args:
            symbol: Stock symbol

        Returns:
            List of Financial objects
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina financial data page - same as rains
            url = f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/{code}.phtml"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.text

            # Parse financial tables like rains does
            financials = self._parse_financials_html(html_content)

            logger.info(f"Retrieved {len(financials)} financial records for {symbol}")
            return financials

        except Exception as e:
            logger.error(f"Failed to get financials for symbol {symbol}: {e}")
            return []

    def _parse_financials_html(self, html_content: str) -> List[Financial]:
        """Parse financial data from Sina HTML like rains does.

        Args:
            html_content: HTML content from Sina financial page

        Returns:
            List of Financial objects
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the financial table like rains does (using CSS selector)
            table = soup.select_one('#FundHoldSharesTable')
            if not table:
                logger.warning("Financial table not found in HTML")
                return []

            # Parse table rows like rains does
            rows = table.select('tr')
            if len(rows) < 2:  # Need at least header + data rows
                logger.warning("Not enough rows in financial table")
                return []

            financials = []
            current_financial = None

            # Skip header row, process data rows
            for row in rows[1:]:
                cells = row.select('td')
                if len(cells) < 12:  # Need 12 columns like rains expects
                    continue

                # Extract data like rains does (12 columns per financial record)
                try:
                    date = cells[0].get_text().strip()
                    total_revenue = self._parse_financial_value(cells[8].get_text().strip())
                    net_profit = self._parse_financial_value(cells[10].get_text().strip())
                    ps_net_assets = self._parse_financial_value(cells[1].get_text().strip())
                    ps_capital_reserve = self._parse_financial_value(cells[3].get_text().strip())

                    # Create financial record
                    financial = Financial(
                        date=date,
                        total_revenue=total_revenue,
                        net_profit=net_profit,
                        ps_net_assets=ps_net_assets,
                        ps_capital_reserve=ps_capital_reserve,
                        total_revenue_rate=0.0,  # Will be calculated later
                        net_profit_rate=0.0       # Will be calculated later
                    )

                    financials.append(financial)

                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse financial row: {e}")
                    continue

            # Calculate growth rates like rains does
            for i in range(len(financials)):
                if i + 4 < len(financials):  # Need previous year data
                    current = financials[i]
                    previous = financials[i + 4]

                    if previous.total_revenue and previous.total_revenue != 0:
                        current.total_revenue_rate = ((current.total_revenue - previous.total_revenue) / previous.total_revenue) * 100.0

                    if previous.net_profit and previous.net_profit != 0:
                        current.net_profit_rate = ((current.net_profit - previous.net_profit) / previous.net_profit) * 100.0

            # Return only the most recent 4 quarters like rains does
            return financials[:4]

        except Exception as e:
            logger.error(f"Failed to parse financials HTML: {e}")
            return []

    def _parse_financial_value(self, value: str) -> Optional[float]:
        """Parse financial value string like rains does.

        Args:
            value: String value from HTML

        Returns:
            Parsed float value or None
        """
        if not value or value.strip() in ('', '-', '--', 'N/A'):
            return None

        try:
            # Remove commas and convert to float
            clean_value = value.replace(',', '').strip()
            return float(clean_value)
        except (ValueError, TypeError):
            return None

    def get_shareholder_structure(self, symbol: str) -> Optional[Structure]:
        """Get shareholder structure information like rains does.

        Args:
            symbol: Stock symbol

        Returns:
            Structure object or None if failed
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina shareholder structure page - same as rains
            url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockHolder/stockid/{code}.phtml"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.text

            # Parse shareholder structure like rains does
            structure = self._parse_shareholder_structure_html(html_content)

            logger.info(f"Retrieved shareholder structure for {symbol}")
            return structure

        except Exception as e:
            logger.error(f"Failed to get shareholder structure for symbol {symbol}: {e}")
            return None

    def _parse_shareholder_structure_html(self, html_content: str) -> Optional[Structure]:
        """Parse shareholder structure from Sina HTML like rains does.

        Args:
            html_content: HTML content from Sina shareholder page

        Returns:
            Structure object or None if parsing failed
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the shareholder table like rains does (Table1)
            table = soup.select_one('#Table1')
            if not table:
                logger.warning("Shareholder table not found in HTML")
                return None

            # Parse table rows like rains does
            rows = table.select('tbody tr')
            if len(rows) < 2:  # Need at least header + data rows
                logger.warning("Not enough rows in shareholder table")
                return None

            structures = []
            current_structure = None

            # Process rows like rains does (17 rows per structure record)
            for i, row in enumerate(rows):
                cells = row.select('td')
                if len(cells) < 2:
                    continue

                match i % 17:  # rains processes 17 rows per shareholder structure
                    case 0:  # Date row
                        if current_structure:
                            structures.append(current_structure)
                        current_structure = Structure(date=cells[0].get_text().strip())
                        current_structure.holders_ten = []

                    case 3:  # Holders number
                        if current_structure:
                            current_structure.holders_num = self._parse_financial_value(cells[0].get_text().strip())

                    case 4:  # Average shares
                        if current_structure:
                            current_structure.shares_avg = self._parse_financial_value(cells[0].get_text().strip())

                    case i if 6 <= i <= 15:  # Top 10 holders (rows 6-15)
                        if current_structure and current_structure.holders_ten is not None and len(cells) >= 4:
                            try:
                                from models.structure import Shareholder
                                holder = Shareholder(
                                    name=cells[1].get_text().strip(),
                                    shares=self._parse_financial_value(cells[2].get_text().strip()) or 0.0,
                                    percent=self._parse_financial_value(cells[3].get_text().strip()) or 0.0,
                                    shares_type=cells[4].get_text().strip() if len(cells) > 4 else ""
                                )
                                current_structure.holders_ten.append(holder)
                            except (ValueError, IndexError) as e:
                                logger.warning(f"Failed to parse shareholder row: {e}")
                                continue

            # Add the last structure
            if current_structure:
                structures.append(current_structure)

            # Return the most recent structure like rains does
            return structures[0] if structures else None

        except Exception as e:
            logger.error(f"Failed to parse shareholder structure HTML: {e}")
            return None

    def get_dividends(self, symbol: str) -> List[Dividend]:
        """Get dividend history for a stock like rains does.

        Args:
            symbol: Stock symbol

        Returns:
            List of Dividend objects
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina dividend page - same as rains
            url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{code}.phtml"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.text

            # Parse dividend table like rains does
            dividends = self._parse_dividends_html(html_content)

            logger.info(f"Retrieved {len(dividends)} dividend records for {symbol}")
            return dividends

        except Exception as e:
            logger.error(f"Failed to get dividends for symbol {symbol}: {e}")
            return []

    def _parse_dividends_html(self, html_content: str) -> List[Dividend]:
        """Parse dividend data from Sina HTML like rains does.

        Args:
            html_content: HTML content from Sina dividend page

        Returns:
            List of Dividend objects
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the dividend table like rains does (#sharebonus_1)
            table = soup.select_one('#sharebonus_1')
            if not table:
                logger.warning("Dividend table not found in HTML")
                return []

            # Parse table rows like rains does
            rows = table.select('tr')
            if len(rows) < 2:  # Need at least header + data rows
                logger.warning("Not enough rows in dividend table")
                return []

            dividends = []

            # Skip header row, process data rows
            for row in rows[1:]:
                cells = row.select('td')
                if len(cells) < 9:  # Need 9 columns like rains expects
                    continue

                try:
                    # Extract data like rains does (9 columns per dividend record)
                    date = cells[0].get_text().strip()
                    shares_dividend = self._parse_financial_value(cells[1].get_text().strip()) or 0.0
                    shares_into = self._parse_financial_value(cells[2].get_text().strip()) or 0.0
                    money = self._parse_financial_value(cells[3].get_text().strip()) or 0.0
                    date_dividend = cells[5].get_text().strip()
                    date_record = cells[6].get_text().strip()

                    # Create dividend record
                    dividend = Dividend(
                        date=date,
                        shares_dividend=shares_dividend,
                        shares_into=shares_into,
                        money=money,
                        date_dividend=date_dividend,
                        date_record=date_record
                    )

                    dividends.append(dividend)

                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse dividend row: {e}")
                    continue

            return dividends

        except Exception as e:
            logger.error(f"Failed to parse dividends HTML: {e}")
            return []


    def get_press_releases(self, symbol: str) -> List[Press]:
        """Get company press releases/announcements like rains does.

        Args:
            symbol: Stock symbol

        Returns:
            List of Press objects
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina press releases page - same as rains
            url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllBulletin/stockid/{code}.phtml"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.text

            # Parse press releases like rains does
            presses = self._parse_presses_html(html_content)

            logger.info(f"Retrieved {len(presses)} press releases for {symbol}")
            return presses

        except Exception as e:
            logger.error(f"Failed to get press releases for symbol {symbol}: {e}")
            return []

    def _parse_presses_html(self, html_content: str) -> List[Press]:
        """Parse press releases from Sina HTML like rains does.

        Args:
            html_content: HTML content from Sina press releases page

        Returns:
            List of Press objects
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the press releases list like rains does (.datelist ul)
            ul = soup.select_one('div.datelist ul')
            if not ul:
                logger.warning("Press releases list not found in HTML")
                return []

            presses = []

            # Parse list items like rains does (3 items per press release: date, link+title, empty)
            items = ul.find_all(recursive=False)
            current_press = None

            for i, item in enumerate(items):
                match i % 3:
                    case 0:  # Date
                        if current_press:
                            presses.append(current_press)
                        current_press = Press(
                            date=item.get_text().strip(),
                            title="",
                            url=""
                        )

                    case 1:  # Link and title
                        if current_press:
                            link = item.find('a')
                            if link:
                                current_press.url = f"https://vip.stock.finance.sina.com.cn{link.get('href')}"
                                current_press.title = link.get_text().strip()

            # Add the last press release
            if current_press:
                presses.append(current_press)

            return presses

        except Exception as e:
            logger.error(f"Failed to parse press releases HTML: {e}")
            return []

    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize stock symbol to Sina format.

        Args:
            symbol: Input symbol

        Returns:
            Normalized symbol with exchange prefix
        """
        symbol = symbol.strip()

        # If already has exchange prefix, return as-is
        if symbol.startswith(('SH', 'SZ', 'BJ')):
            return symbol

        # Determine exchange based on code
        exchange = self._get_exchange_from_code(symbol)
        return f"{exchange}{symbol}"

    def _get_exchange_from_code(self, code: str) -> str:
        """Get exchange prefix from stock code.

        Args:
            code: Stock code

        Returns:
            Exchange prefix ('SH', 'SZ', 'BJ')
        """
        code = code.strip()

        # Shanghai Stock Exchange
        if code.startswith(('600', '601', '602', '603', '605', '688', '689', '700', '701', '702', '703', '704', '705', '706', '707', '708', '709', '710', '711', '712', '713', '714', '715', '716', '717', '718', '719', '720', '721', '722', '723', '724', '725', '726', '727', '728', '729', '730', '731', '732', '733', '734', '735', '736', '737', '738', '739', '740', '741', '742', '743', '744', '745', '746', '747', '748', '749', '750', '751', '752', '753', '754', '755', '756', '757', '758', '759', '760', '761', '762', '763', '764', '765', '766', '767', '768', '769', '770', '771', '772', '773', '774', '775', '776', '777', '778', '779', '780', '781', '782', '783', '784', '785', '786', '787', '788', '789', '790', '791', '792', '793', '794', '795', '796', '797', '798', '799')):
            return 'SH'

        # Shenzhen Stock Exchange
        if code.startswith(('000', '001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016', '017', '018', '019', '020', '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '035', '036', '037', '038', '039', '040', '041', '042', '043', '044', '045', '046', '047', '048', '049', '050', '051', '052', '053', '054', '055', '056', '057', '058', '059', '060', '061', '062', '063', '064', '065', '066', '067', '068', '069', '070', '071', '072', '073', '074', '075', '076', '077', '078', '079', '080', '081', '082', '083', '084', '085', '086', '087', '088', '089', '090', '091', '092', '093', '094', '095', '096', '097', '098', '099', '100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '121', '122', '123', '124', '125', '126', '127', '128', '129', '130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '140', '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '151', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176', '177', '178', '179', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189', '190', '191', '192', '193', '194', '195', '196', '197', '198', '199', '200', '201', '202', '203', '204', '205', '206', '207', '208', '209', '210', '211', '212', '213', '214', '215', '216', '217', '218', '219', '220', '221', '222', '223', '224', '225', '226', '227', '228', '229', '230', '231', '232', '233', '234', '235', '236', '237', '238', '239', '240', '241', '242', '243', '244', '245', '246', '247', '248', '249', '250', '251', '252', '253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '277', '278', '279', '280', '281', '282', '283', '284', '285', '286', '287', '288', '289', '290', '291', '292', '293', '294', '295', '296', '297', '298', '299', '300')):
            return 'SZ'

        # Beijing Stock Exchange
        if code.startswith(('8', '9')):
            return 'BJ'

        # Default to Shanghai for unknown codes
        return 'SH'