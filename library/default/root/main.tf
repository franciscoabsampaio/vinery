provider "azurerm" {
  features {}
}

locals {
  prefix = "${var.project}-${terraform.workspace}"
}

resource "azurerm_resource_group" "ws" {
  name     = "${local.prefix}-rg"
  location = var.region

  tags = {
    Environment = terraform.workspace
    Project = var.project
  }
}
