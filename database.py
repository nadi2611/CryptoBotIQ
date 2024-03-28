import sqlite3
import typing
import threading

class WorkspaceData:
    def __init__(self):
        # Initialize threading local storage for database connections
        self.local_storage = threading.local()

    def _get_connection(self):
        # Create a new database connection if it doesn't exist in the current thread
        if not hasattr(self.local_storage, 'connection'):
            self.local_storage.connection = sqlite3.connect("database.db")
            self.local_storage.connection.row_factory = sqlite3.Row  # Makes the data retrieved from the database accessible by their column name
        return self.local_storage.connection

    def save(self, table: str, data: typing.List[typing.Tuple]):
        # Get the database connection for the current thread
        conn = self._get_connection()
        cursor = conn.cursor()

        # Erase the previous table content
        cursor.execute(f"DELETE FROM {table}")

        # Get the columns of the table
        table_data = cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in table_data.description]

        # Create the SQL insert statement dynamically
        sql_statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"

        # Insert new data into the table
        cursor.executemany(sql_statement, data)

        # Commit changes
        conn.commit()

    def get(self, table: str) -> typing.List[sqlite3.Row]:
        # Get the database connection for the current thread
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get all the rows recorded for the table
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()

        return data
