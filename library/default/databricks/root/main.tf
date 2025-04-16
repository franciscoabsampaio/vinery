provider "azurerm" {
  features {}
}

locals {
  prefix = "${var.project}-${terraform.workspace}"
}

resource "azurerm_databricks_workspace" "env" {
  name                = "${local.prefix}-dbw"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_location
  sku                 = var.sku

  public_network_access_enabled         = !var.is_private
  network_security_group_rules_required = v.sku == "premium" ? "NoAzureDatabricksRules" : "AllRules"

  custom_parameters {
    no_public_ip = var.is_private

    virtual_network_id  = var.virtual_network_id
    public_subnet_name  = azurerm_subnet.ws_public_databricks.name
    private_subnet_name = azurerm_subnet.ws_private_databricks.name

    public_subnet_network_security_group_association_id  = azurerm_subnet_network_security_group_association.ws_public_databricks.id
    private_subnet_network_security_group_association_id = azurerm_subnet_network_security_group_association.ws_private_databricks.id
  }
}

module "azurerm-dbw_private_link" {
  count = var.sku == "premium" ? 1 : 0
  source = "../modules/azurerm-dbw_private_link"

  dbw_id                  = azurerm_databricks_workspace.ws.id
  prefix                  = localprefix
  resource_group_location = var.resource_group_location
  resource_group_name     = var.resource_group_name
  subnet_id               = var.subnet_default_id
  vnet_id                 = var.virtual_network_id
}