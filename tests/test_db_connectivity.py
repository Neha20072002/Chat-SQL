"""
Minimal tests for SQLite database connectivity and STUDENT table existence.
"""
import sqlite3
import pytest
import os
from pathlib import Path


class TestDatabaseConnectivity:
    """Test class for database connectivity and basic operations."""
    
    @pytest.fixture
    def db_path(self):
        """Get the path to the student.db file."""
        return Path(__file__).parent.parent / "student.db"
    
    @pytest.fixture
    def connection(self, db_path):
        """Create a database connection for testing."""
        if not db_path.exists():
            pytest.skip(f"Database file not found at {db_path}")
        
        conn = sqlite3.connect(str(db_path))
        yield conn
        conn.close()
    
    def test_database_file_exists(self, db_path):
        """Test that the student.db file exists."""
        assert db_path.exists(), f"Database file should exist at {db_path}"
    
    def test_database_connection(self, connection):
        """Test that we can connect to the SQLite database."""
        assert connection is not None, "Database connection should be established"
        
        # Test basic query to ensure connection is working
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1, "Basic query should return expected result"
    
    def test_student_table_exists(self, connection):
        """Test that the STUDENT table exists in the database."""
        cursor = connection.cursor()
        
        # Query to check if STUDENT table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='STUDENT'
        """)
        result = cursor.fetchone()
        
        assert result is not None, "STUDENT table should exist in the database"
        assert result[0] == "STUDENT", "Table name should match 'STUDENT'"
    
    def test_student_table_structure(self, connection):
        """Test that the STUDENT table has the expected columns."""
        cursor = connection.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(STUDENT)")
        columns = cursor.fetchall()
        
        # Expected columns: NAME, CLASS, SECTION, MARKS
        expected_columns = ["NAME", "CLASS", "SECTION", "MARKS"]
        actual_columns = [col[1] for col in columns]
        
        for expected_col in expected_columns:
            assert expected_col in actual_columns, f"Column '{expected_col}' should exist in STUDENT table"
    
    def test_student_table_has_data(self, connection):
        """Test that the STUDENT table contains some data."""
        cursor = connection.cursor()
        
        # Count records in STUDENT table
        cursor.execute("SELECT COUNT(*) FROM STUDENT")
        count = cursor.fetchone()[0]
        
        assert count > 0, "STUDENT table should contain at least one record"
        
        # Verify we can fetch some data
        cursor.execute("SELECT * FROM STUDENT LIMIT 1")
        sample_record = cursor.fetchone()
        assert sample_record is not None, "Should be able to fetch at least one record"
        assert len(sample_record) == 4, "Each record should have 4 columns (NAME, CLASS, SECTION, MARKS)"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
