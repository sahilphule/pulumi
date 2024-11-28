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

            configuration = app.ConfigurationArgs(
                ingress = app.IngressArgs(
                    external = values.container_app_properties["container-app-ingress-external-enabled"],
                    target_port = values.container_app_properties["container-app-ingress-port"],
                ),
                registries = [
                    app.RegistryCredentialsArgs(
                        server = acr.acr.login_server,
                        username = acr.admin_username,
                        password_secret_ref = "acrpassword")
                ],
                secrets = [
                    app.SecretArgs(
                        name = "acrpassword",
                        value = acr.admin_password)
                ],         
            ),
            
            template = app.TemplateArgs(
                containers = [
                    app.ContainerArgs(
                        name = values.container_app_properties["container-name"],
                        image = values.container_app_properties["container-image"]
                    )
                ]
            )
        )

        pulumi.export("container-app-url", self.container_app.configuration.ingress.fqdn)