## Database Design

### Introduction

In this project, we used a SQLite implementation to build and manage our database. The design focused on scalability and flexibility, ensuring efficient data handling for stokvel members, transactions, contributions, and payouts.

### Design Overview

While foreign key relationships were created between various tables to maintain logical data structures and relationships, we did not enforce these relationships in SQLite. This represents a shortfall in our current design, and adding foreign key enforcement will be considered as future work to ensure referential integrity within the system.

### Foreign Key Relationships
Although foreign key relationships were established in the table design, they were not enforced at the database level. In future iterations of this project, implementing foreign key enforcement will be critical to prevent orphaned records and ensure that relationships between entities (such as USERS, STOKVELS, and TRANSACTIONS) are properly maintained. This will enhance the integrity and reliability of the data as the system evolves.

### Tables and Relationships

The  various tables used in our design, the purpose of each table and the key fields of each table is detailed below 

1. STOKVEL_MEMBERS Table

#### Purpose

Stores information about users who are members of specific stokvels.

### Key Fields
stokvel_id: Foreign key referencing the STOKVELS table, to link the relationship between stokvels and stokvel members.
user_id: Foreign key referencing the USERS table to link users with the stokvels they are part of.
contribution_amount: Amount the user contributes on a recurring basis. 
Unique Constraint: Ensures each combination of stokvel_id and user_id is unique, preventing duplicate memberships.

2. STOKVELS Table

#### Purpose 

Stores details about each stokvel. The details in this stokvel is used to create the stokvel constitution.

### Key Fields

stokvel_id: Primary key that uniquely identifies each stokvel.
stokvel_name: Name of the stokvel.
ILP_wallet, MOMO_wallet: Wallet information for transactions.
total_contributions: Total contributions made to the stokvel.
payout_frequency_int, payout_frequency_period: Frequency of payouts.
start_date, end_date: Dates marking the stokvel's active period.

3. USERS Table

#### Purpose 

Stores user-specific information.

#### Key Fields

user_id: Primary key that uniquely identifies each user.
user_number: The cell phone number of the user which will be used for interactions on our WhatsApp channel.
user_name, user_surname: Basic user details.
ILP_wallet, MOMO_wallet: Wallet details for the user. This caters for both a ILP and Momo wallet for future applications.
verified_KYC: Flag indicating if the user has KYC verification.

4. TRANSACTIONS Table

#### Purpose 

Records all transactions made by users. Which include contributions to a stokvel and payouts from a stokvel.

This table is used to determine the size of the payout each user should receive from a given stokvel. 

#### Key Fields

user_id: Foreign key referencing the USERS table.
stokvel_id: Foreign key referencing the STOKVELS table.
amount: Transaction amount.
tx_type: Type of transaction (e.g., DEPOSIT, PAYOUT).
tx_date: Date of the transaction.

5. RESOURCES Table

#### Purpose 

Stores links or resources related to the system.

#### Key Fields

name: Name of the resource.
resource_type: Type of the resource (e.g., document, link).
url: URL where the resource is located.

6. ADMIN Table

#### Purpose 

Holds data about stokvel administrators. Stokvel administrators have certain rights that normal stokvel members won't have. 

#### Key Fields

stokvel_id: Foreign key referencing the STOKVELS table.
user_id: Foreign key referencing the USERS table.
total_contributions: Total contributions handled by the admin.
Unique Constraint: Each combination of stokvel_id and user_id must be unique.

7. CONTRIBUTIONS Table

#### Purpose 

Tracks if the contributions process should be kicked off for a specific stokvel. 

#### Key Fields
stokvel_id: Foreign key referencing the STOKVELS table.
frequency_days: Frequency of contributions (in days).
StartDate, NextDate, PreviousDate, EndDate: Track the contribution schedule.

8. PAYOUTS Table

#### Purpose 

Tracks if the payout process should be kicked off for a specific stokvel. 

#### Key Fields

stokvel_id: Foreign key referencing the STOKVELS table.
frequency_days: Frequency of payouts (in days).
StartDate, NextDate, PreviousDate, EndDate: Payout schedule.

9. USER_WALLET Table

#### Purpose 

Stores wallet information for users.

#### Key Fields

user_wallet: Wallet details for the user.
UserBalance: Current balance in the user's wallet.

10. STOKVEL_WALLET Table

#### Purpose 

Stores wallet information for stokvels.

#### Key Fields

user_id: Foreign key referencing the USERS table.
UserBalance: Balance in the stokvel’s wallet.

11. APPLICATIONS Table

#### Purpose 

Tracks applications made by users to join stokvels.

#### Key Fields

stokvel_id: Foreign key referencing the STOKVELS table.
user_id: Foreign key referencing the USERS table.
AppStatus: Status of the application (e.g., pending, approved).
AppDate: Date of the application.

12. STATE_MANAGEMENT Table

#### Purpose 

Manages interaction states on the WhatsApp Channel to enable usets to move between different messaging states.

#### Key Fields

user_number: User's unique number.
last_interaction: Timestamp of the last interaction.
current_stokvel: Current stokvel the user is engaged with.

13. INTEREST Table

#### Purpose 

Tracks the interest rates earned by stokvels across various months. This table will be used to calculate the interest earned by each stokvel in a given month when the payout amount to each stokvel member is calculated

#### Key Fields

stokvel_id: Foreign key referencing the STOKVELS table.
interest_value: The value of the interest.
date: Date the interest was recorded.