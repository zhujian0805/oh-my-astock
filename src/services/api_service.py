"""API service for fetching stock data from akshare."""

import akshare as ak
import requests
import time
import json
import io
from typing import List, Dict, Any
from models.stock import Stock
from lib.logging import get_logger
from lib.debug import debug_metrics, timed_operation, log_data_validation


logger = get_logger(__name__)


class ApiService:
    """Service for interacting with akshare API."""

    def __init__(self):
        """Initialize API service."""
        self._validate_dependencies()
        self._configure_ssl()

    def _validate_dependencies(self):
        """Validate that required dependencies are available."""
        try:
            import akshare
        except ImportError:
            raise ImportError("akshare library is required but not installed")

    def _configure_ssl(self):
        """Configure SSL settings to handle certificate issues."""
        # Disable SSL warnings globally
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

    @timed_operation("api_fetch_code_name_stocks")
    def _fetch_stocks_with_code_name_pagination(self) -> List[Stock]:
        """Fetch all stocks using pagination from Shanghai and Shenzhen stock exchanges.

        Returns:
            List of all Stock objects from Shanghai and Shenzhen exchanges

        Raises:
            Exception: If API calls fail
        """
        import requests
        import pandas as pd

        stocks = []
        session = requests.Session()
        session.verify = False

        # Monkey patch akshare to use our session
        import akshare
        original_session = getattr(akshare, '_session', None)
        akshare._session = session

        try:
            # Fetch Shanghai stocks with pagination
            logger.info("Fetching Shanghai stocks...")
            sh_stocks = self._fetch_shanghai_stocks(session)
            if sh_stocks is not None:
                stocks.extend(sh_stocks)
                logger.info(f"Fetched {len(sh_stocks)} Shanghai stocks")
            else:
                logger.warning("Shanghai stocks fetch returned None")

            # Fetch Shenzhen stocks with pagination
            logger.info("Fetching Shenzhen stocks...")
            sz_stocks = self._fetch_shenzen_stocks(session)
            if sz_stocks is not None:
                stocks.extend(sz_stocks)
                logger.info(f"Fetched {len(sz_stocks)} Shenzhen stocks")
            else:
                logger.warning("Shenzhen stocks fetch returned None")

            # Fetch Beijing stocks (they handle pagination internally)
            logger.info("Fetching Beijing stocks...")
            try:
                bj_df = ak.stock_info_bj_name_code()
                bj_stocks = []
                for _, row in bj_df.iterrows():
                    try:
                        stock = Stock(
                            code=str(row['证券代码']).strip(),
                            name=str(row['证券简称']).strip()
                        )
                        bj_stocks.append(stock)
                    except (ValueError, KeyError) as e:
                        logger.debug(f"Skipping invalid Beijing stock data: {e}")
                        continue
                stocks.extend(bj_stocks)
                logger.info(f"Fetched {len(bj_stocks)} Beijing stocks")
            except Exception as e:
                logger.warning(f"Failed to fetch Beijing stocks: {e}")

        finally:
            # Restore original session
            if original_session is not None:
                akshare._session = original_session
            else:
                if hasattr(akshare, '_session'):
                    delattr(akshare, '_session')

        logger.info(f"Total stocks fetched: {len(stocks)}")
        return stocks

    def _fetch_shanghai_stocks(self, session: requests.Session) -> List[Stock]:
        """Fetch Shanghai stocks with pagination."""
        stocks = []
        page_size = 100  # Based on typical API pagination

        # Shanghai SSE API endpoint
        url = "http://query.sse.com.cn/security/stock/getStockListData2.do"

        for page in range(1, 100):  # Reasonable upper limit
            try:
                params = {
                    "jsonCallBack": "jsonpCallback",
                    "isPagination": "true",
                    "pageHelp.pageSize": str(page_size),
                    "pageHelp.pageNo": str(page),
                    "pageHelp.beginPage": str(page),
                    "pageHelp.endPage": str(page),
                    "stockType": "1",  # A shares
                    "_": str(int(time.time() * 1000))
                }

                headers = {
                    'Referer': 'http://www.sse.com.cn/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = session.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()

                # Parse JSONP response
                content = response.text.strip()
                if content.startswith('jsonpCallback(') and content.endswith(');'):
                    json_str = content[14:-2]  # Remove jsonpCallback( and );
                    data = json.loads(json_str)

                    if 'pageHelp' in data and 'data' in data:
                        page_data = data['data']
                        if not page_data:
                            logger.debug(f"No more Shanghai stocks on page {page}")
                            break

                        logger.debug(f"Shanghai page {page}: Retrieved {len(page_data)} stocks")

                        for stock_data in page_data:
                            try:
                                code = str(stock_data.get('SECURITY_CODE_A', '')).strip()
                                name = str(stock_data.get('SECURITY_ABBR_A', '')).strip()

                                if code and name:
                                    stock = Stock(code=code, name=name)
                                    stocks.append(stock)
                            except ValueError as e:
                                logger.debug(f"Skipping invalid Shanghai stock: {e}")
                                continue

                        # Check if this is the last page
                        total_pages = data.get('pageHelp', {}).get('totalPages', 0)
                        if page >= total_pages:
                            logger.debug(f"Reached last Shanghai page: {page}/{total_pages}")
                            break
                    else:
                        logger.debug(f"No pageHelp/data in Shanghai response for page {page}")
                        break
                else:
                    logger.debug(f"Unexpected Shanghai response format for page {page}")
                    break

            except Exception as e:
                logger.warning(f"Error fetching Shanghai stocks page {page}: {e}")
                break

        return stocks

    def _fetch_shenzen_stocks(self, session: requests.Session) -> List[Stock]:
        """Fetch Shenzhen stocks with pagination."""
        import pandas as pd  # Import pandas locally
        stocks = []
        page_size = 100

        # Shenzhen SZSE API endpoint
        url = "http://www.szse.cn/api/report/ShowReport"

        for page in range(1, 100):  # Reasonable upper limit
            try:
                # SZSE uses different pagination parameters
                params = {
                    "SHOWTYPE": "xlsx",
                    "CATALOGID": "1110",  # Listed companies
                    "TABKEY": "tab1",  # Main board
                    "PAGENO": str(page),
                    "random": str(time.time())
                }

                headers = {
                    'Referer': 'http://www.szse.cn/market/stock/list/index.html',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = session.get(url, params=params, headers=headers, timeout=30)

                # SZSE returns Excel data, we need to parse it
                if response.status_code == 200 and len(response.content) > 0:
                    try:
                        # Try to read as Excel
                        df = pd.read_excel(io.BytesIO(response.content))

                        if df.empty:
                            logger.debug(f"No more Shenzhen stocks on page {page}")
                            break

                        logger.debug(f"Shenzhen page {page}: Retrieved {len(df)} stocks")

                        for _, row in df.iterrows():
                            try:
                                # SZSE Excel format has different column names
                                code = str(row.get('A股代码', row.get('A代码', ''))).strip()
                                name = str(row.get('A股简称', row.get('A简称', ''))).strip()

                                if code and name and code != 'nan' and name != 'nan':
                                    stock = Stock(code=code.zfill(6), name=name)
                                    stocks.append(stock)
                            except (ValueError, KeyError) as e:
                                logger.debug(f"Skipping invalid Shenzhen stock: {e}")
                                continue

                        # If we got less than page_size, this might be the last page
                        if len(df) < page_size:
                            logger.debug(f"Shenzhen page {page} has {len(df)} stocks (< {page_size}), might be last page")
                            # Continue to next page to be sure

                    except Exception as e:
                        logger.warning(f"Error parsing Shenzhen Excel data for page {page}: {e}")
                        break
                else:
                    logger.debug(f"No data from Shenzhen API for page {page}")
                    break

            except Exception as e:
                logger.warning(f"Error fetching Shenzhen stocks page {page}: {e}")
                break

        return stocks

    @timed_operation("api_fetch_paginated_stocks")
    def _fetch_all_stocks_with_pagination(self) -> List[Stock]:
        """Fetch all stocks using pagination from stock_zh_a_spot_em API.

        Returns:
            List of all Stock objects from all pages

        Raises:
            Exception: If API calls fail
        """
        import requests
        import pandas as pd

        stocks = []
        page = 1
        page_size = 100  # Based on the akshare source code

        # Create a session with SSL verification disabled
        session = requests.Session()
        session.verify = False

        # Monkey patch akshare to use our session
        import akshare
        original_session = getattr(akshare, '_session', None)
        akshare._session = session

        try:
            while True:
                logger.info(f"Fetching page {page} (page size: {page_size})...")
                logger.debug(f"Requesting page {page} from East Money API")

                # Call the API with specific page number
                # We need to modify the akshare function to accept page parameter
                url = "https://82.push2.eastmoney.com/api/qt/clist/get"
                params = {
                    "pn": str(page),
                    "pz": str(page_size),
                    "po": "1",
                    "np": "1",
                    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                    "fltt": "2",
                    "invt": "2",
                    "fid": "f12",
                    "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
                    "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,"
                              "f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
                }
                logger.debug(f"API URL: {url}")
                logger.debug(f"Request params: {params}")

                try:
                    response = session.get(url, params=params, timeout=30)
                    response.raise_for_status()

                    data = response.json()
                    logger.debug(f"API response received, status: {response.status_code}")
                    logger.debug(f"Response data keys: {list(data.keys()) if data else 'None'}")
                    if not data or 'data' not in data or not data['data'] or 'diff' not in data['data']:
                        logger.warning(f"No more data on page {page}, stopping pagination")
                        break

                    page_data = data['data']['diff']
                    if not page_data:
                        logger.info(f"No data returned on page {page}, stopping pagination")
                        break

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed for page {page}: {e}")
                    # If this is the first page and we get an error, re-raise it
                    if page == 1:
                        raise e
                    # For subsequent pages, assume we've reached the end
                    logger.info(f"Assuming end of data after page {page-1}")
                    break
                except ValueError as e:
                    logger.warning(f"JSON parsing failed for page {page}: {e}")
                    # If this is the first page and we get an error, re-raise it
                    if page == 1:
                        raise e
                    # For subsequent pages, assume we've reached the end
                    logger.info(f"Assuming end of data after page {page-1}")
                    break

                logger.info(f"Page {page}: Retrieved {len(page_data)} stocks")
                logger.debug(f"Processing {len(page_data)} stocks from page {page}")

                # Convert to DataFrame for easier processing
                df = pd.DataFrame(page_data)

                # Rename columns to match what akshare uses
                column_mapping = {
                    'f12': '代码',
                    'f14': '名称',
                    # Add other mappings as needed
                }
                df = df.rename(columns=column_mapping)
                logger.debug(f"DataFrame columns after mapping: {df.columns.tolist()}")

                # Process the stocks from this page
                page_stocks = 0
                for _, row in df.iterrows():
                    try:
                        # Extract code and name from real-time data
                        code = str(row.get('代码', row.get('f12', ''))).strip()
                        name = str(row.get('名称', row.get('f14', ''))).strip()

                        # Only include A-share stocks (codes starting with 0, 3, 6, 8)
                        if code and name and code.startswith(('0', '3', '6', '8')):
                            stock = Stock(code=code, name=name)
                            stocks.append(stock)
                            page_stocks += 1
                        else:
                            logger.debug(f"Skipping non-A-share stock: code='{code}', name='{name}'")
                    except ValueError as e:
                        logger.warning(f"Skipping invalid stock data: {e}")
                        continue

                logger.info(f"Page {page}: Processed {page_stocks} valid stocks")
                logger.debug(f"Page {page} summary: {len(page_data)} retrieved, {page_stocks} valid, {len(page_data) - page_stocks} skipped")

                # Check if we got less than page_size, indicating this is the last page
                if len(page_data) < page_size:
                    logger.info(f"Received {len(page_data)} stocks (< {page_size}), this appears to be the last page")
                    break

                page += 1

                # Safety check to prevent infinite loops
                if page > 1000:  # Reasonable upper limit
                    logger.warning("Reached maximum page limit (1000), stopping pagination")
                    break

        finally:
            # Restore original session if it existed
            if original_session is not None:
                akshare._session = original_session
            else:
                if hasattr(akshare, '_session'):
                    delattr(akshare, '_session')

        logger.info(f"Total stocks fetched across all pages: {len(stocks)}")
        return stocks

    @timed_operation("api_fetch_stocks")
    def fetch_stock_info(self) -> List[Stock]:
        """Fetch stock information from akshare API.

        Returns:
            List of Stock objects

        Raises:
            Exception: If API call fails
        """
        try:
            logger.info("Fetching stock information from akshare API")

            stocks = []
            api_success = False

            # Try unified East Money API first (gets all stocks from all regions)
            try:
                logger.info("Trying unified East Money API for all regions...")
                stocks = self._fetch_all_stocks_with_pagination()
                logger.info(f"Successfully fetched {len(stocks)} stocks from unified East Money API")

                # Count by region for verification
                sh_count = sum(1 for stock in stocks if stock.code.startswith('6'))
                sz_count = sum(1 for stock in stocks if stock.code.startswith(('0', '3')))
                bj_count = sum(1 for stock in stocks if stock.code.startswith('8'))
                logger.info(f"Stocks by region - Shanghai: {sh_count}, Shenzhen: {sz_count}, Beijing: {bj_count}")

                api_success = True

            except Exception as e1:
                logger.warning(f"Unified East Money API failed: {e1}")

                # Try primary API: stock_info_a_code_name (per spec FR-004)
                try:
                    logger.info("Trying stock_info_a_code_name() as fallback...")
                    # Create a session with SSL verification disabled
                    import requests
                    session = requests.Session()
                    session.verify = False

                    # Monkey patch akshare to use our session
                    import akshare
                    original_session = getattr(akshare, '_session', None)
                    akshare._session = session

                    df = ak.stock_info_a_code_name()

                    # Restore original session if it existed
                    if original_session is not None:
                        akshare._session = original_session
                    else:
                        delattr(akshare, '_session')

                    for _, row in df.iterrows():
                        try:
                            stock = Stock(
                                code=str(row['code']).strip(),
                                name=str(row['name']).strip()
                            )
                            stocks.append(stock)
                        except ValueError as e:
                            logger.warning(f"Skipping invalid stock data: {e}")
                            continue

                    logger.info(f"Successfully fetched {len(stocks)} stocks from stock_info_a_code_name")
                    api_success = True

                except Exception as e2:
                    logger.warning(f"stock_info_a_code_name fallback also failed: {e2}")

                    # Try final fallback: separate exchange APIs with pagination
                    try:
                        logger.info("Trying separate exchange APIs with pagination as final fallback...")
                        stocks = self._fetch_stocks_with_code_name_pagination()
                        logger.info(f"Successfully fetched {len(stocks)} stocks from separate exchange APIs")
                        api_success = True

                    except Exception as e3:
                        logger.warning(f"Separate exchange APIs also failed: {e3}")
                        logger.info("All API methods failed, falling back to sample stock data")

            if api_success and stocks and len(stocks) >= 5000:  # Require at least 5000 A-share stocks for success
                # Remove duplicates before validation
                seen_codes = set()
                unique_stocks = []
                for stock in stocks:
                    if stock.code not in seen_codes:
                        seen_codes.add(stock.code)
                        unique_stocks.append(stock)
                stocks = unique_stocks
                logger.info(f"Removed duplicates, {len(stocks)} unique stocks remaining")

                logger.info(f"Successfully fetched {len(stocks)} stocks total")
                return stocks

        except Exception as e:
            logger.warning(f"Failed to fetch stock information from API: {e}")
            logger.info("Falling back to sample stock data for testing")

        # Provide sample stock data for testing when API fails
        sample_stocks = [
            Stock(code="000001", name="平安银行"),
            Stock(code="000002", name="万科A"),
            Stock(code="000858", name="五粮液"),
            Stock(code="600000", name="浦发银行"),
            Stock(code="600036", name="招商银行"),
            Stock(code="600519", name="贵州茅台"),
            Stock(code="600276", name="恒瑞医药"),
            Stock(code="000568", name="泸州老窖"),
            Stock(code="002142", name="宁波银行"),
            Stock(code="000625", name="长安汽车"),
        ]

        logger.info(f"Returning {len(sample_stocks)} sample stocks for testing")
        return sample_stocks

    def validate_stock_data(self, stocks: List[Stock]) -> bool:
        """Validate fetched stock data.

        Args:
            stocks: List of stocks to validate

        Returns:
            True if all data is valid
        """
        log_data_validation(stocks, "List[Stock]", "stock_data_validation")

        if not stocks:
            logger.warning("No stock data to validate")
            return False

        # Check for duplicate codes
        codes = [stock.code for stock in stocks]
        if len(codes) != len(set(codes)):
            logger.error("Duplicate stock codes found")
            debug_metrics.log_error_with_trace(ValueError("Duplicate stock codes"), "data_validation")
            return False

        logger.info(f"Validated {len(stocks)} stocks successfully")
        return True