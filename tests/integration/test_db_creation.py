"""Integration tests for database creation and basic operations."""

import tempfile
import os
from services.database_service import DatabaseService


class TestDatabaseCreationIntegration:
    """Integration tests for database creation functionality."""

    def test_full_database_lifecycle(self):
        """Test complete database creation and basic operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "integration_test.db")

            # Create database
            service = DatabaseService(db_path)
            assert service.initialize_database() is True
            assert os.path.exists(db_path)

            # Test connection and basic operations
            conn = service.get_connection()
            assert conn.is_connected()

            # Test basic table operations
            result = conn.execute(
                "SELECT table_name FROM duckdb_tables WHERE table_name = 'stock_name_code'"
            )
            tables = result.fetchall()
            assert len(tables) == 1, "Stock_name_code table should exist"
            assert tables[0][0] == "stock_name_code"

            # Close connection
            conn.disconnect()

    def test_database_persistence(self):
        """Test that database persists data across connections."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "persistence_test.db")

            # Create and populate database
            service1 = DatabaseService(db_path)
            service1.initialize_database()

            conn1 = service1.get_connection()
            conn1.execute(
                "INSERT INTO stock_name_code (code, name) VALUES (?, ?)",
                ("000001", "Test Stock"),
            )

            # Close first connection
            conn1.disconnect()

            # Open new connection and verify data
            service2 = DatabaseService(db_path)
            service2.initialize_database()  # Re-initialize (safe since table exists)
            conn2 = service2.get_connection()

            result = conn2.execute(
                "SELECT code, name FROM stock_name_code WHERE code = ?", ("000001",)
            )
            rows = result.fetchall()
            assert len(rows) == 1
            assert rows[0][0] == "000001"
            assert rows[0][1] == "Test Stock"

            # Close connection
            conn2.disconnect()

    def test_concurrent_access(self):
        """Test database behavior with concurrent access."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "concurrent_test.db")

            # Initialize database
            service = DatabaseService(db_path)
            service.initialize_database()

            # Simulate concurrent access (basic test)
            conn1 = service.get_connection()
            conn2 = service.get_connection()  # Same connection instance

            # Both should work
            conn1.execute(
                "INSERT INTO stock_name_code (code, name) VALUES (?, ?)",
                ("000001", "Stock 1"),
            )
            conn2.execute(
                "INSERT INTO stock_name_code (code, name) VALUES (?, ?)",
                ("000002", "Stock 2"),
            )

            result = conn1.execute("SELECT COUNT(*) FROM stock_name_code")
            count = result.fetchone()[0]
            assert count == 2, "Both inserts should succeed"

            # Close connection
            conn1.disconnect()
