import sqlite3
import argparse
import sys
from typing import List, Tuple


def create_connection(db_path: str) -> sqlite3.Connection:
    """Create a database connection to the SQLite database specified by db_path."""
    try:
        connection = sqlite3.connect(db_path)
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    """Check if a table exists in the database."""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None


def create_student_table(cursor: sqlite3.Cursor) -> None:
    """Create the STUDENT table if it doesn't exist."""
    table_info = """
    CREATE TABLE IF NOT EXISTS STUDENT(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME VARCHAR(25) NOT NULL,
        CLASS VARCHAR(25) NOT NULL,
        SECTION VARCHAR(25) NOT NULL,
        MARKS INT NOT NULL,
        UNIQUE(NAME, CLASS, SECTION)
    )
    """
    cursor.execute(table_info)


def get_sample_data() -> List[Tuple[str, str, str, int]]:
    """Return sample student data."""
    return [
        ('Krish', 'Data Science', 'A', 90),
        ('John', 'Data Science', 'B', 100),
        ('Mukesh', 'Data Science', 'A', 86),
        ('Jacob', 'DEVOPS', 'A', 50),
        ('Dipesh', 'DEVOPS', 'A', 35)
    ]


def insert_student_data(cursor: sqlite3.Cursor, data: List[Tuple[str, str, str, int]], 
                       mode: str = 'append') -> None:
    """Insert student data, avoiding duplicates."""
    if mode == 'recreate':
        cursor.execute("DELETE FROM STUDENT")
        print("Cleared existing data (recreate mode)")
    
    insert_query = """
    INSERT OR IGNORE INTO STUDENT (NAME, CLASS, SECTION, MARKS) 
    VALUES (?, ?, ?, ?)
    """
    
    for student in data:
        cursor.execute(insert_query, student)
    
    print(f"Inserted/updated {len(data)} student records")


def display_records(cursor: sqlite3.Cursor) -> None:
    """Display all student records."""
    print("\nCurrent student records:")
    print("-" * 50)
    cursor.execute("SELECT NAME, CLASS, SECTION, MARKS FROM STUDENT ORDER BY NAME")
    records = cursor.fetchall()
    
    if not records:
        print("No records found.")
        return
    
    for record in records:
        print(f"Name: {record[0]}, Class: {record[1]}, Section: {record[2]}, Marks: {record[3]}")


def main():
    """Main function to set up the database."""
    parser = argparse.ArgumentParser(description='Idempotent SQLite database setup script')
    parser.add_argument('--db-path', default='student.db', 
                       help='Path to the SQLite database file (default: student.db)')
    parser.add_argument('--mode', choices=['append', 'recreate'], default='append',
                       help='Mode: append (default) or recreate (clear existing data)')
    parser.add_argument('--no-display', action='store_true',
                       help='Skip displaying records after setup')
    
    args = parser.parse_args()
    
    print(f"Setting up database: {args.db_path}")
    print(f"Mode: {args.mode}")
    
    # Create connection
    connection = create_connection(args.db_path)
    cursor = connection.cursor()
    
    try:
        # Create table if it doesn't exist
        create_student_table(cursor)
        print("+ Table created/verified")
        
        # Insert sample data
        sample_data = get_sample_data()
        insert_student_data(cursor, sample_data, args.mode)
        
        # Display records unless --no-display is specified
        if not args.no_display:
            display_records(cursor)
        
        # Commit changes
        connection.commit()
        print("\n+ Database setup completed successfully")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        connection.rollback()
        sys.exit(1)
    finally:
        connection.close()


if __name__ == "__main__":
    main()