import pulumi_aws as aws

class vpc:
    def __init__(self, values):
        self.vpc = aws.ec2.Vpc(
            'vpc',
            
            cidr_block = '10.0.0.0/16',
            instance_tenancy = 'default',
            enable_dns_hostnames = True,
            enable_dns_support = True,

            tags = {
                'Name': values.vpc_properties["vpc-name"]
            }
        )

        self.igw = aws.ec2.InternetGateway(
            'vpc-igw',

            vpc_id = self.vpc.id,
            
            tags = {
                'Name': values.vpc_properties['vpc-igw-name']
            }
        )

        self.vpc_public_rt = aws.ec2.RouteTable(
            'vpc-public-rt',
            
            vpc_id = self.vpc.id,
            routes = [
                aws.ec2.RouteTableRouteArgs(
                    cidr_block = '0.0.0.0/0',
                    gateway_id = self.igw.id,
                )
            ],
            
            tags={
                'Name': values.vpc_properties['vpc-public-rt-name']
            }
        )

        self.vpc_private_rt = aws.ec2.RouteTable(
            'vpc-private-rt',

            vpc_id = self.vpc.id,

            tags = {
                'Name': values.vpc_properties['vpc-private-rt-name']
            }
        )
        
        self.zones = aws.get_availability_zones()
        self.public_subnet_ids = []
        self.private_subnet_ids = []

        for zone in self.zones.names:
            vpc_public_subnet = aws.ec2.Subnet(
                f'vpc-public-subnet-{zone}',
                
                vpc_id = self.vpc.id,
                cidr_block = f'10.0.{len(self.public_subnet_ids)}.0/24',
                availability_zone = zone,
                map_public_ip_on_launch = True,

                tags = {
                    'Name': f'{values.vpc_properties["vpc-public-subnet-name"]}-{zone}'
                }
            )

            vpc_private_subnet = aws.ec2.Subnet(
                f'vpc-private-subnet-{zone}',

                vpc_id = self.vpc.id,
                cidr_block = f'10.0.{len(self.private_subnet_ids)+100}.0/24',
                availability_zone = zone,

                tags = {
                    'Name': f'{values.vpc_properties["vpc-private-subnet-name"]}-{zone}'
                }
            )

            aws.ec2.RouteTableAssociation(
                f'vpc-public-rt-assoc-{zone}',
                
                route_table_id = self.vpc_public_rt.id,
                subnet_id = vpc_public_subnet.id
            )

            aws.ec2.RouteTableAssociation(
                f'vpc-private-rt-assoc-{zone}',

                route_table_id = self.vpc_private_rt.id,
                subnet_id = vpc_private_subnet.id
            )

            self.public_subnet_ids.append(vpc_public_subnet.id)
            self.private_subnet_ids.append(vpc_private_subnet.id)