resource "azurerm_storage_account" "storage_account" {
    resource_group_name = var.resource_group_name
    name                = "mindgptstacc"
    location            = var.location

    account_tier                    = "Standard"
    account_kind                    = "StorageV2"
    account_replication_type        = "LRS"
    enable_https_traffic_only       = true
    access_tier                     = "Hot"
    allow_nested_items_to_be_public = true
}

# Storage container inside storage account
resource "azurerm_storage_container" "scraped_data_store" {
    name                  = "scraped-data-store"
    storage_account_name  = azurerm_storage_account.storage_account.name
    container_access_type = "container"
}
