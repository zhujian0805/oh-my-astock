"""Contract tests for new data model validation."""

import pytest
from datetime import datetime, date
from models.quote import Quote
from models.profile import Profile
from models.financial import Financial
from models.structure import Structure, Shareholder
from models.dividend import Dividend
from models.press import Press


class TestNewDataModelContract:
    """Contract tests for new data models."""

    def test_quote_creation(self):
        """Test Quote object creation."""
        quote = Quote(
            symbol="000001",
            name="平安银行",
            price=10.50,
            open_price=10.45,
            high_price=10.60,
            low_price=10.40,
            close_price=10.45,
            volume=1000000,
            turnover=10500000.0,
            price_change=0.05,
            price_change_rate=0.48,
            timestamp=datetime.now(),
            market_status="trading"
        )
        assert quote.symbol == "000001"
        assert quote.name == "平安银行"
        assert quote.price == 10.50
        assert quote.market_status == "trading"

    def test_quote_validation(self):
        """Test Quote validation."""
        # Valid quote
        quote = Quote(symbol="000001", name="平安银行")
        assert quote.symbol == "000001"

        # Invalid symbol
        with pytest.raises(ValueError):
            Quote(symbol="", name="平安银行")

        # Invalid name
        with pytest.raises(ValueError):
            Quote(symbol="000001", name="")

    def test_quote_serialization(self):
        """Test Quote to/from dict conversion."""
        original_quote = Quote(
            symbol="000001",
            name="平安银行",
            price=10.50,
            price_change=0.05,
            price_change_rate=0.48,
            timestamp=datetime(2024, 1, 1, 9, 30, 0),
            market_status="trading"
        )

        quote_dict = original_quote.to_dict()

        assert quote_dict["symbol"] == "000001"
        assert quote_dict["name"] == "平安银行"
        assert quote_dict["price"] == 10.50
        assert quote_dict["price_change"] == 0.05
        assert quote_dict["price_change_rate"] == 0.48
        assert quote_dict["market_status"] == "trading"
        assert "timestamp" in quote_dict

        # Round trip
        quote2 = Quote.from_dict(quote_dict)
        assert quote2.symbol == original_quote.symbol
        assert quote2.name == original_quote.name
        assert quote2.price == original_quote.price

    def test_profile_creation(self):
        """Test Profile object creation."""
        profile = Profile(
            symbol="000001",
            name="平安银行",
            english_name="Ping An Bank",
            listing_date=date(1991, 4, 3),
            industry="银行",
            business="商业银行服务",
            market_cap=250000000000.0,
            pe_ratio=8.5,
            pb_ratio=0.8,
            eps=2.1,
            bps=15.6
        )
        assert profile.symbol == "000001"
        assert profile.name == "平安银行"
        assert profile.industry == "银行"
        assert profile.market_cap == 250000000000.0

    def test_profile_validation(self):
        """Test Profile validation."""
        # Valid profile
        profile = Profile(symbol="000001", name="平安银行")
        assert profile.symbol == "000001"

        # Invalid symbol
        with pytest.raises(ValueError):
            Profile(symbol="", name="平安银行")

        # Invalid name
        with pytest.raises(ValueError):
            Profile(symbol="000001", name="")

    def test_profile_serialization(self):
        """Test Profile to/from dict conversion."""
        original_profile = Profile(
            symbol="000001",
            name="平安银行",
            listing_date=date(1991, 4, 3),
            industry="银行",
            market_cap=250000000000.0
        )

        profile_dict = original_profile.to_dict()

        assert profile_dict["symbol"] == "000001"
        assert profile_dict["name"] == "平安银行"
        assert profile_dict["industry"] == "银行"
        assert profile_dict["market_cap"] == 250000000000.0
        assert "listing_date" in profile_dict

        # Round trip
        profile2 = Profile.from_dict(profile_dict)
        assert profile2.symbol == original_profile.symbol
        assert profile2.name == original_profile.name
        assert profile2.industry == original_profile.industry

    def test_financial_creation(self):
        """Test Financial object creation."""
        financial = Financial(
            symbol="000001",
            period="2023Q4",
            revenue=1000000000.0,
            net_profit=200000000.0,
            eps=2.1,
            roe=15.6,
            roa=1.2,
            gross_margin=0.85,
            net_margin=0.20,
            revenue_yoy=0.15,
            net_profit_yoy=0.12
        )
        assert financial.symbol == "000001"
        assert financial.period == "2023Q4"
        assert financial.revenue == 1000000000.0
        assert financial.net_profit == 200000000.0

    def test_financial_validation(self):
        """Test Financial validation."""
        # Valid financial
        financial = Financial(symbol="000001", period="2023Q4")
        assert financial.symbol == "000001"

        # Invalid symbol
        with pytest.raises(ValueError):
            Financial(symbol="", period="2023Q4")

        # Invalid period
        with pytest.raises(ValueError):
            Financial(symbol="000001", period="")

    def test_financial_serialization(self):
        """Test Financial to/from dict conversion."""
        original_financial = Financial(
            symbol="000001",
            period="2023Q4",
            revenue=1000000000.0,
            net_profit=200000000.0,
            eps=2.1
        )

        financial_dict = original_financial.to_dict()

        assert financial_dict["symbol"] == "000001"
        assert financial_dict["period"] == "2023Q4"
        assert financial_dict["revenue"] == 1000000000.0
        assert financial_dict["net_profit"] == 200000000.0
        assert financial_dict["eps"] == 2.1

        # Round trip
        financial2 = Financial.from_dict(financial_dict)
        assert financial2.symbol == original_financial.symbol
        assert financial2.period == original_financial.period
        assert financial2.revenue == original_financial.revenue

    def test_shareholder_creation(self):
        """Test Shareholder object creation."""
        shareholder = Shareholder(
            name="中国平安保险(集团)股份有限公司",
            shares=1000000000,
            percentage=25.6,
            share_type="A股"
        )
        assert shareholder.name == "中国平安保险(集团)股份有限公司"
        assert shareholder.shares == 1000000000
        assert shareholder.percentage == 25.6
        assert shareholder.share_type == "A股"

    def test_shareholder_validation(self):
        """Test Shareholder validation."""
        # Valid shareholder
        shareholder = Shareholder(name="Test Holder", shares=1000, percentage=10.0)
        assert shareholder.name == "Test Holder"

        # Invalid name
        with pytest.raises(ValueError):
            Shareholder(name="", shares=1000, percentage=10.0)

        # Negative shares
        with pytest.raises(ValueError):
            Shareholder(name="Test", shares=-100, percentage=10.0)

        # Invalid percentage
        with pytest.raises(ValueError):
            Shareholder(name="Test", shares=1000, percentage=150.0)

    def test_shareholder_serialization(self):
        """Test Shareholder to/from dict conversion."""
        original_shareholder = Shareholder(
            name="Test Holder",
            shares=1000000,
            percentage=15.5,
            share_type="A股"
        )

        shareholder_dict = original_shareholder.to_dict()

        assert shareholder_dict["name"] == "Test Holder"
        assert shareholder_dict["shares"] == 1000000
        assert shareholder_dict["percentage"] == 15.5
        assert shareholder_dict["share_type"] == "A股"

        # Round trip
        shareholder2 = Shareholder.from_dict(shareholder_dict)
        assert shareholder2.name == original_shareholder.name
        assert shareholder2.shares == original_shareholder.shares
        assert shareholder2.percentage == original_shareholder.percentage

    def test_structure_creation(self):
        """Test Structure object creation."""
        shareholders = [
            Shareholder(name="Holder 1", shares=1000, percentage=20.0),
            Shareholder(name="Holder 2", shares=800, percentage=16.0)
        ]

        structure = Structure(
            symbol="000001",
            report_date=date(2024, 3, 31),
            total_shareholders=1250,
            top_10_shareholders=shareholders
        )

        assert structure.symbol == "000001"
        assert structure.total_shareholders == 1250
        assert len(structure.top_10_shareholders) == 2

    def test_structure_validation(self):
        """Test Structure validation."""
        # Valid structure
        structure = Structure(symbol="000001")
        assert structure.symbol == "000001"

        # Invalid symbol
        with pytest.raises(ValueError):
            Structure(symbol="", top_10_shareholders=[])

    def test_structure_operations(self):
        """Test Structure operations."""
        structure = Structure(symbol="000001")

        # Add shareholder
        shareholder = Shareholder(name="Test Holder", shares=1000, percentage=10.0)
        structure.add_shareholder(shareholder)
        assert len(structure.top_10_shareholders) == 1

    def test_structure_serialization(self):
        """Test Structure to/from dict conversion."""
        shareholders = [Shareholder(name="Holder 1", shares=1000, percentage=20.0)]
        original_structure = Structure(
            symbol="000001",
            total_shareholders=1250,
            top_10_shareholders=shareholders
        )

        structure_dict = original_structure.to_dict()

        assert structure_dict["symbol"] == "000001"
        assert structure_dict["total_shareholders"] == 1250
        assert len(structure_dict["top_10_shareholders"]) == 1

        # Round trip
        structure2 = Structure.from_dict(structure_dict)
        assert structure2.symbol == original_structure.symbol
        assert structure2.total_shareholders == original_structure.total_shareholders
        assert len(structure2.top_10_shareholders) == len(original_structure.top_10_shareholders)

    def test_dividend_creation(self):
        """Test Dividend object creation."""
        dividend = Dividend(
            symbol="000001",
            record_date=date(2024, 6, 30),
            ex_dividend_date=date(2024, 7, 1),
            dividend_per_share=1.5,
            share_dividend=0.5,
            total_dividend=200000000.0,
            dividend_yield=3.2,
            period="2023年报"
        )
        assert dividend.symbol == "000001"
        assert dividend.dividend_per_share == 1.5
        assert dividend.share_dividend == 0.5
        assert dividend.period == "2023年报"

    def test_dividend_validation(self):
        """Test Dividend validation."""
        # Valid dividend
        dividend = Dividend(symbol="000001")
        assert dividend.symbol == "000001"

        # Invalid symbol
        with pytest.raises(ValueError):
            Dividend(symbol="")

    def test_dividend_serialization(self):
        """Test Dividend to/from dict conversion."""
        original_dividend = Dividend(
            symbol="000001",
            dividend_per_share=1.5,
            period="2023年报"
        )

        dividend_dict = original_dividend.to_dict()

        assert dividend_dict["symbol"] == "000001"
        assert dividend_dict["dividend_per_share"] == 1.5
        assert dividend_dict["period"] == "2023年报"

        # Round trip
        dividend2 = Dividend.from_dict(dividend_dict)
        assert dividend2.symbol == original_dividend.symbol
        assert dividend2.dividend_per_share == original_dividend.dividend_per_share

    def test_press_creation(self):
        """Test Press object creation."""
        press = Press(
            symbol="000001",
            title="平安银行2023年年度报告",
            date=datetime(2024, 4, 15, 10, 0, 0),
            type="定期报告",
            url="https://example.com/report.pdf",
            summary="平安银行发布2023年年度财务报告"
        )
        assert press.symbol == "000001"
        assert press.title == "平安银行2023年年度报告"
        assert press.type == "定期报告"
        assert press.url == "https://example.com/report.pdf"

    def test_press_validation(self):
        """Test Press validation."""
        # Valid press
        press = Press(symbol="000001", title="Test Title")
        assert press.symbol == "000001"

        # Invalid symbol
        with pytest.raises(ValueError):
            Press(symbol="", title="Test Title")

        # Invalid title
        with pytest.raises(ValueError):
            Press(symbol="000001", title="")

    def test_press_serialization(self):
        """Test Press to/from dict conversion."""
        original_press = Press(
            symbol="000001",
            title="Test Press Release",
            type="定期报告",
            summary="Test summary"
        )

        press_dict = original_press.to_dict()

        assert press_dict["symbol"] == "000001"
        assert press_dict["title"] == "Test Press Release"
        assert press_dict["type"] == "定期报告"
        assert press_dict["summary"] == "Test summary"

        # Round trip
        press2 = Press.from_dict(press_dict)
        assert press2.symbol == original_press.symbol
        assert press2.title == original_press.title
        assert press2.type == original_press.type

    def test_press_string_representation(self):
        """Test Press string representation."""
        press = Press(
            symbol="000001",
            title="Very Long Title That Should Be Truncated In Display But Not In Data",
            date=datetime(2024, 1, 1)
        )

        str_repr = str(press)
        # Should truncate title in display
        assert "Very Long Title That Should Be Truncated" in str_repr
        assert "000001" in str_repr</content>
<parameter name="file_path">tests/contract/test_new_data_models.py