## Terraform Overview

Terraform is an open-source Infrastructure as Code (IaC) tool that allows you to define and provision data center infrastructure using a high-level configuration language. With Terraform, you can manage resources across various cloud providers, such as Azure, AWS, and Google Cloud, in a consistent and repeatable manner.

In our project, we have used Terraform to define and manage our infrastructure on Azure. This approach enables us to automate the deployment and management of resources, ensuring that our infrastructure is consistent, scalable, and easily reproducible.

For example, below is the Terraform configuration file that outlines our API infrastructure setup:


```hcl
# IaC main file

# Define provider
provider "azurerm" {
  features {

  }
  subscription_id = "secret"

}

# Define resource group
resource "azurerm_resource_group" "masters_uct" {
  name     = "Masters-UCT"
  location = "UK South"
}

# Define our container registry
resource "azurerm_container_registry" "acr" {
  name                = "mastersuctacrv1"
  resource_group_name = azurerm_resource_group.masters_uct.name
  location            = azurerm_resource_group.masters_uct.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_group" "aci_flask_api" {
  name                = "flask-api"
  resource_group_name = azurerm_resource_group.masters_uct.name
  location            = azurerm_resource_group.masters_uct.location
  os_type             = "Linux"

  container {
    name   = "flask-api-container"
    image  = "${azurerm_container_registry.acr.login_server}/stokvel_flask_api:v1.0.2"
    cpu    = "1"
    memory = "1.5"

    environment_variables = {
      TWILIO_ACCOUNT_SID  = "secret"
      TWILIO_AUTH_TOKEN   = "secret"
      TWILIO_PHONE_NUMBER = "secret"
    }

    ports {
      port     = 80
      protocol = "TCP"
    }

  }

  ip_address_type = "Public"
  dns_name_label  = "stokveldigital" # Ensure this is a unique DNS name
  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }


}

output "container_registry_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "flask_api_fqdn" {
  value = azurerm_container_group.aci_flask_api.fqdn
}
```

This Terraform configuration begins by specifying the Azure provider, ensuring that our deployment targets the correct cloud environment.

1. **Resource Group**:
    - We define a resource group named `Masters-UCT`, located in the `UK South` region. This resource group acts as an organizational container for all our related resources.

2. **Azure Container Registry (ACR)**:
    - Within this resource group, we create an Azure Container Registry (ACR) named `mastersuctacr`. This ACR allows us to store and manage Docker container images, with the admin feature enabled for easier access.

3. **Azure Container Instance (ACI)**:
    - To deploy our public API, we utilize an Azure Container Instance (ACI) named `mastersuctaci`. This instance runs a Linux-based container, specifically the `fsd-public-api` image, which is pulled directly from our ACR. The container is configured with 0.5 CPUs and 1.5 GB of memory, with port 80 open for HTTP traffic.
    - The ACI is assigned a public IP address and is accessible via a DNS name label `fsdpublicapi`, enabling users to interact with our API.

4. **Outputs**:
    - The configuration outputs the login server URL for the container registry and the fully qualified domain name (FQDN) for the container instance. These outputs provide essential endpoints for managing and accessing our deployed resources.

This Terraform setup ensures that our infrastructure is consistent, scalable, and easy to manage.

## Terraform Workflow in our Project

To apply changes defined in a Terraform configuration file, we generally follow a series of commands. Here's how they works:

### Terraform Commands

1. **`terraform init`**:
    - **Purpose**: This command initializes the Terraform working directory. It downloads the necessary provider plugins specified in our configuration file (e.g., `azurerm` for Azure) and sets up the backend for storing the state file (`terraform.tfstate`).
    - **When to Run**: We run this command once after creating or cloning a Terraform configuration. It’s also necessary after adding new providers or modules to the configuration.

2. **`terraform plan`**:

    - **Purpose**: This command creates an execution plan, showing us what Terraform will do when we apply our changes. It compares the state file with our current configuration to determine what needs to be created, modified, or destroyed.
    - **When to Run**: We use this command to review the changes before applying them. It’s a good practice to run it every time we make changes to your configuration file.

3. **`terraform apply`**:

    - **Purpose**: This command applies the changes required to reach the desired state of the configuration, as outlined by the plan. It prompts us to confirm the execution of the changes by typing "yes".
    - **When to Run**: After reviewing the plan, we run this command to apply the changes to your infrastructure.

4. **`terraform destroy`**:

    - **Purpose**: This command destroys all resources managed by our Terraform configuration. It is useful for cleaning up resources when they are no longer needed.
    - **When to Run**: We use this command when we want to completely remove our infrastructure. It will ask for confirmation before proceeding.

### Terraform State (`tfstate`)

- **What It Is**: Terraform's state file (`terraform.tfstate`) is a JSON file that keeps track of the infrastructure resources managed by Terraform. It acts as a snapshot of the deployed infrastructure, storing information about the current state of resources, including IDs, attributes, and metadata.

- **Purpose**: The state file is essential for Terraform to understand what has been created, modified, or destroyed. When we run `terraform plan` or `terraform apply`, Terraform compares the current state in the `tfstate` file with the desired state defined in your configuration file to determine the necessary actions.

- **Storage**: The state file is stored locally by default, but it can (and should) be stored remotely in a secure backend (e.g., Azure Blob Storage, AWS S3) to facilitate collaboration and ensure consistency across multiple team members.

### Terraform Diff

- **What It Is**: The diff in Terraform refers to the difference between the current state of our infrastructure (as recorded in the `tfstate` file) and the desired state defined in our Terraform configuration.

- **Purpose**: The diff is generated when we run `terraform plan`. It shows a summary of what will change if we run `terraform apply`. This includes resources to be created, modified, or destroyed, marked with `+`, `~`, and `-` respectively in the output.

- **Importance**: Reviewing the diff before applying changes is critical to ensure that the planned modifications align with your expectations. It helps avoid unintentional changes to our infrastructure.

By running these Terraform commands and understanding the role of the `tfstate` file and the diff, we can effectively manage our infrastructure changes, ensuring they are applied safely and accurately.