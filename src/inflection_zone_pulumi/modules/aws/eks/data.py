import pulumi_aws as aws

eks_cluster_role_policy_document = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Action': 'sts:AssumeRole',
            'Principal': {
                'Service': 'eks.amazonaws.com'
            },
            'Effect': 'Allow'
        }
    ]
}

eks_node_group_role_policy_document = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Action': 'sts:AssumeRole',
            'Principal': {
                'Service': 'ec2.amazonaws.com'
            },
            'Effect': 'Allow',
        }
    ]
}