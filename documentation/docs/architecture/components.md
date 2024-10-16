## Database Architecture

The database design is centered around two primary tables:

- The Coins table
- The Users table

The Coins table stores essential information about various cryptocurrencies, including their names, symbols, and historical data. The Users table manages user authentication and stores sign-in credentials, ensuring secure access to the application. This design enables efficient data management and supports the core functionalities of the crypto financial dashboard.

The image below shows the structure of the two tables that are used in the project architecture.

![database design](./images/db_design.png)

## Backend Architecture

The API serves as the bridge between the frontend and the database, built using FastAPI, a modern web framework for creating APIs with Python. It manages data processing, business logic, and database interactions, offering endpoints for data retrieval, updates, and analytical operations. The API is containerized and deployed on Azure Container Instances, facilitating easy scaling and management.

## Quality of Life Queries

The quality-of-life queries gives end-user and admin a view on their account details, deposits and payouts. Also included are changes that can be made in terms of naming as well as stokvel constitution updates.

**Data Captured:**
- **User Number**: The user or admin’s WhatsApp number.
- **User Input**: User or admin send input via WhatsApp message.
- **Stokvel Selection**: The users or admin’s stokvel selection

**Endpoints included in Quality of Life Queries:**

**POST /stokvel/stokvel_summary**:
  - The endpoint is hosted in `stokvels.py`, where it requests the stokvel selection and user number from the state manager.
  - If successful it returns the message stating the stokvel name, the total deposits in the stokvel, users deposits into specific stokvel, users payout from stokvel and number of active users in stokvel.
  - Error message will only be displayed if there is an error value in the database as the stokvel selection would have been verified by this step in the state manager.

**POST /stokvel/view_constitution**:
  - The endpoint is hosted in `stokvels.py`, where it requests the stokvel selection from the state manager.
  - If successful it returns the message stating the stokvel name, the minimum contributing amount, maximum number of contributors and the creation of the stokvel.
  - Error message will only be displayed if there is an error value in the database as the stokvel selection would have been verified by this step in the state manager.

**POST /admin/change_stokvel_name**:
  - The endpoint is hosted in `stokvels.py`, where it requests the stokvel selection, user number from the state manager and prompts the user to enter an input.
  - Once user has been submitted, a message will be returned stating that the change of name has been successful and new name will be stated.
  - Error message will appear if no user input is inserted.

**POST /stokvel/admin/change_member_number**:
  - The endpoint is hosted in `stokvels.py`, where it requests the stokvel selection, user number from the state manager and prompts the user to enter an input.
  - Once user has been submitted, a message will be returned stating that the change of maximum number of contributors has been successful and new name will be stated.
  - Error message will appear should the end user not insert a numeric value.

**POST /view_account_details**:
  - The endpoint is hosted in `users.py`, where it requests the stokvel selection and phone number from the state manager.
  - If successful it returns the message stating the user name and surname, user ID, their wallet ID, their total contributions and their total payouts.
  - Error message will only be displayed if there is an error value in the database as the phone number would have been verified by this step in the state manager.

**POST /admin/update_username**:
  - The endpoint is hosted in `users.py`, where it requests the user number from the state manager and prompts the user to enter an input.
  - Once user has been submitted, a message will be returned stating that the change of name has been successful and new name will be stated.
  - Error message will appear if no user input is inserted.

**POST /admin/update_usersurname**:
  - The endpoint is hosted in `users.py`, where it requests the user number from the state manager and prompts the user to enter an input.
  - Once user has been submitted, a message will be returned stating that the change of surname has been successful and new name will be stated.
  - Error message will appear if no user input is inserted.
