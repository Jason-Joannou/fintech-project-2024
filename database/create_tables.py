# from .sql_connection import sql_connection
from sqlalchemy import text

from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()

# URL refers to the openAPI address of the stokvel


def create_stokvel_members_table_sqlite() -> None:
    """
    Create STOKVEL_MEMBERS table with a unique constraint on (stokvel_id, user_id) to prevent duplicate entries.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS STOKVEL_MEMBERS (
                id INTEGER PRIMARY KEY,
                stokvel_id INTEGER,
                user_id INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                UNIQUE (stokvel_id, user_id)  -- Ensure stokvel_id and user_id combination is unique
            )
        """
            )
        )


def create_stokvel_table_sqlite() -> None:
    """
    Create STOKVELS table with a unique constraint on stokvel_id.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS STOKVELS (
                stokvel_id INTEGER PRIMARY KEY,
                stokvel_name TEXT UNIQUE,  -- Add UNIQUE constraint here
                ILP_wallet TEXT,
                MOMO_wallet TEXT,
                total_members INTEGER,
                min_contributing_amount NUMBER,
                max_number_of_contributors INTEGER,
                Total_contributions NUMBER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """
            )
        )


def create_user_table_sqlite() -> None:
    """
    Create USERS table with a unique constraint on user_id.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS USERS (
                user_id INTEGER PRIMARY KEY,
                user_number TEXT,
                user_name TEXT,
                user_surname TEXT,
                ILP_wallet TEXT,
                MOMO_wallet TEXT,
                verified_KYC INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                UNIQUE (user_id)  -- Ensure user_id is unique
            );
        """
            )
        )


def create_transaction_table_sqlite() -> None:
    """
    Create TRANSACTIONS table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS TRANSACTIONS (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                stokvel_id INTEGER,
                amount NUMBER,
                tx_type TEXT,
                wallet_type TEXT,
                tx_date TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
        );
    """
            )
        )


def create_resource_table_sqlite() -> None:
    """
    Create RESOURCES table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS RESOURCES (
                id INTEGER PRIMARY KEY,
                name TEXT,
                resource_type TEXT,
                url TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """
            )
        )


def create_admin_table_sqlite() -> None:
    """
    Create ADMIN table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS ADMIN (
                id INTEGER PRIMARY KEY,
                stokvel_id INTEGER,
                stokvel_name TEXT,
                user_id INTEGER,
                total_contributions NUMBER,
                total_members INTEGER,
                UNIQUE (stokvel_id, user_id)  -- Ensure each stokvel_id and user_id combination is unique
            );
        """
            )
        )


def create_contributions_table_sqlite() -> None:
    """
    Create CONTRIBUTIONS table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS CONTRIBUTIONS (
                id INTEGER PRIMARY KEY,
                stokvel_id INTEGER,
                user_id INTEGER,
                frequency_days INTEGER,
                StartDate DATETIME,
                EndDate DATETIME,
                contribution NUMBER,
                UNIQUE (stokvel_id, user_id)  -- Ensure each stokvel_id and user_id combination is unique
            );
        """
            )
        )


def create_user_wallet_table_sqlite() -> None:
    """
    Create USER_WALLET table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS USER_WALLET (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                user_wallet TEXT,
                UserBalance NUMBER,
                UNIQUE (id)  -- Ensure user_id is unique
            );
        """
            )
        )


def create_stokvel_wallet_table_sqlite() -> None:
    """
    Create STOKVEL_WALLET table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS STOKVEL_WALLET (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                user_wallet TEXT,
                UserBalance NUMBER,
                UNIQUE (id)  -- Ensure user_id is unique
            );
        """
            )
        )


def create_applications_table_sqlite() -> None:
    """
    Create APPLICATIONS table.
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS APPLICATIONS (
                id INTEGER PRIMARY KEY,
                stokvel_id INTEGER,
                user_id INTEGER,
                AppStatus TEXT,
                AppDate DATETIME            );
        """
            )
        )


def create_state_management_table() -> None:
    """
    docstring
    """

    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
        CREATE TABLE IF NOT EXISTS STATE_MANAGEMENT (
            id INTEGER PRIMARY KEY,
            user_number TEXT,
            last_interaction DATETIME,
            stack_state TEXT
        );
        """
            )
        )


if __name__ == "__main__":
    create_user_table_sqlite()
    create_resource_table_sqlite()
    create_admin_table_sqlite()
    create_contributions_table_sqlite()
    create_stokvel_members_table_sqlite()
    create_stokvel_table_sqlite()
    create_transaction_table_sqlite()
    create_user_wallet_table_sqlite()
    create_stokvel_wallet_table_sqlite()
    create_applications_table_sqlite()
    create_state_management_table()
