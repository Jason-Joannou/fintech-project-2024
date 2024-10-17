## Update User

The update_user page is designed for users to modify their personal details like name, email, and password. The page consists of a form with multiple input fields that allow users to input new information and submit it for updating their profile. Upon submission, the form sends the data to the backend for validation and processing.

**Data Captured:**

- **Name**: A required field that captures the user's full name, which is typically displayed on their profile and used for identification in the system.
- **Email**: A required field for the user's email address. This must follow a valid email format (e.g., name@example.com). The email is used for communication and account recovery.
- **Password**: A required field for the user's password. It enforces password strength rules to ensure the account is secure. The password may need to meet certain complexity requirements such as minimum length, inclusion of special characters, and numbers.
- **Confirm Password**: A required field that asks the user to re-enter the password for confirmation, ensuring that the user has not made any typing mistakes.

**Why the Update User page is designed so:**
This page is a crucial part of the user profile management system. By allowing users to update their profile details, the system ensures that users can keep their information accurate and up-to-date. The password confirmation feature is designed to enhance security, ensuring that the user has entered their new password correctly without typos. Email validation is key to maintaining the integrity of contact information, as it may be used for authentication or recovery.

**Endpoints in Update User:**
**POST /update_user**: 
  - Upon submission, the form data is sent to the backend, where it is processed by the update_user_info.py file. The backend validates each input field: it checks the format of the email, ensures that the two password fields match, and verifies the overall integrity of the data.
  - If any validation fails, an error message is generated and sent back to the front end, prompting the user to correct the mistakes.
  - Once all fields are validated, the system updates the user's details in the database, confirming the changes.
  - If the process is successful, a success message is displayed to the user. In the event of an error (e.g., invalid email, passwords don't match), the page will display error feedback.

## Update Stokvel

The `update_stokvel` page is designed to allow stokvel administrators to edit the group's information, including the group's name, description, and the list of members. This page is vital for keeping group information accurate and up-to-date as the group grows or changes.

**Data Captured:**

- **Group Name**: The stokvel group's name, a required field that identifies the group.
- **Description**: A text field that allows the administrator to enter or modify the description of the group, outlining its purpose and activities.
- **Member List**: An optional feature that allows the administrator to add or remove members from the group. The system might include a mechanism for searching and selecting members to be added or removed.

**Why the Update Stokvel page is designed so:**
The ability to edit stokvel details is essential for managing the group's dynamic nature. As the group evolves, changes in its purpose, size, and membership may occur, and this page provides a simple way for administrators to manage those changes. The ability to update the member list without needing to recreate the group is particularly useful in stokvels, where membership often fluctuates. This page ensures that stokvel details remain accurate, relevant, and up-to-date.

**Endpoints in Update Stokvel:**
**POST /update_stokvel**:
  - The form data is sent to the backend (handled by `update_stokvel.py`), where it is validated to ensure that all required fields (e.g., group name) are filled out correctly. Optional fields like the description can be left empty or updated as needed.
  - If any data is missing or incorrect, the user is notified with an error message and prompted to fix the issue.
  - Upon successful validation, the group's information is updated in the database, and a success message is displayed. The system may also send notifications to group members about the updates, depending on the design.

## Update User Login

The `update_user_login` page provides users with a secure way to update their login credentials, including username and password. This is a critical feature for maintaining account security and allowing users to make necessary changes, such as when they forget their password or want to change their username.

**Data Captured:**

- **Username**: A required field where the user can input a new or existing username. It must be unique in the system to avoid conflicts with other users.
- **Password**: A required field where the user can input a new password. Password complexity rules might be enforced, such as requiring a minimum number of characters, special characters, and digits.
- **Confirm Password**: A required field to confirm the new password. This prevents errors caused by typing mistakes.

**Why the Update User Login page is designed so:**
The `update_user_login` page is designed to give users full control over their login credentials, which is an important aspect of security and usability. Allowing users to change their username and password ensures that they can secure their accounts if they feel their current credentials have been compromised or if they want a change for personal reasons. The system's design enforces security by requiring password confirmation to avoid accidental changes.

**Endpoints in Update User Login:**
**POST /update_user_login**:
  - Handled by `users.py`, the backend verifies the new credentials before updating them in the system. It checks the username for uniqueness to prevent conflicts.
  - Password validation ensures that it meets security requirements and that both password fields match.
  - If everything is valid, the backend updates the login credentials in the database.
  - If any errors occur, such as a duplicate username or mismatched passwords, appropriate error messages are returned to the user.

## Stokvel Search

The `stokvel_search` page allows users to search for existing stokvel groups by entering a search term or applying filters like group type or location. This page helps users find stokvels that match their interests or geographical preferences.

**Data Captured:**

- **Search Term**: A keyword or group name entered by the user to search for stokvels. This could be a partial or full name of the group.
- **Filters**: Optional fields that allow users to refine their search by location, type of stokvel, or other categories.

**Why the Stokvel Search page is designed so:**
This page makes it easier for users to discover stokvels that align with their interests. By providing search functionality with filtering options, the system caters to users who are looking for groups within specific geographical areas or who have particular preferences. This feature improves user engagement by offering a straightforward way to explore and join new groups.

**Endpoints in Stokvel Search:**
**GET /stokvel_search**:

  - The search term and filters are processed by the backend (`stokvel.py`), which queries the database for matching stokvels.
  - The system returns a list of stokvels that match the search criteria. If no matches are found, a message is displayed to the user, indicating that no relevant groups were found.
  - The page may also offer options to further refine the search or provide suggestions for similar groups.

## Onboarding Template

The `onboarding_template` page serves as a guide for new users to help them sign up and set up their accounts. It collects basic information like name, email, and password and may offer additional options to customize the user experience.

**Data Captured:**

- **Full Name**: A required field to capture the user's full name, which will be used to personalize the account and communication.
- **Email Address**: A required field to capture the user's email, which must follow a valid email format. The email is used for communication and account management.
- **Password**: A required field for account security. Password complexity rules may be enforced to ensure strong security.
- **Preference Settings**: Optional fields that allow the user to customize their experience (e.g., notification settings, group suggestions).

**Why the Onboarding Template page is designed so:**
Onboarding is critical for user retention and ensuring a smooth first experience. By guiding new users through account setup, the page ensures that users can easily get started with the system. It simplifies the sign-up process while capturing essential information needed for creating an account. The optional customization settings enhance the user experience by tailoring the platform to the user's preferences right from the start.

**Endpoints in Onboarding Template:**
**POST /onboarding**:

  - The form data is sent to the backend (`onboarding.py`), where it is validated for accuracy and completeness.
  - The backend checks for duplicate emails and verifies that the password meets the security requirements.
  - If the validation is successful, the user's account is created in the database, and they are logged into the system.
  - If there are any issues, such as a duplicate email or password weakness, appropriate error messages are displayed to guide the user in fixing the problem.

## Stokvel Creation Template

The `stokvel_creation_template` page allows users to create a new stokvel group by providing basic details such as the group's name, its purpose, and the initial list of members. The page is designed to streamline the process of starting a stokvel.

**Data Captured:**

- **Group Name**: A required field that captures the name of the new stokvel group.
- **Purpose**: A description field that outlines the purpose or goal of the group. This helps new members understand what the group is about.
- **Initial Members**: A list of people to be invited or added as founding members of the stokvel.

**Why the Stokvel Creation Template page is designed so:**
This page is designed to encourage users to create new stokvels by providing a simple and straightforward process. Group creation needs to be intuitive to lower the barrier for entry, and the page achieves this by minimizing the number of required fields while still capturing essential details. The ability to invite or add initial members during creation also fosters early group collaboration.

**Endpoints in Stokvel Creation Template:**
**POST /create_stokvel**:

  - The form data is processed by `create_stokvel.py`, where the backend validates the group name to ensure uniqueness.
  - The backend also ensures that required fields (e.g., group name and purpose) are filled out correctly.
  - If the validation is successful, the new stokvel is created in the database, and the initial members are notified of their inclusion.
  - If there are any issues, such as a duplicate group name, an error message is returned to the user for correction.

## Joining Template

The `joining_template` page allows users to submit a request to join an existing stokvel. The page collects the user's basic information and, optionally, a message explaining why they want to join the group.

**Data Captured:**

- **User Information**: The user's name and email address.
- **Reason for Joining**: An optional field where the user can explain their motivation for joining the group. This is particularly useful for stokvels that have specific membership criteria.

**Why the Joining Template page is designed so:**
This page formalizes the process of joining a stokvel, ensuring that administrators receive all the necessary information to make informed decisions about membership. The optional reason-for-joining field helps administrators understand the user's motivations and decide whether they are a good fit for the group.

**Endpoints in Joining Template:**
**POST /join_stokvel**:

  - The form data is processed by `join_stokvel.py`, which submits the user's request to the stokvel administrator.
  - The system checks for potential issues (e.g., duplicate requests) before submitting the application.
  - Upon successful submission, the user is notified that their request has been sent. The stokvel admin will then review the application and decide whether to accept or reject it.

## Approve Applications

The `approve_applications` page is designed for stokvel administrators to manage membership requests. Administrators can view pending applications and either approve or reject them based on the details provided by the applicants.

**Data Captured:**
- **Pending Applications**: A list of pending membership requests is displayed, including each applicant's name, email, and reason for joining (if provided).

**Why the Approve Applications page is designed so:**
This page is essential for stokvel management. It provides a simple and intuitive interface for administrators to view and manage applications, ensuring that the group's membership is carefully controlled. By reviewing the reasons for joining, administrators can maintain the integrity of the group and ensure that new members align with the group's purpose.

**Endpoints in Approve Applications:**
**POST /approve_application**:

  - The administrator's decision (approve or reject) is sent to `approve_applications.py`, where the backend updates the status of the application in the database.
  - If the application is approved, the user is notified and added to the group. If rejected, the user is informed of the decision.
  - The page may also allow administrators to leave a note explaining their decision, particularly if the application is rejected.

## Approval Login

The `approval_login` page ensures that only authorized administrators can access the approve/reject functionality. It requires administrators to log in with their credentials before they can manage membership applications.

**Data Captured:**
- **Username**: The admin's login username.
- **Password**: The password used to authenticate the admin.

**Why the Approval Login page is designed so:**
This page enhances security by requiring administrators to authenticate before making changes to the group's membership. Ensuring that only authorized users can approve or reject applications helps protect the group from unauthorized access and ensures that membership decisions are legitimate.

**Endpoints in Approval Login:**
**POST /approval_login**:

  - The form data is processed by `approval_login.py`, where the backend verifies the admin's credentials.
  - If the credentials are correct, the admin is granted access to the membership management page.
  - If the login attempt fails, an error message is displayed, and the admin is prompted to retry.

## Action Success Template

The `action_success_template` page is a generic confirmation page that informs users that their requested action has been successfully completed. It is commonly used after form submissions or updates, providing a clear indication that the user's request was processed without errors.

**Data Captured:**
- No specific data is captured on this page. It simply displays a success message.

**Why the Action Success Template page is designed so:**
Feedback is crucial for user experience. After completing an action (e.g., submitting a form or updating a profile), users need to know that their request was successful. The `action_success_template` provides this confirmation, ensuring that users are aware that their action was processed as expected.

**Endpoints in Action Success Template:**
**GET /action_success**:

  - This endpoint displays the success message after a user completes a specific action, such as submitting a form or making an update. It is designed to provide positive feedback and closure to the user's interaction.

## Action Failed Template

The `action_failed_template` page notifies users that an action they attempted has failed, usually due to a validation error or system issue. This page is designed to help users understand what went wrong and how they can correct it.

**Data Captured:**

- No specific data is captured on this page. It simply displays an error message with guidance on how to resolve the issue.

**Why the Action Failed Template page is designed so:**

- When something goes wrong, users need clear feedback to understand the problem and how to fix it. The `action_failed_template` page provides this feedback, helping users correct errors and retry their actions. It improves user experience by providing clear guidance on next steps.

**Endpoints in Action Failed Template:**
**GET /action_failed**:

  - This endpoint displays an error message when the user's action fails. It could be triggered by form validation failures, incorrect login attempts, or issues processing a request. The page offers guidance on how the user can resolve the issue or retry the action.
