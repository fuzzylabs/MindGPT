output "azure_storage_primary_connection_string" {
    description = "The Azure connection string for the MindGPT data storage."
    value       = module.storage_account.primary_connection_string
    sensitive   = true
}
