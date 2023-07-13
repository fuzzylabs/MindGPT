resource "azurerm_storage_account" "storage_account" {
    resource_group_name = var.resource_group_name
    name                = var.name
    location            = var.location

    account_tier                    = "Standard"
    account_kind                    = "StorageV2"
    account_replication_type        = "LRS"
    enable_https_traffic_only       = true
    access_tier                     = "Hot"
    allow_nested_items_to_be_public = true
}

# Storage container inside storage account
resource "azurerm_storage_container" "data_store" {
    name                  = var.container_name
    storage_account_name  = azurerm_storage_account.storage_account.name
    container_access_type = "container"
}
