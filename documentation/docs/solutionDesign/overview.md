# Project Overview

A stokvel is a traditional savings scheme practiced in South Africa, where a group of people agree to contribute a fixed amount of money to a common pool on a regular basis. This pool is then used for a common objective, such as savings, investments, or purchasing goods. The stokvel sector in South Africa is substantial, with over 810,000 active stokvels comprising 11 million members and managing around R50 billion annually.

The primary objective of this project is to design and develop a platform that digitizes stokvels using the Interledger Protocol (ILP) Open Payments standard. The platform aims to enhance financial inclusion by being accessible through a low-tech interface, specifically a WhatsApp chatbot. This approach ensures that even users with basic mobile phones can participate in the digital economy.

## Specific Goals

1. **Accessibility**: The platform will be accessible via a WhatsApp chatbot interface, making it user-friendly for individuals in emerging markets.
2. **Interoperability**: Implement the ILP Open Payments API to facilitate seamless transactions across different financial systems.
3. **Modular Architecture**: Design a modular system that can be easily extended and maintained.
4. **Integration**: Integrate with existing mobile money solutions, such as the Rafiki Money wallet and MTN MoMo, to leverage existing financial infrastructure.
5. **Flexible Contributions**: Allow stokvel participants to contribute varying amounts, which will be applied during the distribution of the stokvel benefits.
6. **Regulatory Compliance**: Ensure that the platform adheres to relevant regulatory requirements and includes a go-to-market strategy to drive adoption.

## Deliverables

The project will deliver the following:

- **Project Specification Document**: Detailed requirements and user stories.
- **Technical Specification Document**: UI mockups, proposed implementation, technology justification, and architecture diagrams.
- **Proof of Concept**: Including a GitHub repository and a deployed version of the platform.
- **Lessons Learnt Document**: Individual reflections on the project.
- **Final Presentation and Product Demo**: To be presented to a wide audience, including the Financial Innovation Hub and the ILF team.

## Team Structure

The project team will be divided into three core groups:

1. **Product Team**: Responsible for research and documentation.
2. **Development Team 1**: Focused on backend development.
3. **Development Team 2**: Focused on frontend development.

Additionally, a management team comprising a CEO, COO, and CTO will be elected from the core teams to oversee the project's progress.

## Timeline

The project will follow a structured timeline, starting with initial research and project specification in the first two weeks, followed by product development over the next five weeks. Key milestones include internal and external project check-ins, proof of concept demos, and the final presentation.

---

# Project Requirements

This section outlines the functional and non-functional requirements of the project, providing a detailed description of what the system should do and the constraints under which it must operate.

## Functional Requirements

### User Authentication and Authorization

- **Registration**: Users must be able to register using their mobile numbers. Users will be recognized as system members or new joiners based on the cell phone number used to interact with the system. The registration process for new joiners should include verification via an OTP (One-Time Password) sent to the user's mobile number.
- **Login**: Users should log in using their registered mobile number and a password. Implement a "Forgot Password" feature to allow users to reset their password via OTP.
- **Role-Based Access Control**: The system should support different user roles. Each role will have specific permissions. These roles include:
  - **New joiners**: Register by adding customer details like username, surname, and wallet address from which they will make payments to the stokvel.
  - **Users**: Join existing stokvels, create new stokvels, view and manage profile details.
  - **Stokvel admins**: Edit stokvels, approve applications from users to join a stokvel.

### Stokvel Management

- **Create Stokvel Group**: Admin users should be able to create new stokvel groups by specifying group details such as name, description, contribution amount, frequency (weekly, monthly), and payout schedule.
- **Join Stokvel Group**: Users should be able to search for and join existing stokvel groups. Admins can approve or reject membership requests.
- **Manage Group**: Admins should manage group settings, including contribution amounts, payout schedules, and member removal.
- **Contribution Scheduling**: The system should allow for the scheduling of contributions, sending reminders to members before the due date.

### Payment Processing

- **Integration with Mobile Money Services**: The platform should integrate with mobile money services like MTN MoMo to facilitate contributions and payouts. This includes API integration for seamless transactions.
- **Multiple Payment Methods**: Support for bank transfers, mobile money, and possibly cryptocurrency.
- **Automated Transactions**: Automate contributions collection and payout distribution according to the stokvel's schedule.
- **Flexible Payments**: Allow users to specify contribution amounts, subject to the minimum contribution amount set by the stokvel admin.
- **Payouts**: Payouts to stokvel members should be proportional to the contributions made, with interest distributed accordingly.

### Transaction History

- **User Transaction History**: Users should be able to view their individual transaction history, including contributions and payouts.
- **Group Transaction Reports**: Admins should have access to financial reports for each stokvel group.
- **Export Functionality**: Allow users to export transaction history and reports in CSV or PDF format.

### Notifications

- **Contribution Reminders**: Send automated reminders via WhatsApp for upcoming contributions.
- **Transaction Alerts**: Notify users of successful contributions, payouts, or failed transactions.
- **General Notifications**: Inform users about important updates, such as changes in group settings.

### Customer Support

- **Support Chatbot**: Provide a WhatsApp chatbot to handle common queries.
- **Human Support Escalation**: Allow users to escalate issues to human agents if the chatbot cannot resolve their queries.

---

## Non-Functional Requirements

### Scalability

- **Horizontal Scaling**: Support horizontal scaling to handle increasing users and transactions.
- **Load Balancing**: Implement load balancing to ensure consistent performance.

### Security

- **Data Encryption**: Encrypt sensitive data in transit and at rest.
- **Authentication**: Implement multi-factor authentication (MFA).
- **Audit Logs**: Maintain audit logs of all transactions and activities for monitoring and compliance.

### Usability

- **User Interface**: Design an intuitive WhatsApp chatbot interface.
- **Accessibility**: Ensure the platform is usable by users with basic mobile phones.

### Reliability

- **High Availability**: Design the system for minimal downtime and failover mechanisms.
- **Data Backup**: Regular data backups to prevent loss in case of failures.

### Compliance

- **Regulatory Compliance**: Ensure the platform complies with financial regulations (e.g., KYC, AML).
- **Data Protection**: Adhere to data protection laws like POPIA in South Africa.

### Performance

- **Response Time**: Aim for sub-second response times for user interactions and transactions.
- **Throughput**: Ensure the system handles a high volume of transactions smoothly.

### Maintainability

- **Modular Architecture**: Implement a modular system for easy maintenance and updates.
- **Documentation**: Provide comprehensive documentation for the codebase, APIs, and architecture.

---

## Assumptions and Constraints

- **Target Market**: Primarily targeting users in South Africa, with potential for expansion.
- **User Devices**: Users will have basic mobile phones with WhatsApp.
- **Budget and Timeline**: The project will adhere to a fixed budget and timeline.

## Dependencies

- **Third-Party Integrations**: Successful integration with mobile money services and the ILP Open Payments API.
- **Regulatory Approvals**: Necessary approvals for legal operation.
- **Technology Stack**: Availability and stability of the chosen tech stack, including cloud services and databases.
