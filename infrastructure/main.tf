provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "./resource_group"

  resource_group_name = var.resource_group_name
  location = var.location
}

module "storage_account" {
  source = "./storage_account"

  depends_on = [module.resource_group]

  resource_group_name = var.resource_group_name
  location = var.location
  name = "mindgptdvc"
  container_name = "mindgptdvccontainer"
}
