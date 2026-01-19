"""Contract tests for new CLI commands."""

import pytest
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli.commands import cli


class TestNewCliCommandsContract:
    """Contract tests for new CLI commands."""

    def test_search_command_help(self):
        """Test search command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search for stocks by code, name, or pinyin" in result.output
        assert "--limit" in result.output

    @patch('services.sina_finance_service.SinaFinanceService.search_stocks')
    def test_search_command_success(self, mock_search):
        """Test successful search command."""
        mock_search.return_value = [
            {
                'code': '000001',
                'name': '平安银行',
                'exchange': 'SZ',
                'full_code': 'SZ000001'
            }
        ]

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "平安"])

        assert result.exit_code == 0
        assert "Searching for stocks matching '平安'..." in result.output
        assert "Found 1 stocks" in result.output

        # Should output valid JSON
        try:
            data = json.loads(result.output.split('\n\n')[1])
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['code'] == '000001'
        except (json.JSONDecodeError, IndexError):
            pytest.fail("Command should output valid JSON")

    @patch('services.sina_finance_service.SinaFinanceService.search_stocks')
    def test_search_command_no_results(self, mock_search):
        """Test search command with no results."""
        mock_search.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "nonexistent"])

        assert result.exit_code == 1
        assert "No stocks found matching the query" in result.output

    @patch('services.sina_finance_service.SinaFinanceService.search_stocks')
    def test_search_command_with_limit(self, mock_search):
        """Test search command with limit option."""
        mock_search.return_value = [
            {'code': '000001', 'name': '平安银行', 'exchange': 'SZ'},
            {'code': '000002', 'name': '万科A', 'exchange': 'SZ'},
            {'code': '600000', 'name': '浦发银行', 'exchange': 'SH'}
        ]

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "银行", "--limit", "2"])

        assert result.exit_code == 0

        # Should only return 2 results
        try:
            data = json.loads(result.output.split('\n\n')[1])
            assert len(data) == 2
        except (json.JSONDecodeError, IndexError):
            pytest.fail("Command should output valid JSON")

    def test_quote_command_help(self):
        """Test quote command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["quote", "--help"])

        assert result.exit_code == 0
        assert "Get real-time quote for a stock" in result.output

    @patch('services.sina_finance_service.SinaFinanceService.get_quote')
    def test_quote_command_success(self, mock_get_quote):
        """Test successful quote command."""
        mock_quote = MagicMock()
        mock_quote.to_dict.return_value = {
            'symbol': '000001',
            'name': '平安银行',
            'price': 10.50,
            'price_change': 0.05,
            'price_change_rate': 0.48
        }
        mock_get_quote.return_value = mock_quote

        runner = CliRunner()
        result = runner.invoke(cli, ["quote", "000001"])

        assert result.exit_code == 0
        assert "Fetching real-time quote for 000001..." in result.output

        # Should output valid JSON
        try:
            data = json.loads(result.output.strip())
            assert isinstance(data, dict)
            assert data['symbol'] == '000001'
            assert data['price'] == 10.50
        except json.JSONDecodeError:
            pytest.fail("Command should output valid JSON")

    @patch('services.sina_finance_service.SinaFinanceService.get_quote')
    def test_quote_command_no_data(self, mock_get_quote):
        """Test quote command with no data."""
        mock_get_quote.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ["quote", "999999"])

        assert result.exit_code == 1
        assert "No quote data found for symbol 999999" in result.output

    def test_info_command_help(self):
        """Test info command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "--help"])

        assert result.exit_code == 0
        assert "Get detailed information about a stock" in result.output
        assert "--include-financials" in result.output
        assert "--include-shareholders" in result.output
        assert "--include-dividends" in result.output
        assert "--include-press" in result.output

    @patch('services.sina_finance_service.SinaFinanceService.get_profile')
    @patch('services.sina_finance_service.SinaFinanceService.get_quote')
    def test_info_command_basic_success(self, mock_get_quote, mock_get_profile):
        """Test successful info command with basic data."""
        # Mock profile
        mock_profile = MagicMock()
        mock_profile.to_dict.return_value = {
            'symbol': '000001',
            'name': '平安银行',
            'industry': '银行',
            'market_cap': 250000000000.0
        }
        mock_get_profile.return_value = mock_profile

        # Mock quote
        mock_quote = MagicMock()
        mock_quote.to_dict.return_value = {
            'symbol': '000001',
            'name': '平安银行',
            'price': 10.50,
            'price_change': 0.05
        }
        mock_get_quote.return_value = mock_quote

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "000001"])

        assert result.exit_code == 0
        assert "Fetching information for 000001..." in result.output

        # Should output valid JSON
        try:
            data = json.loads(result.output.strip())
            assert isinstance(data, dict)
            assert 'profile' in data
            assert 'quote' in data
            assert data['profile']['symbol'] == '000001'
            assert data['quote']['price'] == 10.50
        except json.JSONDecodeError:
            pytest.fail("Command should output valid JSON")

    @patch('services.sina_finance_service.SinaFinanceService.get_profile')
    @patch('services.sina_finance_service.SinaFinanceService.get_quote')
    @patch('services.sina_finance_service.SinaFinanceService.get_financials')
    @patch('services.sina_finance_service.SinaFinanceService.get_shareholder_structure')
    def test_info_command_with_all_options(self, mock_get_structure, mock_get_financials, mock_get_quote, mock_get_profile):
        """Test info command with all optional data."""
        # Mock profile
        mock_profile = MagicMock()
        mock_profile.to_dict.return_value = {'symbol': '000001', 'name': '平安银行'}
        mock_get_profile.return_value = mock_profile

        # Mock quote
        mock_quote = MagicMock()
        mock_quote.to_dict.return_value = {'symbol': '000001', 'price': 10.50}
        mock_get_quote.return_value = mock_quote

        # Mock financials
        mock_financial = MagicMock()
        mock_financial.to_dict.return_value = {'symbol': '000001', 'period': '2023Q4', 'revenue': 1000000000.0}
        mock_get_financials.return_value = [mock_financial]

        # Mock structure
        mock_structure = MagicMock()
        mock_structure.to_dict.return_value = {'symbol': '000001', 'total_shareholders': 1250}
        mock_get_structure.return_value = mock_structure

        runner = CliRunner()
        result = runner.invoke(cli, [
            "info", "000001",
            "--include-financials",
            "--include-shareholders",
            "--include-dividends",
            "--include-press"
        ])

        assert result.exit_code == 0

        # Should output valid JSON with all sections
        try:
            data = json.loads(result.output.strip())
            assert isinstance(data, dict)
            assert 'profile' in data
            assert 'quote' in data
            assert 'financials' in data
            assert 'shareholder_structure' in data
            # dividends and press are mocked to return empty lists
            assert 'dividends' in data
            assert 'press_releases' in data
        except json.JSONDecodeError:
            pytest.fail("Command should output valid JSON")

    @patch('services.sina_finance_service.SinaFinanceService.get_profile')
    @patch('services.sina_finance_service.SinaFinanceService.get_quote')
    def test_info_command_profile_failure(self, mock_get_quote, mock_get_profile):
        """Test info command when profile fetch fails."""
        mock_get_profile.return_value = None

        mock_quote = MagicMock()
        mock_quote.to_dict.return_value = {'symbol': '000001', 'price': 10.50}
        mock_get_quote.return_value = mock_quote

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "000001"])

        assert result.exit_code == 0
        assert "Warning: Could not fetch company profile" in result.output

    @patch('services.sina_finance_service.SinaFinanceService.get_profile')
    @patch('services.sina_finance_service.SinaFinanceService.get_quote')
    def test_info_command_quote_failure(self, mock_get_quote, mock_get_profile):
        """Test info command when quote fetch fails."""
        mock_profile = MagicMock()
        mock_profile.to_dict.return_value = {'symbol': '000001', 'name': '平安银行'}
        mock_get_profile.return_value = mock_profile

        mock_get_quote.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "000001"])

        assert result.exit_code == 0
        assert "Warning: Could not fetch real-time quote" in result.output

    @patch('services.sina_finance_service.SinaFinanceService.get_profile')
    def test_info_command_complete_failure(self, mock_get_profile):
        """Test info command when all fetches fail."""
        mock_get_profile.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ["info", "000001"])

        assert result.exit_code == 0

        # Should still output valid JSON (empty dict)
        try:
            data = json.loads(result.output.strip())
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Command should output valid JSON even on failures")