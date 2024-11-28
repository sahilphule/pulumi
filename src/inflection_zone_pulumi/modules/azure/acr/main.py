import pulumi
from pulumi_azure_native import containerregistry

class acr:
    def __init__(self, values, resource_group):
        self.acr = containerregistry.Registry(
            "acr",

            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
            
            registry_name = values.acr_properties["acr-registry-name"],
            sku = containerregistry.SkuArgs(
                name = "Basic",
            ),
            admin_user_enabled = values.acr_properties["acr-admin-user-enabled"]
        )
 
        self.credentials = pulumi.Output.all(
            resource_group.resource_group.name, 
            self.acr.name
            ).apply(
                lambda args: containerregistry.list_registry_credentials(
                    resource_group_name = args[0],
                    registry_name = args[1]
                )
            )
        
        self.admin_username = self.credentials.username
        self.admin_password = self.credentials.passwords[0]["value"]

        pulumi.export("acr-login-server", self.acr.login_server)
