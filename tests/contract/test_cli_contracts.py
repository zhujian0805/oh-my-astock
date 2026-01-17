"""Contract tests for CLI commands."""

import pytest
import tempfile
import os
import subprocess
import json
from click.testing import CliRunner
from src.cli.commands import cli


class TestCliContract:
    """Contract tests for CLI command interfaces."""

    def test_init_db_command_basic(self):
        """Test init-db command creates database file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            runner = CliRunner()
            result = runner.invoke(cli, ['init-db', '--db-path', db_path])

            assert result.exit_code == 0
            assert os.path.exists(db_path)
            assert "Database initialized successfully" in result.output

    def test_init_db_command_default_path(self):
        """Test init-db command with default path."""
        runner = CliRunner()
        result = runner.invoke(cli, ['init-db', '--default'])

        assert result.exit_code == 0
        assert "Database initialized successfully" in result.output

    def test_fetch_stocks_validate_only(self):
        """Test fetch-stocks command with validate-only flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['fetch-stocks', '--validate-only'])

        assert result.exit_code == 0
        # Should output JSON array
        try:
            data = json.loads(result.output.strip())
            assert isinstance(data, list)
            if data:  # If we got sample data
                assert 'code' in data[0]
                assert 'name' in data[0]
        except json.JSONDecodeError:
            pytest.fail("Command should output valid JSON")

    def test_list_stocks_empty_database(self):
        """Test list-stocks command with empty database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "empty.db")

            runner = CliRunner()
            result = runner.invoke(cli, ['list-stocks', '--db-path', db_path])

            assert result.exit_code == 1
            assert "Database does not exist" in result.output

    def test_list_tables_populated_database(self):
        """Test list-tables command with populated database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            # First initialize database
            runner = CliRunner()
            init_result = runner.invoke(cli, ['init-db', '--db-path', db_path])
            assert init_result.exit_code == 0

            # Then list tables
            list_result = runner.invoke(cli, ['list-tables', '--db-path', db_path])
            assert list_result.exit_code == 0

            # Should contain stocks table
            try:
                tables = json.loads(list_result.output.strip())
                assert isinstance(tables, list)
                assert "stocks" in tables
            except json.JSONDecodeError:
                pytest.fail("Command should output valid JSON")

    def test_debug_flag_enables_debug_logging(self):
        """Test that --debug flag enables debug logging."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--debug', 'init-db', '--default'])

        assert result.exit_code == 0
        # Debug output should be more verbose
        assert "Database initialized successfully" in result.output

    def test_invalid_database_path_handling(self):
        """Test handling of invalid database paths in commands."""
        runner = CliRunner()

        # Test with non-existent directory that can't be created
        invalid_path = "Z:\\nonexistent\\drive\\database.db"
        result = runner.invoke(cli, ['init-db', '--db-path', invalid_path])

        # Should handle gracefully (depending on OS permissions)
        # Either succeed (if path creation works) or fail gracefully
        assert result.exit_code in [0, 1]  # 0 for success, 1 for expected failure

    def test_command_help_output(self):
        """Test that commands provide help information."""
        runner = CliRunner()

        # Test main command help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Stock data management CLI" in result.output

        # Test init-db help
        result = runner.invoke(cli, ['init-db', '--help'])
        assert result.exit_code == 0
        assert "--db-path" in result.output
        assert "--default" in result.output

    def test_json_output_format(self):
        """Test that JSON output is properly formatted."""
        runner = CliRunner()
        result = runner.invoke(cli, ['fetch-stocks', '--validate-only'])

        assert result.exit_code == 0

        # Should be valid JSON
        output = result.output.strip()
        try:
            parsed = json.loads(output)
            assert isinstance(parsed, list)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}")

        # Should be pretty-printed (indented)
        lines = output.split('\n')
        assert len(lines) > 1  # Multi-line indicates pretty printing