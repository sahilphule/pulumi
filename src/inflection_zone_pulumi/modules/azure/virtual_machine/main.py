import pulumi
import base64
from pulumi_azure_native import compute, network

class virtual_machine:
    def __init__(self, values, resource_group, vnet):
        # Public IP
        self.public_ip = network.PublicIPAddress(
            "vm-public-ip",

            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
        
            # name = values.virtual_machine_properties["public-ip-name"],
            public_ip_allocation_method = values.virtual_machine_properties["public-ip-allocation-method"],
        )

        self.nsg = network.NetworkSecurityGroup(
            "network-security-group",

            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,

            # name = values.virtual_machine_properties["network-security-group-name"],
            security_rules = [
                network.SecurityRuleArgs(
                    name = "AllowSSH",
                    priority = 100,
                    direction = "Inbound",
                    access = "Allow",
                    protocol = "Tcp",
                    source_port_range = "*",
                    destination_port_range = "22",
                    source_address_prefix = "*",
                    destination_address_prefix = "*",
                ),
                network.SecurityRuleArgs(
                    name = "AllowHTTP",
                    priority = 200,
                    direction = "Inbound",
                    access = "Allow",
                    protocol = "Tcp",
                    source_port_range = "*",
                    destination_port_range = "80",
                    source_address_prefix = "*",
                    destination_address_prefix = "*",
                ),
                network.SecurityRuleArgs(
                    name = "AllowHTTPS",
                    priority = 300,
                    direction = "Inbound",
                    access = "Allow",
                    protocol = "Tcp",
                    source_port_range = "*",
                    destination_port_range = "443",
                    source_address_prefix = "*",
                    destination_address_prefix = "*",
                ),
            ],
        )

        # Network Interface
        self.network_interface = network.NetworkInterface(
            "network-interface",
        
            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
        
            # name = values.virtual_machine_properties["network-interface-name"],
            ip_configurations = [
                network.NetworkInterfaceIPConfigurationArgs(
                    name = values.virtual_machine_properties["network-interface-ip-configuration-name"],
                    subnet = network.SubnetArgs(id = vnet.subnet.id),
                    public_ip_address = network.PublicIPAddressArgs(id = self.public_ip.id),
                )
            ],
            network_security_group = network.NetworkSecurityGroupArgs(id = self.nsg.id),
        )

        self.custom_data_file_path = values.virtual_machine_properties["virtual-machine-vm-custom-data-file-path"]

        # Read and encode the custom data script
        with open(self.custom_data_file_path, "r") as file:
            self.custom_data_script = file.read()

        self.custom_data_encoded = base64.b64encode(self.custom_data_script.encode("utf-8")).decode("utf-8")
        
        # Virtual Machine
        self.vm = compute.VirtualMachine(
            "virtual-machine",
        
            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
        
            # name = values.virtual_machine_properties["virtual-machine-vm-name"],
            hardware_profile = compute.HardwareProfileArgs(vm_size = values.virtual_machine_properties["virtual-machine-vm-size"]),
            os_profile = compute.OSProfileArgs(
                computer_name = values.virtual_machine_properties["virtual-machine-vm-os-profile-computer-name"],
                admin_username = values.virtual_machine_properties["virtual-machine-vm-os-profile-admin-username"],
                admin_password = values.virtual_machine_properties["virtual-machine-vm-os-profile-admin-password"],
                custom_data = self.custom_data_encoded,
            ),
            storage_profile = compute.StorageProfileArgs(
                os_disk = compute.OSDiskArgs(
                    create_option = values.virtual_machine_properties["virtual-machine-vm-storage-profile-os-disk-create-option"],
                    managed_disk = compute.ManagedDiskParametersArgs(
                        storage_account_type = values.virtual_machine_properties["virtual-machine-vm-storage-profile-os-disk-storage-account-type"]
                    ),
                ),
                image_reference = compute.ImageReferenceArgs(
                    publisher = values.virtual_machine_properties["virtual-machine-vm-storage-profile-image-reference-publisher"],
                    offer = values.virtual_machine_properties["virtual-machine-vm-storage-profile-image-reference-offer"],
                    sku = values.virtual_machine_properties["virtual-machine-vm-storage-profile-image-reference-sku"],
                    version = values.virtual_machine_properties["virtual-machine-vm-storage-profile-image-reference-version"],
                ),
            ),
            network_profile = compute.NetworkProfileArgs(
                network_interfaces = [
                    compute.NetworkInterfaceReferenceArgs(id = self.network_interface.id)
                ]
            ),
        )

        # Output the VM's public IP address
        pulumi.export("vm-public-ip", self.public_ip.ip_address)
