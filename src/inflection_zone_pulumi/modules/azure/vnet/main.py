from pulumi_azure_native import network

class vnet:
    def __init__(self, values, resource_group):
        self.vnet = network.VirtualNetwork(
            "virtualNetwork",
            
            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
            
            virtual_network_name = values.vnet_properties["vnet-name"],
            
            address_space = {
                "address_prefixes": values.vnet_properties["vnet-address-prefixes"]
            }
        )

        self.subnet_count = values.vnet_properties["vnet-public-subnet-count"]

        for subnet in range(0, self.subnet_count):
            self.subnet = network.Subnet(
                f"subnet-{subnet}",

                resource_group_name = resource_group.resource_group.name,
        
                subnet_name = values.vnet_properties["vnet-subnet-names"][subnet],
                address_prefix = f"10.1.{subnet}.0/23",
                virtual_network_name = self.vnet.name,
                private_endpoint_network_policies = "Disabled",
                private_link_service_network_policies = "Disabled"
            )