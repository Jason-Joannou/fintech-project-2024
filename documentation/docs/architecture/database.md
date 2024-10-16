## Database Design

### Introduction

This project utilizes a SQLite database to build and manage data storage, focusing on scalability and flexibility. The design ensures efficient data handling for stokvel members, transactions, contributions, and payouts.

### Design Overview

While foreign key relationships were defined between various tables to maintain logical data structures, these relationships are not currently enforced by SQLite. This is a limitation of the existing design, and future updates will aim to implement foreign key enforcement to ensure referential integrity across the system.

### Foreign Key Relationships

Although foreign key relationships were set up in the table design, they are not enforced at the database level. Enforcing these relationships in future iterations will be essential to prevent orphaned records and to maintain the integrity of relationships between entities (e.g., **USERS**, **STOKVELS**, **TRANSACTIONS**). This step will enhance the data reliability as the system continues to develop.

### Tables and Relationships

#### STOKVEL_MEMBERS Table

**Purpose:** Stores information about users who are members of specific stokvels.

**Key Fields:**

- `stokvel_id`: Foreign key referencing the **STOKVELS** table, linking stokvels to their members.
- `user_id`: Foreign key referencing the **USERS** table, associating users with the stokvels they belong to.
- `contribution_amount`: Amount contributed by the user on a recurring basis.
- **Unique Constraint:** Ensures that each combination of `stokvel_id` and `user_id` is unique, preventing duplicate memberships.

#### STOKVELS Table

**Purpose:** Stores details about each stokvel, which are used to create the stokvel constitution.

**Key Fields:**

- `stokvel_id`: Primary key that uniquely identifies each stokvel.
- `stokvel_name`: Name of the stokvel.
- `ILP_wallet`, `MOMO_wallet`: Wallet information for transactions.
- `total_contributions`: Sum of all contributions to the stokvel.
- `payout_frequency_int`, `payout_frequency_period`: Defines payout frequency.
- `start_date`, `end_date`: Period marking the stokvel’s activity duration.

#### USERS Table

**Purpose:** Stores user-specific information.

**Key Fields:**

- `user_id`: Primary key that uniquely identifies each user.
- `user_number`: The user's cell phone number, used for interactions on our WhatsApp channel.
- `user_name`, `user_surname`: Basic user details.
- `ILP_wallet`, `MOMO_wallet`: Wallet details for both ILP and Momo wallets.
- `verified_KYC`: Indicates if the user has completed KYC verification.

#### TRANSACTIONS Table

**Purpose:** Records all transactions by users, including contributions to and payouts from stokvels.

**Key Fields:**

- `user_id`: Foreign key referencing the **USERS** table.
- `stokvel_id`: Foreign key referencing the **STOKVELS** table.
- `amount`: Transaction amount.
- `tx_type`: Type of transaction (e.g., DEPOSIT, PAYOUT).
- `tx_date`: Date of the transaction.

#### RESOURCES Table

**Purpose:** Stores links or resources related to the system.

**Key Fields:**

- `name`: Name of the resource.
- `resource_type`: Type of the resource (e.g., document, link).
- `url`: URL location of the resource.

#### ADMIN Table

**Purpose:** Contains information about stokvel administrators, who have specific rights unavailable to regular members.

**Key Fields:**

- `stokvel_id`: Foreign key referencing the **STOKVELS** table.
- `user_id`: Foreign key referencing the **USERS** table.
- `total_contributions`: Total contributions managed by the admin.
- **Unique Constraint:** Ensures each `stokvel_id` and `user_id` pairing is unique.

#### CONTRIBUTIONS Table

**Purpose:** Manages the contribution process for specific stokvels.

**Key Fields:**

- `stokvel_id`: Foreign key referencing the **STOKVELS** table.
- `frequency_days`: Contribution frequency (in days).
- `StartDate`, `NextDate`, `PreviousDate`, `EndDate`: Tracks the contribution schedule.

#### PAYOUTS Table

**Purpose:** Manages the payout process for specific stokvels.

**Key Fields:**

- `stokvel_id`: Foreign key referencing the **STOKVELS** table.
- `frequency_days`: Payout frequency (in days).
- `StartDate`, `NextDate`, `PreviousDate`, `EndDate`: Payout schedule.

#### USER_WALLET Table

**Purpose:** Stores user wallet information.

**Key Fields:**

- `user_wallet`: Wallet details for the user.
- `UserBalance`: Current balance in the user's wallet.

#### STOKVEL_WALLET Table

**Purpose:** Stores wallet information for stokvels.

**Key Fields:**

- `user_id`: Foreign key referencing the **USERS** table.
- `UserBalance`: Balance in the stokvel's wallet.

#### APPLICATIONS Table

**Purpose:** Tracks user applications to join stokvels.

**Key Fields:**

- `stokvel_id`: Foreign key referencing the **STOKVELS** table.
- `user_id`: Foreign key referencing the **USERS** table.
- `AppStatus`: Status of the application (e.g., pending, approved).
- `AppDate`: Application submission date.

#### STATE_MANAGEMENT Table

**Purpose:** Manages interaction states on the WhatsApp channel, allowing users to navigate between different messaging states.

**Key Fields:**

- `user_number`: Unique user number.
- `last_interaction`: Timestamp of the last interaction.
- `current_stokvel`: The current stokvel the user is engaged with.

#### INTEREST Table

**Purpose:** Tracks interest rates earned by stokvels, used to calculate monthly payouts to members.

**Key Fields:**

- `stokvel_id`: Foreign key referencing the **STOKVELS** table.
- `interest_value`: Interest rate.
- `date`: Date when the interest was recorded.
