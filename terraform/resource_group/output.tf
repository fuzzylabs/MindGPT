output "name" {
  description = "Name of the resource group"
  value = azurerm_resource_group.resource_group.name
}

output "location" {
  description = "Location of the resource group"
  value = azurerm_resource_group.resource_group.location
}
