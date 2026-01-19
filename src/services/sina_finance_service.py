"""Sina Finance API service for fetching stock data."""

import requests
import json
import re
import time
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
        self._configure_ssl()
        self.session = requests.Session()
        self.session.verify = False  # Sina Finance often has SSL issues
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })

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
            # Sina search API - construct URL like rains does
            url = f"https://suggest3.sinajs.cn/suggest/type=11,12,15,21,22,23,24,25,26,31,33,41&key={quote(query)}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Parse JSONP response like rains does
            content = response.text.strip()
            results = []

            # Extract JSON content from quotes using regex (like rains)
            import re
            json_match = re.search(r'"([^"]*)"', content)
            if json_match:
                matched = json_match.group(1)
                if matched:
                    # Parse the CSV data
                    stocks_data = matched.split(';')
                    for stock_str in stocks_data:
                        if not stock_str.strip():
                            continue
                        parts = stock_str.split(',')
                        if len(parts) >= 3:
                            code = parts[0]
                            name = parts[1]
                            market_type = parts[2]

                            # Determine exchange from code
                            exchange = self._get_exchange_from_code(code)

                            results.append({
                                'code': code,
                                'name': name,
                                'market_type': market_type,
                                'exchange': exchange,
                                'full_code': f"{exchange}{code}"
                            })

        except Exception as e:
            logger.error(f"Failed to search stocks for query '{query}': {e}")
            return []

    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote for a stock.

        Args:
            symbol: Stock symbol (e.g., '000001' or 'SH000001')

        Returns:
            Quote object or None if failed
        """
        try:
            # Configure SSL for akshare before importing
            self._configure_akshare_ssl()

            import akshare as ak
            import pandas as pd

            # Get real-time data for this stock
            df = ak.stock_zh_a_spot_em()
            # Normalize symbol to 6-digit code
            code = symbol.lstrip('SH').lstrip('SZ').lstrip('BJ').zfill(6)
            df = df[df['代码'] == code]

            if df.empty:
                logger.warning(f"No quote data found for symbol {symbol}")
                return None

            row = df.iloc[0]

            # Extract data
            name = str(row.get('名称', ''))
            price = float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None
            open_price = float(row.get('今开', 0)) if pd.notna(row.get('今开')) else None
            high_price = float(row.get('最高', 0)) if pd.notna(row.get('最高')) else None
            low_price = float(row.get('最低', 0)) if pd.notna(row.get('最低')) else None
            close_price = float(row.get('昨收', 0)) if pd.notna(row.get('昨收')) else None
            volume = int(float(row.get('成交量', 0))) if pd.notna(row.get('成交量')) else None
            turnover = float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else None

            # Calculate change
            price_change = None
            price_change_rate = None
            if price is not None and close_price is not None and close_price != 0:
                price_change = price - close_price
                price_change_rate = (price_change / close_price) * 100

            # Market status (simplified)
            market_status = "trading"  # akshare provides real-time data

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
                timestamp=pd.Timestamp.now(),
                market_status=market_status
            )

            logger.info(f"Retrieved quote for {symbol}: {quote}")
            return quote

        except Exception as e:
            logger.error(f"Failed to get quote for symbol {symbol}: {e}")
            return None

    def get_profile(self, symbol: str) -> Optional[Profile]:
        """Get company profile information.

        Args:
            symbol: Stock symbol

        Returns:
            Profile object or None if failed
        """
        try:
            # Configure SSL for akshare
            self._configure_akshare_ssl()

            import akshare as ak
            import pandas as pd

            # Normalize symbol to 6-digit code
            code = symbol.lstrip('SH').lstrip('SZ').lstrip('BJ').zfill(6)

            profile_data = {
                'symbol': symbol,
                'name': symbol,
                'english_name': None,
                'industry': None,
                'business': None,
                'market_cap': None,
                'pe_ratio': None,
                'pb_ratio': None,
                'eps': None,
                'bps': None,
                'total_shares': None,
                'circulating_shares': None,
                'website': None,
                'address': None,
                'phone': None,
                'listing_date': None
            }

            # Try to get basic individual stock info
            try:
                df_basic = ak.stock_individual_info_em(code)
                if not df_basic.empty:
                    row = df_basic.iloc[0] if len(df_basic) > 0 else {}

                    # Extract basic information
                    profile_data['name'] = str(row.get('股票简称', symbol))
                    profile_data['industry'] = str(row.get('行业', '')) if row.get('行业') else None
                    profile_data['total_shares'] = float(row.get('总股本', 0)) if pd.notna(row.get('总股本')) else None
                    profile_data['circulating_shares'] = float(row.get('流通股', 0)) if pd.notna(row.get('流通股')) else None
                    profile_data['market_cap'] = float(row.get('总市值', 0)) if pd.notna(row.get('总市值')) else None

                    # Try to get listing date
                    if row.get('上市时间'):
                        try:
                            listing_date_str = str(row.get('上市时间', ''))
                            if listing_date_str and listing_date_str != 'None':
                                profile_data['listing_date'] = pd.to_datetime(listing_date_str).date()
                        except:
                            pass

                    logger.debug(f"Retrieved basic info for {symbol} using akshare")
            except Exception as e:
                logger.warning(f"Failed to get basic info for {symbol}: {e}")
                # Continue to other sources instead of failing

            # Skip slow akshare calls and go directly to Sina fallback for better performance
            # Fall back to Sina scraping
            logger.info(f"Falling back to Sina scraping for {symbol}")
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina company profile page
            url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{code}.phtml"

            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                # Handle gb2312 encoding for Sina pages
                if response.encoding != 'utf-8':
                    response.encoding = 'gb2312'
                    html_content = response.text
                else:
                    html_content = response.text

                # Extract basic information using regex patterns
                name = self._extract_from_html(html_content, r'<title>([^<]+)</title>')
                if name:
                    # Clean up the title (remove extra text)
                    name = name.replace('公司资料_新浪财经_新浪网', '').strip()
                    if not profile_data['name'] or profile_data['name'] == symbol:
                        profile_data['name'] = name

                # Extract listing date
                if not profile_data['listing_date']:
                    profile_data['listing_date'] = self._extract_listing_date(html_content)

                # Extract industry
                if not profile_data['industry']:
                    profile_data['industry'] = self._extract_from_html(html_content, r'行业[：:]\s*([^<\n]+)')

                # Extract business description
                if not profile_data['business']:
                    profile_data['business'] = self._extract_business_description(html_content)

                # Extract additional information from Sina page
                # Try to extract market cap
                if not profile_data['market_cap']:
                    market_cap_match = re.search(r'总市值[：:]\s*([0-9,]+\.?\d*)\s*(亿|万)?', html_content, re.IGNORECASE)
                    if market_cap_match:
                        try:
                            value = float(market_cap_match.group(1).replace(',', ''))
                            unit = market_cap_match.group(2)
                            if unit == '亿':
                                value *= 100000000  # Convert to yuan
                            elif unit == '万':
                                value *= 10000
                            profile_data['market_cap'] = value
                        except (ValueError, IndexError):
                            pass

                # Try to extract PE ratio
                if not profile_data['pe_ratio']:
                    pe_match = re.search(r'市盈率[：:]\s*([0-9,]+\.?\d*)', html_content, re.IGNORECASE)
                    if pe_match:
                        try:
                            profile_data['pe_ratio'] = float(pe_match.group(1).replace(',', ''))
                        except (ValueError, IndexError):
                            pass

                # Try to extract PB ratio
                if not profile_data['pb_ratio']:
                    pb_match = re.search(r'市净率[：:]\s*([0-9,]+\.?\d*)', html_content, re.IGNORECASE)
                    if pb_match:
                        try:
                            profile_data['pb_ratio'] = float(pb_match.group(1).replace(',', ''))
                        except (ValueError, IndexError):
                            pass

                # Try to extract EPS
                if not profile_data['eps']:
                    eps_match = re.search(r'每股收益[：:]\s*([0-9,]+\.?\d*)', html_content, re.IGNORECASE)
                    if eps_match:
                        try:
                            profile_data['eps'] = float(eps_match.group(1).replace(',', ''))
                        except (ValueError, IndexError):
                            pass

                # Try to extract BPS
                if not profile_data['bps']:
                    bps_match = re.search(r'每股净资产[：:]\s*([0-9,]+\.?\d*)', html_content, re.IGNORECASE)
                    if bps_match:
                        try:
                            profile_data['bps'] = float(bps_match.group(1).replace(',', ''))
                        except (ValueError, IndexError):
                            pass

                # Try to extract total shares
                if not profile_data['total_shares']:
                    total_shares_match = re.search(r'总股本[：:]\s*([0-9,]+\.?\d*)\s*(亿|万)?', html_content, re.IGNORECASE)
                    if total_shares_match:
                        try:
                            value = float(total_shares_match.group(1).replace(',', ''))
                            unit = total_shares_match.group(2)
                            if unit == '亿':
                                value *= 100000000  # Convert to shares
                            elif unit == '万':
                                value *= 10000
                            profile_data['total_shares'] = value
                        except (ValueError, IndexError):
                            pass

                # Try to extract circulating shares
                if not profile_data['circulating_shares']:
                    circ_shares_match = re.search(r'流通股[：:]\s*([0-9,]+\.?\d*)\s*(亿|万)?', html_content, re.IGNORECASE)
                    if circ_shares_match:
                        try:
                            value = float(circ_shares_match.group(1).replace(',', ''))
                            unit = circ_shares_match.group(2)
                            if unit == '亿':
                                value *= 100000000  # Convert to shares
                            elif unit == '万':
                                value *= 10000
                            profile_data['circulating_shares'] = value
                        except (ValueError, IndexError):
                            pass

                # Try to extract website
                if not profile_data['website']:
                    website_match = re.search(r'网站[：:]\s*(https?://[^\s<]+)', html_content, re.IGNORECASE)
                    if website_match:
                        profile_data['website'] = website_match.group(1).strip()

                # Try to extract address
                if not profile_data['address']:
                    address_match = re.search(r'地址[：:]\s*([^<\n]+)', html_content, re.IGNORECASE)
                    if address_match:
                        profile_data['address'] = address_match.group(1).strip()

                # Try to extract phone
                if not profile_data['phone']:
                    phone_match = re.search(r'电话[：:]\s*([^<\n]+)', html_content, re.IGNORECASE)
                    if phone_match:
                        profile_data['phone'] = phone_match.group(1).strip()

                logger.info(f"Retrieved enhanced profile for {symbol} using Sina fallback")

            except Exception as e:
                logger.warning(f"Sina scraping also failed for {symbol}: {e}")

            # Create Profile object with collected data
            profile = Profile(
                symbol=profile_data['symbol'],
                name=profile_data['name'],
                english_name=profile_data['english_name'],
                listing_date=profile_data['listing_date'],
                industry=profile_data['industry'],
                business=profile_data['business'],
                market_cap=profile_data['market_cap'],
                pe_ratio=profile_data['pe_ratio'],
                pb_ratio=profile_data['pb_ratio'],
                eps=profile_data['eps'],
                bps=profile_data['bps'],
                total_shares=profile_data['total_shares'],
                circulating_shares=profile_data['circulating_shares'],
                website=profile_data['website'],
                address=profile_data['address'],
                phone=profile_data['phone']
            )

            logger.info(f"Retrieved comprehensive profile for {symbol}: {profile}")
            return profile

        except Exception as e:
            logger.error(f"Failed to get profile for symbol {symbol}: {e}")
            return None

    def get_financials(self, symbol: str) -> List[Financial]:
        """Get financial data for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            List of Financial objects
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina financial data page
            url = f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/{code}.phtml"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.text

            # Parse financial tables (simplified - would need more robust parsing)
            financials = []

            # This is a placeholder - actual implementation would need to parse the HTML tables
            # For now, return empty list
            logger.info(f"Retrieved {len(financials)} financial records for {symbol}")
            return financials

        except Exception as e:
            logger.error(f"Failed to get financials for symbol {symbol}: {e}")
            return []

    def get_shareholder_structure(self, symbol: str) -> Optional[Structure]:
        """Get shareholder structure information.

        Args:
            symbol: Stock symbol

        Returns:
            Structure object or None if failed
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina shareholder structure page (this might not exist or be different)
            # Placeholder implementation
            structure = Structure(symbol=symbol)

            logger.info(f"Retrieved shareholder structure for {symbol}: {structure}")
            return structure

        except Exception as e:
            logger.error(f"Failed to get shareholder structure for symbol {symbol}: {e}")
            return None

    def get_dividends(self, symbol: str) -> List[Dividend]:
        """Get dividend history for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            List of Dividend objects
        """
        try:
            # Placeholder implementation - Sina doesn't have a dedicated dividend API
            # Would need to scrape from company pages or other sources
            dividends = []

            logger.info(f"Retrieved {len(dividends)} dividend records for {symbol}")
            return dividends

        except Exception as e:
            logger.error(f"Failed to get dividends for symbol {symbol}: {e}")
            return []

    def get_press_releases(self, symbol: str) -> List[Press]:
        """Get company press releases/announcements.

        Args:
            symbol: Stock symbol

        Returns:
            List of Press objects
        """
        try:
            code = self._normalize_symbol(symbol).replace('SH', '').replace('SZ', '').replace('BJ', '')

            # Sina announcements page
            url = f"https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol={code}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Parse announcements (simplified)
            press_releases = []

            logger.info(f"Retrieved {len(press_releases)} press releases for {symbol}")
            return press_releases

        except Exception as e:
            logger.error(f"Failed to get press releases for symbol {symbol}: {e}")
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

    def _extract_from_html(self, html: str, pattern: str) -> Optional[str]:
        """Extract text from HTML using regex pattern.

        Args:
            html: HTML content
            pattern: Regex pattern

        Returns:
            Extracted text or None
        """
        match = re.search(pattern, html, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_listing_date(self, html: str) -> Optional[date]:
        """Extract listing date from HTML.

        Args:
            html: HTML content

        Returns:
            Listing date or None
        """
        # Look for date patterns in Chinese format - be more specific to avoid false matches
        patterns = [
            r'上市日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'上市时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日.*上市',
            r'成立日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日'
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))

                    # Skip obviously wrong dates (like future dates or very old dates)
                    from datetime import date as date_class
                    today = date_class.today()
                    parsed_date = date_class(year, month, day)

                    if parsed_date > today or year < 1990:
                        continue

                    return parsed_date
                except (ValueError, IndexError):
                    continue

        return None

    def _extract_business_description(self, html: str) -> Optional[str]:
        """Extract business description from HTML.

        Args:
            html: HTML content

        Returns:
            Business description or None
        """
        # Look for business/main business section
        patterns = [
            r'主营业务[：:]\s*([^<\n]+)',
            r'经营范围[：:]\s*([^<\n]+)',
            r'公司业务[：:]\s*([^<\n]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None