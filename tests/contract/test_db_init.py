"""Contract tests for database initialization."""

import pytest
import tempfile
import os
from services.database_service import DatabaseService


class TestDatabaseInitializationContract:
    """Contract tests for database initialization functionality."""

    def test_database_file_creation(self):
        """Test that database file is created at specified path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            assert not os.path.exists(db_path), "Database should not exist yet"

            service = DatabaseService(db_path)
            result = service.initialize_database()

            assert result is True, "Database initialization should succeed"
            assert os.path.exists(db_path), "Database file should be created"

            # Close connection to allow cleanup
            service.db_connection.disconnect()

    def test_default_path_usage(self):
        """Test that default path is used when no custom path provided."""
        # Test with None path - should use default
        service = DatabaseService()
        # This should work with default path
        result = service.initialize_database()
        assert result is True, (
            "Database initialization with default path should succeed"
        )

        # Close connection
        service.db_connection.disconnect()

    def test_database_connection(self):
        """Test that database connection can be established."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            service = DatabaseService(db_path)
            service.initialize_database()

            conn = service.get_connection()
            assert conn.is_connected(), "Connection should be established"

            # Close connection to allow cleanup
            conn.disconnect()

    def test_invalid_path_handling(self):
        """Test handling of invalid database paths."""
        # This should still work as Config.ensure_path_exists handles directory creation
        invalid_path = "/invalid/path/that/does/not/exist/database.db"

        service = DatabaseService(invalid_path)
        result = service.initialize_database()
        # Should succeed because we create parent directories
        assert result is True, "Database initialization should handle path creation"

        # Close connection
        service.db_connection.disconnect()
