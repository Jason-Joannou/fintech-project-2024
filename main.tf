# IaC main file

# Define provider
provider "azurerm" {
  features {

  }

}

# Define resource group
resource "azurerm_resource_group" "masters_uct" {
  name     = "Masters-UCT"
  location = "UK South"
}

# Define our container registry
resource "azurerm_container_registry" "acr" {
  name                = "mastersuctacr"
  resource_group_name = azurerm_resource_group.masters_uct.name
  location            = azurerm_resource_group.masters_uct.location
  sku                 = "Basic"
  admin_enabled       = true
}



