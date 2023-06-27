output "storage_container_name" {
  description = "The name of the Azure Storage Container."
  value = azurerm_storage_container.scraped_data_store.name
}

output "blobstorage_container_path" {
  description = "The Azure Blob Storage Container path for storing your artifacts"
  value       = "az://${azurerm_storage_container.scraped_data_store.name}"
}

output "storage_account_name" {
  description = "The name of the Azure Storage Account."
  value = azurerm_storage_account.storage_account.name
}

output "primary_access_key" {
  description = "Azure Storage Account - Primary access key"
  value       = azurerm_storage_account.storage_account.primary_access_key
  sensitive   = true
}

output "secondary_access_key" {
  description = "Azure Storage Account - Secondary access key"
  value       = azurerm_storage_account.storage_account.secondary_access_key
  sensitive   = true
}

output "primary_connection_string" {
  description = "Azure Storage Account - Primary connection string"
  value       = azurerm_storage_account.storage_account.primary_connection_string
  sensitive   = true
}

output "secondary_connection_string" {
  description = "Azure Storage Account - Secondary connection string"
  value       = azurerm_storage_account.storage_account.secondary_connection_string
  sensitive   = true
}
