"""Contract tests for CLI commands."""

import pytest
import tempfile
import os
import json
from click.testing import CliRunner
from cli.commands import cli


class TestCliContract:
    """Contract tests for CLI command interfaces."""

    def test_init_db_command_basic(self):
        """Test init-db command creates database file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            result = runner.invoke(cli, ["init-db", "--db-path", db_path])

            assert result.exit_code == 0
            assert os.path.exists(db_path)
            assert "Database initialized successfully" in result.output

    def test_init_db_command_default_path(self):
        """Test init-db command with default path."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init-db", "--default"])

        assert result.exit_code == 0
        assert "Database initialized successfully" in result.output

    def test_fetch_stocks_validate_only(self):
        """Test fetch-stocks command with validate-only flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fetch-stocks", "--validate-only"])

        assert result.exit_code == 0
        # Should output JSON array
        try:
            data = json.loads(result.output.strip())
            assert isinstance(data, list)
            if data:  # If we got sample data
                assert "code" in data[0]
                assert "name" in data[0]
        except json.JSONDecodeError:
            pytest.fail("Command should output valid JSON")

    def test_fetch_stocks_with_database(self):
        """Test fetch-stocks command with database storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            # First initialize database
            init_result = runner.invoke(cli, ["init-db", "--db-path", db_path])
            assert init_result.exit_code == 0

            # Then fetch and store stocks
            result = runner.invoke(cli, ["fetch-stocks", "--db-path", db_path])

            assert result.exit_code == 0
            assert "Successfully stored" in result.output
            assert "stocks in database" in result.output

    def test_list_stocks_command(self):
        """Test list-stocks command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            # First initialize database and add some stocks
            runner.invoke(cli, ["init-db", "--db-path", db_path])
            runner.invoke(cli, ["fetch-stocks", "--db-path", db_path])

            # Then list stocks
            result = runner.invoke(cli, ["list-stocks", "--db-path", db_path, "--limit", "5"])

            assert result.exit_code == 0
            # Should output JSON array
            try:
                data = json.loads(result.output.strip())
                assert isinstance(data, list)
                if len(data) > 0:
                    assert "code" in data[0]
                    assert "name" in data[0]
            except json.JSONDecodeError:
                pytest.fail("Command should output valid JSON")

    def test_list_tables_command(self):
        """Test list-tables command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            # First initialize database
            runner.invoke(cli, ["init-db", "--db-path", db_path])

            # Then list tables
            result = runner.invoke(cli, ["list-tables", "--db-path", db_path])

            assert result.exit_code == 0
            # Should output JSON array
            try:
                data = json.loads(result.output.strip())
                assert isinstance(data, list)
            except json.JSONDecodeError:
                pytest.fail("Command should output valid JSON")

    def test_get_historical_command(self):
        """Test get-historical command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            # First initialize database and add some stocks
            runner.invoke(cli, ["init-db", "--db-path", db_path])
            runner.invoke(cli, ["fetch-stocks", "--db-path", db_path])

            # Try to get historical data (may not have any, but should not crash)
            result = runner.invoke(cli, ["get-historical", "000001", "--db-path", db_path])

            # Should not crash, even if no data
            assert result.exit_code == 0
            assert "000001" in result.output

    def test_sync_historical_command_help(self):
        """Test sync-historical command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["sync-historical", "--help"])

        assert result.exit_code == 0
        assert "Sync historical data" in result.output
        assert "--max-threads" in result.output
        assert "--force-full-sync" in result.output

    def test_list_stocks_empty_database(self):
        """Test list-stocks command with empty database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            # Initialize database but don't add stocks
            runner.invoke(cli, ["init-db", "--db-path", db_path])

            # List stocks should return empty array
            result = runner.invoke(cli, ["list-stocks", "--db-path", db_path])

            assert result.exit_code == 0
            try:
                data = json.loads(result.output.strip())
                assert isinstance(data, list)
                assert len(data) == 0
            except json.JSONDecodeError:
                pytest.fail("Command should output valid JSON")
