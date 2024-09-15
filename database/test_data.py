from sqlalchemy import text
from datetime import datetime
from sqlalchemy import exc, select, func
from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")

def get_next_unique_id(conn, table_name, id_column):
    """
    Get the next unique id for the given table and id column.
    """
    result = conn.execute(
        text(f"SELECT MAX({id_column}) FROM {table_name}")
    ).fetchone()
    # If no result exists (table is empty), return 1, otherwise increment the max id
    return (result[0] or 0) + 1

def create_test_data():
    """
    Create test data for all tables with unique user_id and stokvel_id,
    and print success or failure messages for each entry.
    """
    try:
        with sqlite_conn.connect() as conn:
            # Get unique user_id and stokvel_id
            user_id = get_next_unique_id(conn, 'USERS', 'user_id')
            stokvel_id = get_next_unique_id(conn, 'STOKVELS', 'stokvel_id')

            # Insert test data for USERS table

            test_user = {
                'user_id': user_id,
                'user_number': '+1234567',
                'user_name': "John",
                'user_surname': "Doe" ,
                'ILP_wallet': "123ILP" ,
                'MOMO_wallet': "123MOMO",
                'verified_KYC': 1,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

                # SQL query for inserting data
            insert_query = """
                INSERT INTO USERS (user_id, user_number, user_name ,user_surname, ILP_wallet, MOMO_wallet, verified_KYC, created_at, updated_at)
            VALUES (:user_id, :user_number,:user_name, :user_surname, :ILP_wallet, :MOMO_wallet, :verified_KYC, :created_at, :updated_at)
            """

            try:
                conn.execute(text(insert_query), test_user)
                conn.commit()
                print("Success: Test user added to USERS table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test user to USERS table. Error: {e}")

            # Insert test data for STOKVELS table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO STOKVELS (stokvel_id, stokvel_name, ILP_wallet, MOMO_wallet, total_members, min_contributing_amount, max_number_of_contributors, Total_contributions, created_at, updated_at)
                        VALUES ({stokvel_id}, 'Stokvel_{stokvel_id}', 'Stokvel_ILP_Wallet_001', 'Stokvel_MOMO_Wallet_001', 10, 100.0, 20, 1000.0, datetime('now'), datetime('now'));
                        """
                    )
                )
                conn.commit()
                print("Success: Test stokvel added to STOKVELS table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test stokvel to STOKVELS table. Error: {e}")

            # Insert test data for STOKVEL_MEMBERS table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO STOKVEL_MEMBERS (stokvel_id, user_id, created_at, updated_at)
                        VALUES ({stokvel_id}, {user_id}, datetime('now'), datetime('now'));
                        """
                    )
                )
                conn.commit()
                print("Success: Test member added to STOKVEL_MEMBERS table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test member to STOKVEL_MEMBERS table. Error: {e}")

            # Insert test data for TRANSACTIONS table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO TRANSACTIONS (user_id, stokvel_id, amount, tx_type, wallet_type, tx_date, created_at, updated_at)
                        VALUES ({user_id}, {stokvel_id}, 150.0, 'deposit', 'ILP', datetime('now'), datetime('now'), datetime('now'));
                        """
                    )
                )
                conn.commit()
                print("Success: Test transaction added to TRANSACTIONS table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test transaction to TRANSACTIONS table. Error: {e}")

            # Insert test data for RESOURCES table
            try:
                conn.execute(
                    text(
                        """
                        INSERT INTO RESOURCES (name, resource_type, url, created_at, updated_at)
                        VALUES ('Guide to Stokvels', 'PDF', 'https://example.com/guide.pdf', datetime('now'), datetime('now'));
                        """
                    )
                )
                conn.commit()
                print("Success: Test resource added to RESOURCES table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test resource to RESOURCES table. Error: {e}")

            # Insert test data for ADMIN table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO ADMIN (stokvel_id, stokvel_name, user_id, total_contributions, total_members)
                        VALUES ({stokvel_id}, 'Stokvel_{stokvel_id}', {user_id}, 1000.0, 10);
                        """
                    )
                )
                conn.commit()
                print("Success: Test admin added to ADMIN table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test admin to ADMIN table. Error: {e}")

            # Insert test data for CONTRIBUTIONS table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO CONTRIBUTIONS (stokvel_id, user_id, frequency_days, StartDate, EndDate, contribution)
                        VALUES ({stokvel_id}, {user_id}, 30, datetime('now'), datetime('now', '+1 year'), 100.0);
                        """
                    )
                )
                conn.commit()
                print("Success: Test contribution added to CONTRIBUTIONS table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test contribution to CONTRIBUTIONS table. Error: {e}")

            # Insert test data for USER_WALLET table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO USER_WALLET (user_id, user_wallet, UserBalance)
                        VALUES ({user_id}, 'UserWallet001', 500.0);
                        """
                    )
                )
                conn.commit()
                print("Success: Test user wallet added to USER_WALLET table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test user wallet to USER_WALLET table. Error: {e}")

            # Insert test data for STOKVEL_WALLET table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO STOKVEL_WALLET (user_id, user_wallet, UserBalance)
                        VALUES ({user_id}, 'StokvelWallet001', 1000.0);
                        """
                    )
                )
                conn.commit()
                print("Success: Test stokvel wallet added to STOKVEL_WALLET table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test stokvel wallet to STOKVEL_WALLET table. Error: {e}")

            # Insert test data for APPLICATIONS table
            try:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO APPLICATIONS (stokvel_id, user_id, AppStatus, AppDate)
                        VALUES ({stokvel_id}, {user_id}, 'pending', datetime('now'));
                        """
                    )
                )
                conn.commit()
                print("Success: Test application added to APPLICATIONS table.")
            except exc.IntegrityError as e:
                print(f"Failure: Could not add test application to APPLICATIONS table. Error: {e}")

    except Exception as e:
        print(f"An error occurred while inserting test data: {e}")


if __name__ == "__main__":
    create_test_data()