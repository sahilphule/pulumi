from pulumi_azure_native import containerservice

class aks:
    def __init__(self, values, resource_group, vnet):
        self.managed_cluster = containerservice.ManagedCluster(
            "aks-cluster",

            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,

            kubernetes_version = values.aks_properties["aks-kubernetes-version"],
            dns_prefix = resource_group.resource_group.name,
            enable_rbac = True,
            node_resource_group = f"MC_azure-native-go_{values.aks_properties["aks-cluster-name"]}_centralindia",
         
            agent_pool_profiles = [
                {
                    "name": values.aks_properties["aks-agent-pool-profiles-name"],
                    "type": values.aks_properties["aks-agent-pool-profile-type"],
                    "mode": values.aks_properties["aks-agent-pool-profile-mode"],
                    "vm_size": values.aks_properties["aks-agent-pool-profile-vm-size"],
                    "max_pods": values.aks_properties["aks-agent-pool-profile-max-pods"],
                    "count": values.aks_properties["aks-agent-pool-profile-count"],
                    "enable_node_public_ip": values.aks_properties["aks-agnet-pool-profile-enable-node-public-ip"],
                    "node_labels": {},
                    "os_disk_size_gb": 30,
                    "os_type": "Linux",
                    "vnet_subnet_id": vnet.subnet.id,
                }
            ],

            identity={
                "type": containerservice.ResourceIdentityType.SYSTEM_ASSIGNED,
            },

            # service_principal_profile = {
            #     "client_id": values.aks_properties["aks-service-principal-client-id"],
            #     "secret": values.aks_properties["aks-service-principal-secret"]
            # }
        )