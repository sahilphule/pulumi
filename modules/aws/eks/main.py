import pulumi_aws as aws
from commons.eks import data
import json

class eks:
    def __init__(self, values, vpc):
        self.eks_cluster_role = aws.iam.Role(
            'eks-cluster-role',

            name = values.eks_properties["eks-cluster-role-name"],
            assume_role_policy = json.dumps(data.eks_cluster_role_policy_document)
        )

        aws.iam.RolePolicyAttachment(
            'eks-cluster-role-AmazonEKSClusterPolicy',
            
            role = self.eks_cluster_role.id,
            policy_arn = 'arn:aws:iam::aws:policy/AmazonEKSClusterPolicy'
        )

        self.eks_cluster_sg = aws.ec2.SecurityGroup(
            'eks-cluster-sg',

            vpc_id = vpc.vpc.id,

            ingress = [
                aws.ec2.SecurityGroupIngressArgs(
                    from_port = 80,
                    to_port = 80,
                    protocol = 'tcp',
                    cidr_blocks = ['0.0.0.0/0']
                )
            ],
            egress = [
                {
                    "from_port": 0,
                    "to_port": 0,
                    "protocol": -1,
                    "cidr_blocks": ["0.0.0.0/0"]
                }
            ],
            
            tags = {
                'Name': values.eks_properties['eks-cluster-sg-name']
            }
        )

        self.eks_cluster = aws.eks.Cluster(
            'eks-cluster',
            
            name = values.eks_properties["eks-cluster-name"],
            role_arn = self.eks_cluster_role.arn,
            
            vpc_config = aws.eks.ClusterVpcConfigArgs(
                public_access_cidrs = ['0.0.0.0/0'],
                security_group_ids = [
                    self.eks_cluster_sg.id
                ],
                subnet_ids = vpc.public_subnet_ids
            )
        )

        self.eks_node_group_role = aws.iam.Role(
            'eks-node-group-role',
            
            name = values.eks_properties["eks-node-group-role-name"],
            assume_role_policy = json.dumps(data.eks_node_group_role_policy_document)
        )

        aws.iam.RolePolicyAttachment(
            'eks-node-group-role-AmazonEKSWorkerNodePolicy',
            
            role = self.eks_node_group_role.id,
            policy_arn = 'arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy'
        )


        aws.iam.RolePolicyAttachment(
            'eks-node-group-role-cni-policy-attachment',
            
            role = self.eks_node_group_role.id,
            policy_arn = 'arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy'
        )

        aws.iam.RolePolicyAttachment(
            'eks-node-group-role-AmazonEC2ContainerRegistryReadOnly',
            
            role = self.eks_node_group_role.id,
            policy_arn = 'arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly'
        )

        self.eks_nodegroup = aws.eks.NodeGroup(
            'eks-node-group',
            
            node_group_name = values.eks_properties['eks-node-group-name'],
            cluster_name = self.eks_cluster.name,
            node_role_arn = self.eks_node_group_role.arn,

            subnet_ids = vpc.public_subnet_ids,
            instance_types = values.eks_properties["eks-instance-types"],
            
            scaling_config = aws.eks.NodeGroupScalingConfigArgs(
                desired_size = 1,
                max_size = 1,
                min_size = 1
            )
        )