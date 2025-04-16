variable "accounts" {
  description = "A map of account configurations"
  type = map(object({
    create_new            = bool
    is_private            = bool
    resource_id           = optional(string)
    blob_service_endpoint = optional(string)
    containers            = list(string)
  }))

  validation {
    condition = alltrue([
      for name, acc in var.accounts :
      (acc.create_new && acc.resource_id == null && acc.blob_service_endpoint == null)
      || (!acc.create_new && acc.resource_id != null && acc.blob_service_endpoint != null)
    ])
    error_message = "If 'create_new' is true, 'resource_id' and 'blob_service_endpoint' must NOT be defined. If 'create_new' is false, both must be defined."
  }
}
