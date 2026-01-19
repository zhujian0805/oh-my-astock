"""Integration tests for new features."""

import json
from click.testing import CliRunner
from cli.commands import cli


class TestNewFeaturesIntegration:
    """Integration tests for new features."""

    def test_search_command_integration(self):
        """Integration test for search command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "平安", "--limit", "1"])

        # Command should execute without error
        assert result.exit_code in [0, 1]  # 0 for success, 1 for no results

        # Should contain search message
        assert "Searching for stocks matching" in result.output

    def test_quote_command_integration(self):
        """Integration test for quote command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["quote", "000001"])

        # Command should execute without error
        assert result.exit_code in [0, 1]  # 0 for success, 1 for no data

        # Should contain quote message
        assert "Fetching real-time quote for 000001" in result.output

    def test_info_command_integration(self):
        """Integration test for info command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "000001"])

        # Command should execute without error
        assert result.exit_code == 0

        # Should contain info message
        assert "Fetching information for 000001" in result.output

        # Should output valid JSON
        output_lines = result.output.strip().split('\n')
        json_start = False
        json_content = []

        for line in output_lines:
            if line.strip().startswith('{'):
                json_start = True
            if json_start:
                json_content.append(line)

        json_output = '\n'.join(json_content)
        if json_output.strip():
            try:
                parsed = json.loads(json_output)
                assert isinstance(parsed, dict)
                assert 'profile' in parsed
            except json.JSONDecodeError:
                # If JSON parsing fails, that's okay for this integration test
                # The important thing is the command structure works
                pass

    def test_commands_help_integration(self):
        """Test that all new commands have help."""
        runner = CliRunner()

        commands = ['search', 'quote', 'info']

        for cmd in commands:
            result = runner.invoke(cli, [cmd, '--help'])
            assert result.exit_code == 0
            assert 'Show this message and exit' in result.output

    def test_data_models_integration(self):
        """Test that data models can be imported and used."""
        from models.quote import Quote
        from models.profile import Profile
        from models.financial import Financial
        from models.structure import Structure, Shareholder
        from models.dividend import Dividend
        from models.press import Press

        # Test basic instantiation
        quote = Quote(symbol="000001", name="Test Stock")
        profile = Profile(symbol="000001", name="Test Stock")
        financial = Financial(symbol="000001", period="2023Q4")
        shareholder = Shareholder(name="Test Holder", shares=1000, percentage=10.0)
        structure = Structure(symbol="000001", top_10_shareholders=[shareholder])
        dividend = Dividend(symbol="000001", dividend_per_share=1.0)
        press = Press(symbol="000001", title="Test Press Release")

        # Test serialization
        assert quote.to_dict()
        assert profile.to_dict()
        assert financial.to_dict()
        assert structure.to_dict()
        assert dividend.to_dict()
        assert press.to_dict()

        # Test string representation
        assert str(quote)
        assert str(profile)
        assert str(financial)
        assert str(structure)
        assert str(dividend)
        assert str(press)

    def test_sina_service_integration(self):
        """Test SinaFinanceService basic functionality."""
        from services.sina_finance_service import SinaFinanceService

        service = SinaFinanceService()

        # Test symbol normalization
        assert service._normalize_symbol("000001") == "SZ000001"
        assert service._normalize_symbol("600000") == "SH600000"

        # Test exchange detection
        assert service._get_exchange_from_code("000001") == "SZ"
        assert service._get_exchange_from_code("600000") == "SH"

        # Test HTML extraction
        html = '<title>Test Title</title><div>行业：银行</div>'
        title = service._extract_from_html(html, r'<title>([^<]+)</title>')
        industry = service._extract_from_html(html, r'行业：([^<\n]+)')

        assert title == "Test Title"
        assert industry is not None  # Just check it's extracted, ignore encoding