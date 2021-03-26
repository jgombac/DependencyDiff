from postgres import Postgres

conn_str = "postgresql://localhost:5432/test_db?user=root&password=root"

class Database:

    def __init__(self, connection_str: str):
        self.db = Postgres(connection_str)
        self.db.run("CREATE TABLE foo (bar text, baz int)")


db = Database(conn_str)