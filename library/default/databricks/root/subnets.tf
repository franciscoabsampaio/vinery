resource "azurerm_subnet" "ws_public_databricks" {
  name                 = "${local.prefix}-subnet_public_databricks"
  virtual_network_name = var.virtual_network_name
  resource_group_name  = var.resource_group_name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "databricks"

    service_delegation {
      name = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}

resource "azurerm_subnet" "ws_private_databricks" {
  name                 = "${local.prefix}-subnet_private_databricks"
  virtual_network_name = var.virtual_network_name
  resource_group_name  = var.resource_group_name
  address_prefixes     = ["10.0.3.0/24"]

  default_outbound_access_enabled = false

  delegation {
    name = "databricks"

    service_delegation {
      name = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}

resource "azurerm_network_security_group" "ws_databricks" {
  name                = "${local.prefix}-nsg_databricks"
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name
}

resource "azurerm_subnet_network_security_group_association" "ws_public_databricks" {
  subnet_id                 = azurerm_subnet.ws_public_databricks.id
  network_security_group_id = azurerm_network_security_group.ws_databricks.id
}

resource "azurerm_subnet_network_security_group_association" "ws_private_databricks" {
  subnet_id                 = azurerm_subnet.ws_private_databricks.id
  network_security_group_id = azurerm_network_security_group.ws_databricks.id
}