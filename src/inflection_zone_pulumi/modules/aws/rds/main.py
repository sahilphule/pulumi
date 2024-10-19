import pulumi
import pulumi_aws as aws
from  commons.rds import data

class rds:
    def __init__(self, values, vpc):
        self.db_subnet_group = aws.rds.SubnetGroup(
            "db-subnet-group",

            name = values.rds_properties["db-subnet-group-name"],
            subnet_ids = vpc.private_subnet_ids
        )

        self.db_sg = aws.ec2.SecurityGroup(
            'db-sg',

            vpc_id = vpc.vpc.id,

            ingress = [
                aws.ec2.SecurityGroupIngressArgs(
                    from_port = 3306,
                    to_port = 3306,
                    protocol = 'tcp',
                    cidr_blocks = ['0.0.0.0/0']
                )
            ],

            egress = [
                aws.ec2.SecurityGroupEgressArgs(
                    from_port = 0,
                    to_port = 0,
                    protocol = -1,
                    cidr_blocks = ["0.0.0.0/0"]
                )
            ],

            tags = {
                'Name': values.rds_properties['db-sg-name']
            }
        )

        self.db = aws.rds.Instance(
            "db",

            identifier = values.rds_properties["db-identifier"],
            allocated_storage = values.rds_properties["db-allocated-storage"],
            engine = values.rds_properties["db-engine"],
            engine_version = values.rds_properties["db-engine-version"],
            instance_class = values.rds_properties["db-instance-class"],
            username = values.rds_properties["db-username"],
            password = values.rds_properties["db-password"],
            publicly_accessible = values.rds_properties["db-publicly-accessible"],
            skip_final_snapshot = values.rds_properties["db-skip-final-snapshot"],
            db_subnet_group_name = self.db_subnet_group.name,

            vpc_security_group_ids = [
                self.db_sg.id
            ]
        )

        self.bastion_host_sg = aws.ec2.SecurityGroup(
            'bastion-host-sg',

            vpc_id = vpc.vpc.id,

            ingress = [
                aws.ec2.SecurityGroupIngressArgs(
                    from_port = 22,
                    to_port = 22,
                    protocol = 'tcp',
                    cidr_blocks = ['0.0.0.0/0']
                )
            ],

            egress = [
                aws.ec2.SecurityGroupEgressArgs(
                    from_port = 0,
                    to_port = 0,
                    protocol = -1,
                    cidr_blocks = ['0.0.0.0/0']
                )
            ],

            tags = {
                'Name': values.bastion_properties['bastion-host-sg-name']
            }
        )

        self.bastion_host_key_pub_file = open(values.bastion_properties["bastion-host-key-public-file"],"r+")

        self.bastion_host_key_pair = aws.ec2.KeyPair(
            "bastion-host-key-pair",

            key_name = "bastion-host-key-pair",
            public_key = self.bastion_host_key_pub_file.read()
        )

        self.bastion_host = aws.ec2.Instance(
            "bastion-host",

            ami = data.linux_ami.id,
            instance_type = values.bastion_properties["bastion-host-instance-type"],
            key_name = self.bastion_host_key_pair.id,
            subnet_id = vpc.public_subnet_ids[0],
            vpc_security_group_ids = [
                self.bastion_host_sg.id
            ],

            tags = {
                'Name': values.bastion_properties["bastion-host-name"]
            }
        )

        pulumi.export("DB_HOST", self.db.address)
        pulumi.export("bastion-host-ip", self.bastion_host.public_ip)