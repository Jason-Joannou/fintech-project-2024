variable "resource_group_name" {
  default     = "rafiki-resource-group"
  description = "Name of the resource group."
}

variable "location" {
  default     = "uksouth"
  description = "Location of the resources."
}

variable "postgresql_admin_password" {
  description = "Password for the PostgreSQL admin user."
  type        = string
  sensitive   = true
}