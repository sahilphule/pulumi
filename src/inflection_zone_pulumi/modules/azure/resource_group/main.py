from pulumi_azure_native import resources

# Create new resource group

class resource_group:
    def __init__(self, values):
        self.resource_group = resources.ResourceGroup(
            "resource_group",
            
            resource_group_name = values.resource_group_properties["rg-name"],
            location = values.resource_group_properties["rg-location"]
        )