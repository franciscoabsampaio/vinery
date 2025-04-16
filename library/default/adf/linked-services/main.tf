provider "azurerm" {
  features {}
}

locals {
  prefix = "${var.project}-${terraform.workspace}"
}
