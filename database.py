import sqlite3
import typing


class WorkspaceData:
    def __init__(self):
        self.connect = sqlite3.connect("database.db")
        self.connect.row_factory = sqlite3.Row
        self.cursor = self.connect.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS watchlist (symbol TEXT, exchange TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS strategies (strategy_type TEXT, contract TEXT, "
                            "timeframe TEXT, balance_pct REAL, take_profit REAL, stop_loss REAL, extra_params TEXT)")

        self.connect.commit()

    def save(self, table: str, data: typing.List[typing.Tuple]):
        self.cursor.execute(f"DELETE FROM {table}")

        table_data = self.cursor.execute(f"SELECT * FROM {table}")

        columns = [description[0] for description in table_data.description]

        sql_statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"

        self.cursor.executemany(sql_statement, data)
        self.connect.commit()

    def get(self, table: str) -> typing.List[sqlite3.Row]:
        self.connect.execute("SELECT * FROM {table}")
        data = self.cursor.fetchall()

        return data
    