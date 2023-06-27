output "primary_connection_string" {
  description = "Azure Storage Account - Primary connection string"
  value       = azurerm_storage_account.storage_account.primary_connection_string
  sensitive   = true
}
