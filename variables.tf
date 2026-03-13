variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type = string
}

variable "eventhub_namespace_name" {
  type = string
}

variable "eventhub_name" {
  type = string
}

variable "cosmosdb_account_name" {
  type = string
}

variable "cosmosdb_database_name" {
  type    = string
  default = "securitylogs"
}

variable "cosmosdb_container_name" {
  type    = string
  default = "alerts"
}

variable "storage_account_name" {
  type = string
}

variable "app_service_plan_name" {
  type = string
}

variable "function_app_name" {
  type = string
}
