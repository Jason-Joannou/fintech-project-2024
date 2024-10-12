## Database Architecture

The database design is centered around two primary tables:

- The Coins table
- The Users table

The Coins table stores essential information about various cryptocurrencies, including their names, symbols, and historical data. The Users table manages user authentication and stores sign-in credentials, ensuring secure access to the application. This design enables efficient data management and supports the core functionalities of the crypto financial dashboard.

The image below shows the structure of the two tables that are used in the project architecture.

![database design](./images/db_design.png)

## Backend Architecture

The API serves as the bridge between the frontend and the database, built using FastAPI, a modern web framework for creating APIs with Python. It manages data processing, business logic, and database interactions, offering endpoints for data retrieval, updates, and analytical operations. The API is containerized and deployed on Azure Container Instances, facilitating easy scaling and management.