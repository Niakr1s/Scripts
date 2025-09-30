import argparse
import sqlite3


class JavguruDatabase:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with the required table structure"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT NOT NULL PRIMARY KEY,
                    description TEXT NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 10),
                    comment TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create trigger to update timestamp only when rating or comment changes
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_timestamp
                AFTER UPDATE ON items
                FOR EACH ROW
                WHEN OLD.rating IS NOT NEW.rating OR OLD.comment IS NOT NEW.comment
                BEGIN
                    UPDATE items SET timestamp = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)

    def insert_row(self, id, description):
        """Insert new row with id and description. If id exists, do nothing and print warning."""

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO items (id, description) VALUES (?, ?)",
                    (id, description),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                print(f"Warning: ID '{id}' already exists. No action taken.")

    def update_rating(self, id, rating):
        """Update rating for a specific ID"""
        if rating is not None and (rating < 1 or rating > 10):
            raise ValueError("Rating must be between 1 and 10 or None")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE items SET rating = ? WHERE id = ?", (rating, id)
            )
            conn.commit()

            if cursor.rowcount == 0:
                print(f"Warning: ID '{id}' not found. No rating updated.")
            else:
                print(f"Successfully updated rating for ID: {id}")

    def update_comment(self, id, comment):
        """Update comment for a specific ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE items SET comment = ? WHERE id = ?", (comment, id)
            )
            conn.commit()

            if cursor.rowcount == 0:
                print(f"Warning: ID '{id}' not found. No comment updated.")
            else:
                print(f"Successfully updated comment for ID: {id}")


def test():
    parser = argparse.ArgumentParser(description="SQLite Database Manager")
    parser.add_argument(
        "--db", default="database.db", help="Database file path (default: database.db)"
    )
    args = parser.parse_args()

    # Example usage
    db = JavguruDatabase(args.db)

    # Example operations
    try:
        # Insert new rows
        db.insert_row("12345678901234567890", "Test Item 1")
        db.insert_row("12345678901234567891", "Test Item 2")

        # Try to insert duplicate ID
        db.insert_row("12345678901234567890", "Duplicate Item")

        # Update ratings
        db.update_rating("12345678901234567890", 8)
        db.update_rating("12345678901234567891", None)

        # Update comments
        db.update_comment("12345678901234567890", "Great item!")
        db.update_comment("12345678901234567891", "Needs improvement")

        # Try to update non-existent ID
        db.update_rating("nonexistent123456789", 5)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test()
