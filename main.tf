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



