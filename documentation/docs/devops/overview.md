## DevOps Overview

The DevOps strategy for **DigiStokvel** focuses on delivering a seamless, automated development and deployment process. By leveraging agile methodologies, containerization, and infrastructure as code (IaC) tools, the project ensures that each component is scalable, secure, and consistently deployed across environments. This overview highlights how the team has incorporated modern DevOps practices to enhance collaboration, increase deployment speed, and maintain system reliability.

### Key Components of the DevOps Pipeline

#### **Agile Workflow**

DigiStokvel follows an **Agile development methodology**, with work organized into iterative **sprints**. This methodology allows the team to release features incrementally, ensuring continuous delivery and the flexibility to adapt to changes quickly.

- **Sprint Planning**: At the beginning of each sprint, goals are defined based on the product backlog. Tasks are estimated and assigned to team members for execution.
- **Sprint Execution**: Daily standups facilitate communication and ensure alignment. Tasks are updated in **Azure Boards**, providing real-time visibility of progress.
- **Sprint Review and Retrospective**: The team reviews deliverables with stakeholders, gathers feedback, and reflects on ways to improve future sprints. The agile workflow improves flexibility and responsiveness to feedback, allowing for continuous integration of new features.

For more details on the sprint workflow, visit the [Agile Workflow](./agile.md) page.

#### **Version Control and Collaboration**

- All code is managed using **Git** with repositories hosted on **GitHub**. GitHub facilitates version control, code review, and team collaboration, ensuring all changes are tracked efficiently.
- **Branching Strategy**: A feature-branch workflow is adopted, where each new feature or bug fix is developed in an isolated branch. After passing code reviews and automated testing, changes are merged into the main branch.
- The [Git Workflow](./git.md) details the full branching strategy for DigiStokvel.

#### **Continuous Integration (CI)**

- **GitHub Actions** is used for continuous integration, triggering automated builds and tests on each code commit. This process ensures the codebase remains stable, with immediate feedback provided on code quality.
- The CI pipeline integrates unit tests, integration tests, and linting, which run automatically to verify that new changes do not introduce regressions.

#### **Containerization with Docker**

DigiStokvel uses **Docker** to containerize the application components, ensuring consistent behavior across development, staging, and production environments.

- **API Containerization**: The API is encapsulated in a Docker container, isolating dependencies and providing an easily replicable deployment setup.
- The Docker workflow also simplifies environment management, reducing the time required to replicate environments for development or testing.

Refer to the [Docker Overview](./docker.md) for details on how the DigiStokvel API is containerized.

#### **Infrastructure as Code with Terraform**

DigiStokvel’s infrastructure is defined using **Terraform**, an infrastructure-as-code tool that automates the provisioning and management of cloud resources.

- **Azure Deployment**: Terraform is used to provision and manage resources such as **Azure Container Instances (ACI)** and **Azure Container Registry (ACR)**, ensuring scalability and consistency across deployments.
- **Infrastructure Automation**: By defining infrastructure in code, Terraform enables automatic scaling and disaster recovery, as well as easy replication of environments.

For detailed infrastructure definitions, see the [Terraform Overview](./terraform.md).

#### **Deployment Workflow**

- **Azure Cloud**: DigiStokvel is deployed on **Azure**, utilizing **ACI** for containerized workloads and **ACR** for managing Docker images. This setup provides a robust, scalable environment for running the application.
- **Automated Deployment**: The deployment pipeline automates the process from building Docker images to pushing them to ACR and deploying to ACI.

### Documentation and Collaboration

- **MkDocs** is used to generate and maintain project documentation. The documentation is continuously updated as new features are developed, ensuring transparency and easy access to project information.
- The **Material** theme for MkDocs provides a clean and intuitive interface for browsing documentation, and links to API documentation generated by **Swagger UI** ensure that the project is well-documented for both developers and stakeholders.