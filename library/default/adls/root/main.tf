provider "azurerm" {
  features {}
}

locals {
  prefix = "${var.project}-${terraform.workspace}"
}

// Create new storage accounts
resource "azurerm_storage_account" "ws_account" {
  for_each = { for k, v in var.accounts : k => v if v.create_new }

  name                     = "${local.prefix}-adls"
  resource_group_name      = var.resource_group_name
  location                 = var.resource_group_location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
// and respective containers
resource "azurerm_storage_container" "ws_account_container" {
  for_each = merge([
    for account, details in var.accounts : {
      for container in details.containers :
      "${account}-${container}" => {
        storage_account_name = azurerm_storage_account.ws_account[account].name
        container_name       = container
        is_private           = details.is_private
      }
    } if details.create_new
  ]...)

  name                  = each.value.container_name
  storage_account_id    = azurerm_storage_account.ws[each.value.adls_key].id
  container_access_type = "private" ? each.value.is_private : "blob"
}

// If a storage account already exists, and resides in its own private network
// Create a private endpoint from the default subnet to it
resource "azurerm_private_endpoint" "adls" {
  for_each = { for k, v in var.accounts : k => v if !v.create_new && v.is_private }

  name                = "${local.prefix}-pe-adls_${each.key}"
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name

  subnet_id = var.subnet_default_id

  private_service_connection {
    name                           = "${local.prefix}-psc-adls_${each.key}"
    private_connection_resource_id = each.value.resource_id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }
}