variable "is_private" {
    type = bool
}

variable "sku" {
  type = string

  validation {
    condition = var.sku != "premium" && var.is_private == true

    error_message = "ERROR: Allow private frontend only if SKU is Premium tier."
  }
}