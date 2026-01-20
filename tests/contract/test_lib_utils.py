"""Contract tests for lib utilities."""

import os
import tempfile
from pathlib import Path
from lib.config import Config
from lib.debug import debug_metrics, timed_operation, debug_context, log_data_validation


class TestConfig:
    """Contract tests for Config utilities."""

    def test_get_database_path_custom_path(self):
        """Test get_database_path with custom path."""
        custom_path = "/custom/path/stock.db"
        result = Config.get_database_path(custom_path)
        assert result == Path(custom_path)

    def test_get_database_path_environment_variable(self, monkeypatch):
        """Test get_database_path with environment variable."""
        env_path = "/env/path/stock.db"
        monkeypatch.setenv("ASTOCK_DB_PATH", env_path)
        result = Config.get_database_path()
        assert result == Path(env_path)

    def test_get_database_path_default_path(self, monkeypatch):
        """Test get_database_path with default path."""
        # Clear environment variable
        monkeypatch.delenv("ASTOCK_DB_PATH", raising=False)
        result = Config.get_database_path()
        expected = Path.cwd() / "stock.duckdb"
        assert result == expected

    def test_ensure_path_exists_creates_directory(self):
        """Test ensure_path_exists creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "nested", "dirs", "stock.db")
            Config.ensure_path_exists(nested_path)
            assert os.path.exists(os.path.dirname(nested_path))

    def test_get_threads_returns_int(self):
        """Test get_threads returns an integer."""
        threads = Config.get_threads()
        assert isinstance(threads, int)
        assert threads > 0


class TestDebug:
    """Contract tests for debug utilities."""

    def test_debug_metrics_decorator(self):
        """Test debug_metrics decorator logs execution time."""
        @debug_metrics
        def sample_function():
            return "test result"

        result = sample_function()
        assert result == "test result"

    def test_timed_operation_decorator_without_parentheses(self):
        """Test timed_operation decorator without parentheses."""
        @timed_operation
        def sample_function():
            return "timed result"

        result = sample_function()
        assert result == "timed result"

    def test_timed_operation_decorator_with_name(self):
        """Test timed_operation decorator with custom name."""
        @timed_operation("custom operation")
        def sample_function():
            return "timed result"

        result = sample_function()
        assert result == "timed result"

    def test_debug_context_manager(self):
        """Test debug_context context manager."""
        with debug_context("test context", key="value"):
            pass  # Just test it doesn't crash

    def test_log_data_validation_passed(self):
        """Test log_data_validation with passed validation."""
        test_data = {"key": "value"}
        log_data_validation(test_data, True, "test context")
        # Should not raise exception

    def test_log_data_validation_failed(self):
        """Test log_data_validation with failed validation."""
        test_data = {"key": "value"}
        log_data_validation(test_data, False, "test context")
        # Should not raise exception