import pulumi
from pulumi_azure_native import app, operationalinsights

class container_app:
    def __init__(self, values, resource_group, vnet, acr):
        self.workspace = operationalinsights.Workspace(
            "container-app-log-analytics-workspace",
            
            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,

            workspace_name = values.container_app_properties["container-app-log-analytics-workspace-name"],
            sku = operationalinsights.WorkspaceSkuArgs(name = "PerGB2018"),
            retention_in_days = 30
        )

        self.workspace_shared_keys = pulumi.Output.all(resource_group.resource_group.name, self.workspace.name).apply(
            lambda args: operationalinsights.get_shared_keys(
                resource_group_name = args[0],
                workspace_name = args[1]
            )
        )

        self.managed_environment = app.ManagedEnvironment(
            "container-app-environment",
            
            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
            
            environment_name = values.container_app_properties["container-app-environment-name"],
        
            app_logs_configuration = app.AppLogsConfigurationArgs(
                destination = "log-analytics",
                log_analytics_configuration = app.LogAnalyticsConfigurationArgs(
                    customer_id = self.workspace.customer_id,
                    shared_key = self.workspace_shared_keys.apply(lambda r: r.primary_shared_key)
                )
            ),
        
            vnet_configuration = app.VnetConfigurationArgs(
                infrastructure_subnet_id = vnet.subnet.id,
            )
        )

        self.container_app = app.ContainerApp(
            "container-app",
            
            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,

            container_app_name = values.container_app_properties["container-app-name"],
            managed_environment_id = self.managed_environment.id,

            configuration = {
                "ingress": {
                    "external": True,
                    "target_port": 3000,
                },
                "registries": [{
                    # "identity": "string",
                    "server": acr.acr.login_server,
                    "username": acr.admin_username,
                    "password_secret_ref": "acrpassword",
                }],
                "secrets": [{
                    # "identity": "string",
                    # "key_vault_url": "string",
                    "name": "acrpassword",
                    "value": acr.admin_password,
                }],
            },
            template={
                "containers": [{
                    "image": values.container_app_properties["container-app-container-image"],
                    "name": values.container_app_properties["container-app-container-name"],
                }],
                "scale": {
                    "min_replicas": values.container_app_properties["container-app-min-replicas"],
                    "max_replicas": values.container_app_properties["container-app-max-replicas"],
                    "rules": [{
                        "custom": {
                            "metadata": {
                                "concurrentRequests": "50",
                            },
                            "type": "http",
                        },
                        "name": "httpscalingrule",
                    }],
                },
            },
            workload_profile_type="GeneralPurpose"
        )

        pulumi.export("container-app-url", self.container_app.configuration.ingress.fqdn)