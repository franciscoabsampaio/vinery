resource "azurerm_virtual_network" "ws" {
  name                = "${local.prefix}-vnet"
  location            = azurerm_resource_group.ws.location
  resource_group_name = azurerm_resource_group.ws.name
  address_space       = ["10.0.0.0/16"]
  dns_servers         = ["10.0.0.4", "10.0.0.5"]

  tags = {
    Environment = terraform.workspace
    Project = var.project
  }
}

resource "azurerm_subnet" "ws_default" {
  name                 = "${local.prefix}-subnet_default"
  virtual_network_name = azurerm_virtual_network.ws.name
  resource_group_name  = azurerm_resource_group.ws.name
  address_prefixes     = ["10.0.1.0/24"]
}
