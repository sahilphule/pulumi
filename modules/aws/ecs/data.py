import pulumi_aws as aws

ecs_task_role_policy_document = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Action': 'sts:AssumeRole',
            'Principal': {
                'Service': 'ecs-tasks.amazonaws.com'
            },
            'Effect': 'Allow'
        }
    ]
}