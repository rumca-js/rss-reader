from sqlalchemy import create_engine

from linkarchivetools.utils.reflected import (
   ReflectedEntryTable,
   ReflectedSourceTable,
   ReflectedTable,
)

class DbConnection(object):
    def __init__(self, db_file):
        self.db_file = db_file

        self.engine = DbConnection.create_engine(self.db_file)
        self.connection = self.engine.connect()

        self.entries_table = ReflectedEntryTable(engine=self.engine, connection=self.connection)
        self.sources_table = ReflectedSourceTable(engine=self.engine, connection=self.connection)

    def create_engine(db_file):
        engine = create_engine(f"sqlite:///{db_file}")
        return engine

    def truncate(self):
        self.entries_table.truncate()
        self.sources_table.truncate()

        table = ReflectedTable(engine=self.engine, connection=self.connection)
        table.vacuum()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
