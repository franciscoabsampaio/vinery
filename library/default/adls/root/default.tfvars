accounts = {
  alice = {
    create_new            = false,
    # The resource provider must have read access to the storage account
    # A private DNS zone in the ADLS subscription linked to this VNet is required
    resource_id           = "0000000-xxxx-xxxx-xxxx-000000000000/resourceGroups/proj-dev-rg/providers/Microsoft.Storage/storageAccounts/xxxxxxxx",
    blob_service_endpoint = "https://xxxxxxxx.blob.core.windows.net/"
    is_private            = true,
  },
  bob = {
    create_new = true
    is_private = true,
    containers = ["container1", "container2"]
  }
}