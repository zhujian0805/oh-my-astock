"""Contract tests for SinaFinanceService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from models.quote import Quote
from models.profile import Profile
from models.structure import Structure, Shareholder
from services.sina_finance_service import SinaFinanceService


class TestSinaFinanceServiceContract:
    """Contract tests for SinaFinanceService."""

    def test_service_initialization(self):
        """Test SinaFinanceService initialization."""
        service = SinaFinanceService()
        assert service.session is not None
        assert hasattr(service, 'search_stocks')
        assert hasattr(service, 'get_quote')
        assert hasattr(service, 'get_profile')

    @patch('services.sina_finance_service.requests.Session')
    def test_search_stocks_success(self, mock_session_class):
        """Test successful stock search."""
        # Mock the session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '/*["平安银行","000001","SZ","平安银行",null,null,"000001"]*/'
        mock_session.get.return_value = mock_response

        service = SinaFinanceService()
        results = service.search_stocks("平安")

        assert len(results) > 0
        assert results[0]['code'] == '000001'
        assert results[0]['name'] == '平安银行'
        assert results[0]['exchange'] == 'SZ'

    @patch('services.sina_finance_service.requests.Session')
    def test_search_stocks_no_results(self, mock_session_class):
        """Test stock search with no results."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '/*[]*/'
        mock_session.get.return_value = mock_response

        service = SinaFinanceService()
        results = service.search_stocks("nonexistent")

        assert len(results) == 0

    @patch('services.sina_finance_service.ak.stock_zh_a_spot_em')
    def test_get_quote_success(self, mock_ak_function):
        """Test successful quote retrieval."""
        # Mock akshare response
        mock_df = Mock()
        mock_df.empty = False
        mock_df.iloc = [Mock()]
        mock_row = Mock()
        mock_row.get.side_effect = lambda key, default=None: {
            '名称': '平安银行',
            '最新价': 10.50,
            '今开': 10.45,
            '最高': 10.60,
            '最低': 10.40,
            '昨收': 10.45,
            '成交量': 1000000,
            '成交额': 10500000.0
        }.get(key, default)
        mock_df.iloc[0] = mock_row
        mock_ak_function.return_value = mock_df

        service = SinaFinanceService()
        quote = service.get_quote("000001")

        assert quote is not None
        assert quote.symbol == "000001"
        assert quote.name == "平安银行"
        assert quote.price == 10.50
        assert quote.open_price == 10.45
        assert quote.volume == 1000000

    @patch('services.sina_finance_service.ak.stock_zh_a_spot_em')
    def test_get_quote_no_data(self, mock_ak_function):
        """Test quote retrieval with no data."""
        mock_df = Mock()
        mock_df.empty = True
        mock_ak_function.return_value = mock_df

        service = SinaFinanceService()
        quote = service.get_quote("999999")

        assert quote is None

    def test_normalize_symbol(self):
        """Test symbol normalization."""
        service = SinaFinanceService()

        # Test various symbol formats
        assert service._normalize_symbol("000001") == "SZ000001"
        assert service._normalize_symbol("600000") == "SH600000"
        assert service._normalize_symbol("SH600000") == "SH600000"
        assert service._normalize_symbol("SZ000001") == "SZ000001"
        assert service._normalize_symbol("BJ000001") == "BJ000001"

    def test_get_exchange_from_code(self):
        """Test exchange detection from stock code."""
        service = SinaFinanceService()

        # Shanghai codes
        assert service._get_exchange_from_code("600000") == "SH"
        assert service._get_exchange_from_code("688000") == "SH"
        assert service._get_exchange_from_code("700000") == "SH"

        # Shenzhen codes
        assert service._get_exchange_from_code("000001") == "SZ"
        assert service._get_exchange_from_code("300000") == "SZ"

        # Beijing codes
        assert service._get_exchange_from_code("800000") == "BJ"
        assert service._get_exchange_from_code("900000") == "BJ"

        # Default
        assert service._get_exchange_from_code("999999") == "SH"

    @patch('services.sina_finance_service.requests.Session')
    def test_get_profile_success(self, mock_session_class):
        """Test successful profile retrieval."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''
        <html>
        <head><title>平安银行(000001)股票_公司资料_新浪财经</title></head>
        <body>
        行业：银行<br>
        主营业务：商业银行服务<br>
        上市日期：1991年4月3日
        </body>
        </html>
        '''
        mock_session.get.return_value = mock_response

        service = SinaFinanceService()
        profile = service.get_profile("000001")

        assert profile is not None
        assert profile.symbol == "000001"
        assert profile.name == "平安银行(000001)股票_公司资料_新浪财经"
        assert profile.industry == "银行"
        assert profile.business == "商业银行服务"
        assert profile.listing_date == date(1991, 4, 3)

    @patch('services.sina_finance_service.requests.Session')
    def test_get_profile_failure(self, mock_session_class):
        """Test profile retrieval failure."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get.side_effect = Exception("Network error")

        service = SinaFinanceService()
        profile = service.get_profile("000001")

        assert profile is None

    def test_extract_listing_date(self):
        """Test listing date extraction from HTML."""
        service = SinaFinanceService()

        # Test various date formats
        html1 = "上市日期：1991年4月3日"
        date1 = service._extract_listing_date(html1)
        assert date1 == date(1991, 4, 3)

        html2 = "1991年4月3日上市"
        date2 = service._extract_listing_date(html2)
        assert date2 == date(1991, 4, 3)

        html3 = "1991-4-3"
        date3 = service._extract_listing_date(html3)
        assert date3 == date(1991, 4, 3)

        # Test invalid format
        html4 = "no date here"
        date4 = service._extract_listing_date(html4)
        assert date4 is None

    def test_extract_business_description(self):
        """Test business description extraction."""
        service = SinaFinanceService()

        html1 = "主营业务：商业银行服务"
        business1 = service._extract_business_description(html1)
        assert business1 == "商业银行服务"

        html2 = "经营范围：金融服务"
        business2 = service._extract_business_description(html2)
        assert business2 == "金融服务"

        html3 = "no business info"
        business3 = service._extract_business_description(html3)
        assert business3 is None

    def test_extract_from_html(self):
        """Test generic HTML extraction."""
        service = SinaFinanceService()

        html = '<title>Test Title</title><div>Some content</div>'
        title = service._extract_from_html(html, r'<title>([^<]+)</title>')
        assert title == "Test Title"

        # Test no match
        missing = service._extract_from_html(html, r'<missing>([^<]+)</missing>')
        assert missing is None

    def test_get_financials_placeholder(self):
        """Test financials method (currently placeholder)."""
        service = SinaFinanceService()
        financials = service.get_financials("000001")

        assert isinstance(financials, list)
        assert len(financials) == 0

    def test_get_shareholder_structure_placeholder(self):
        """Test shareholder structure method (currently placeholder)."""
        service = SinaFinanceService()
        structure = service.get_shareholder_structure("000001")

        assert structure is not None
        assert structure.symbol == "000001"
        assert len(structure.top_10_shareholders) == 0

    def test_get_dividends_placeholder(self):
        """Test dividends method (currently placeholder)."""
        service = SinaFinanceService()
        dividends = service.get_dividends("000001")

        assert isinstance(dividends, list)
        assert len(dividends) == 0

    def test_get_press_releases_placeholder(self):
        """Test press releases method (currently placeholder)."""
        service = SinaFinanceService()
        press = service.get_press_releases("000001")

        assert isinstance(press, list)
        assert len(press) == 0</content>
<parameter name="file_path">tests/contract/test_sina_finance_service.py