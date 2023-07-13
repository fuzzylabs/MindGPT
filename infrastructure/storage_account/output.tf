output "primary_connection_string" {
  description = "Azure Storage Account - Primary connection string"
  value       = azurerm_storage_account.storage_account.primary_connection_string
  sensitive   = true
}

output "storage_container_url" {
  description = "The url of the storage container"
  value = "azure://${azurerm_storage_container.data_store.name}"
  sensitive = false
}

output "storage_account_name" {
  description = "The name of the storage account"
  value = azurerm_storage_account.storage_account.name
  sensitive = false
}
