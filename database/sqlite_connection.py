import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SQLiteConnection:
    """
    This class manages the SQL connection to an SQLite database. It encapsulates the connection details, 
    such as the database file path. It provides methods to get an engine, a session, and a connection.

    Args:
        database (str): The name of the SQLite database file to connect to.
        _engine (sqlalchemy.engine): The engine that is used to interact with the database.
    """

    def __init__(self, database=None):
        """
        The constructor for the SQLiteConnection. It initializes the connection parameters.
        """
        if database is not None:
            self.database = database
            self._engine = None
        else:
            raise ValueError(f"Database connection not established, connection = {database}")

    def get_engine(self):
        """
        This method returns a sqlalchemy engine that is used to interact with the SQLite database.
        If the engine is not yet created, it will create one.

        Returns:
            sqlalchemy.engine: The engine to interact with the SQLite database.

        Raises:
            Exception: An error occurred creating the engine.
        """
        if not os.path.exists(self.database):
            raise FileNotFoundError(f"SQLite database file '{self.database}' not found")
    
        if not self._engine:
            try:
                self._engine = create_engine(
                    f"sqlite:///{self.database}"
                )
            except Exception as e:
                logging.error(f'Error creating SQLite engine: {e}')
                raise
        return self._engine
    
    def get_session(self):
        """
        This method returns a sqlalchemy session that is bound to the engine.

        Returns:
            sqlalchemy.orm.session.Session: The session to interact with the SQLite database.
        """
        session = sessionmaker(bind=self.get_engine())
        return session()
    
    def connect(self):
        """
        This method returns a connection to the SQLite database using the engine.

        Returns:
            sqlalchemy.engine.Connection: The connection to the SQLite database.
        """
        try:
            connection = self.get_engine().connect()
            return connection
        except Exception as e:
            logging.error(f'Error establishing SQL connection: {e}')
            raise
        
    def test_connection(self):
        """
        This method returns a connection to the SQLite database using the engine.

        Returns:
            sqlalchemy.engine.Connection: The connection to the SQLite database.
        """
        try:
            connection = self.get_engine().connect()
            response = {"connection_status": "complete", "message": "Successfully established SQLite connection."}
            return response
        except Exception as e:
            response = {"connection_status": "incomplete", "message": f'Error establishing SQLite connection: {e}'}
            return response

# Usage example
if __name__ == "__main__":
    connection = SQLiteConnection(database="test.db")
    engine = connection.get_engine()
    session = connection.get_session()
    conn = connection.connect()
    print("Connected to SQLite database successfully.")
