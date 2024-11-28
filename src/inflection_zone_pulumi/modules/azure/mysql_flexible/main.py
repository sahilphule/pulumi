import pulumi
from pulumi_azure_native import network, dbformysql

class mysql_flexible:
    def __init__(self, values, resource_group, vnet):
        self.subnet = network.Subnet(
            "mysql-flexible-subnet",

            resource_group_name = resource_group.resource_group.name,

            subnet_name = values.mysql_flexible_properties["mysql-flexible-subnet-name"],
            address_prefix = values.mysql_flexible_properties["mysql-flexible-subnet-address-prefix"],
            virtual_network_name = vnet.vnet.name,

            delegations = [
                network.DelegationArgs(
                    name = "delegation",
                    service_name = "Microsoft.DBforMySQL/flexibleServers"
                )
            ]
        )

        self.mysql_server = dbformysql.Server(
            "mysql-flexible-server",

            resource_group_name = resource_group.resource_group.name,
            location = resource_group.resource_group.location,
            
            server_name = values.mysql_flexible_properties["mysql-flexible-server-name"],
            version = values.mysql_flexible_properties["mysql-flexible-server-version"],
            administrator_login = values.mysql_flexible_properties["mysql-flexible-server-admin-username"],
            administrator_login_password = values.mysql_flexible_properties["mysql-flexible-server-admin-password"],

            sku = dbformysql.SkuArgs(
                name = values.mysql_flexible_properties["mysql-flexible-server-sku-name"],
                tier = "Burstable"
            ),

            storage = dbformysql.StorageArgs(
                storage_size_gb = 32
            ),

            backup = dbformysql.BackupArgs(
                backup_retention_days = 7,
                geo_redundant_backup = "Disabled"
            ),
 
            network = dbformysql.NetworkArgs(
                delegated_subnet_resource_id = self.subnet.id,
                private_dns_zone_resource_id = None
            )
        
            # backup={
            #     "backup_retention_days": 7,
            #     "geo_redundant_backup": azure_native.dbformysql.EnableStatusEnum.DISABLED,
            # },
                        
            # storage={
            #     "auto_grow": azure_native.dbformysql.EnableStatusEnum.DISABLED,
            #     "iops": 600,
            #     "storage_size_gb": 100,
            # },    
        )


       # self.mysql_database = dbformysql.Database(
        #     "mysql-database",
            
        #     resource_group_name = resource_group.resource_group.name,
        #     server_name = self.mysql_server.name,
            
        #     charset = "utf8mb4",
        #     collation = "utf8mb4_general_ci",
        # )
        
        pulumi.export("mysql-server-fqdn", self.mysql_server.fully_qualified_domain_name)