resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "rafiki-vnet"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "default" {
  name                 = "rafiki-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "postgresql-delegation"

    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"

      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_private_dns_zone" "dns_zone" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "dns_link" {
  name                  = "dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.dns_zone.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "rafiki-aks-cluster"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "rafikiaks"

  default_node_pool {
    name       = "default"
    node_count = 1  # Reduced node count for student subscription
    vm_size    = "Standard_B2s"  # Smaller VM size for cost-effectiveness
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
    dns_service_ip = "10.2.0.10"
    service_cidr   = "10.2.0.0/16"
  }
}

resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "rafiki-postgres-server"
  location               = azurerm_resource_group.rg.location
  resource_group_name    = azurerm_resource_group.rg.name
  administrator_login    = "adminuser"
  administrator_password = var.postgresql_admin_password
  version                = "13"
  storage_mb             = 32768  # Minimum allowed storage
  sku_name               = "B_Standard_B1ms"  # Smaller SKU for student subscription
  backup_retention_days  = 7

  delegated_subnet_id    = azurerm_subnet.default.id
  private_dns_zone_id    = azurerm_private_dns_zone.dns_zone.id
  public_network_access_enabled = false  # Disable Public Network Access
}

resource "azurerm_postgresql_flexible_server_database" "postgres_db" {
  name      = "rafiki_db"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  collation = "en_GB.utf8"  # UK-specific collation
  charset   = "UTF8"
}

resource "azurerm_redis_cache" "redis" {
  name                = "rafiki-redis-cache"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  capacity            = 0  # Smaller capacity for cost-effectiveness
  family              = "C"
  sku_name            = "Basic"  # Required attribute
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}

output "postgresql_host" {
  value = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "postgresql_username" {
  value = azurerm_postgresql_flexible_server.postgres.administrator_login
}

output "postgresql_password" {
  value     = var.postgresql_admin_password
  sensitive = true
}

output "redis_host" {
  value = azurerm_redis_cache.redis.hostname
}

output "redis_port" {
  value = azurerm_redis_cache.redis.port
}