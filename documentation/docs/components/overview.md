## Components Overview

The DigiStokvel project is built using a modular architecture, leveraging various components to handle specific functions such as database management, backend frameworks, and automated financial operations. This overview provides a detailed look at the core components that form the foundation of the DigiStokvel system.

### Database

The DigiStokvel system uses **SQLite** for its database, which stores and manages key data related to stokvels, users, transactions, and contributions. Although foreign key relationships have been defined between tables, they are not enforced by SQLite in the current design. Future iterations will enhance data integrity by enforcing these relationships.

- **Key Features**:
  - Storage for users, stokvels, transactions, and payouts.
  - Efficient handling of stokvel member data, contributions, and financial operations.
  - Future-proof design for scalability and referential integrity.

For a more detailed description of the database design, including table structures and relationships, refer to the [Database Overview](./database.md).


### Express

**Express** is used as the core framework for DigiStokvel’s backend services, specifically for handling communication with the **Interledger Protocol (ILP)**. Express is lightweight yet powerful, enabling the system to manage grants, incoming and outgoing payments, and quotes generation with the ILP Open Payments API.

- **Core Features**:
  - RESTful API services to interact with payment systems.
  - Integration with ILP for managing grants and secure payment transactions.
  - Asynchronous processing to handle multiple user requests efficiently.

For more information on how Express is used in the DigiStokvel project, visit the [Express Overview](./express.md).



### Flask Templates

The **Flask** framework is utilized to build web-based user interfaces that complement WhatsApp-based interactions. While WhatsApp is the primary communication channel for simple text commands, more complex tasks like form submissions and detailed user inputs are handled using Flask templates.

- **Key Use Cases**:
  - Complex forms for user onboarding, stokvel creation, and membership management.
  - Secure handling of sensitive information, such as user credentials and stokvel settings.
  - Enhanced user experience through rich visual feedback and structured forms.

To learn more about why Flask templates are integrated into the system, refer to the [Flask Template Overview](./flask_templates.md).


### Flask Backend

The **Flask** backend serves as the backbone of the DigiStokvel system, handling core operations such as user registration, stokvel management, and integration with payment services like **MTN MoMo** and **WhatsApp**.

- **Key Features**:
  - User authentication and management.
  - Stokvel creation, contribution tracking, and payouts.
  - Automated financial operations integrated with WhatsApp chatbot for user convenience.

For further details about the endpoints and features provided by the Flask backend, see the [Flask Overview](./flask.md).

### Function Apps

**Function apps** automate the core financial operations within the DigiStokvel system, specifically for handling scheduled contributions and payouts. These apps run daily, ensuring that all financial activities are processed without manual intervention.

- **Payouts Engine**: Automatically handles the disbursement of funds to stokvel members based on the predefined payout schedules.
- **Contributions Engine**: Automates the collection of recurring contributions from stokvel members, ensuring the financial stability of the group.

The function apps are critical for ensuring the efficiency and reliability of DigiStokvel's automated financial workflows. To explore how these apps work, visit the [Function Apps Overview](./function_app.md).

