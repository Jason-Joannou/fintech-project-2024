import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


ENV = load_dotenv(dotenv_path=r"./.env", override=True)


class SqlConnection:
    """
    This class manages the SQL connection to a database. It encapsulates the connection details, such as the server, 
    database, username and password. It provides methods to get an engine, a session, and a connection.

    Args:
        server (str): The server to connect to.
        database (str): The name of the database to connect to.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication. Read from environment variables for security.
        _engine (sqlalchemy.engine): The engine that is used to interact with the database.
    """

    def __init__(self, server=None, database=None, username=None, password=None):
        """
        The constructor for the SQLConnection. It initializes the connection parameters.
        """

        env_keys = ["DB_SERVER", "DB_DATABASE", "DB_USERNAME", "DB_PASSWORD"]
        missing = []
        for k in env_keys:
            if not os.getenv(k):
                missing.append(k)

        if len(missing) > 0:
            raise ValueError(f"Missing sql server related environment variables in .env file: `{missing}`")

        self.server = os.getenv("DB_SERVER", server)
        self.database = os.getenv("DB_DATABASE", database)
        self.username = os.getenv("DB_USERNAME", username)
        self.password = os.getenv("DB_PASSWORD", password)
        self._engine = None

        logging.info("Read environment variables - server: %s, database: %s, username: %s", self.server, self.database, self.username)


        if '@' in self.username:
            raise ValueError("Username cannot contain '@'")
        if '@' in self.password:
            raise ValueError("Password cannot contain '@'")

    def get_engine(self):
        """
        This method returns a sqlalchemy engine that is used to interact with the database.
        If the engine is not yet created, it will create one.

        Returns:
            sqlalchemy.engine: The engine to interact with the database.

        Raises:
            Exception: An error occurred creating the engine.
        """
        if not self._engine:
            try:
                self._engine = create_engine(
                    f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server",
                    fast_executemany=True
                )
            except Exception as e:
                logging.error("Error creating SQL engine: %s", e)
                raise
        return self._engine
    
    def get_session(self):
        """
        This method returns a sqlalchemy session that is bound to the engine.

        Returns:
            sqlalchemy.orm.session.Session: The session to interact with the database.
        """
        session = sessionmaker(bind=self.get_engine())
        return session()
    
    def connect(self):
        """
        This method returns a connection to the database using the engine.

        Returns:
            sqlalchemy.engine.Connection: The connection to the database.
        """
        try:
            connection = self.get_engine().connect()
            logging.info("Successfully established SQL connection.")
            return connection
        except Exception as e:
            logging.error("Error establishing SQL connection: %s", e)
            raise