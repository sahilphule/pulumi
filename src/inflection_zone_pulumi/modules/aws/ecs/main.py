import pulumi
import pulumi_aws as aws
from . import data
import json

class ecs:
    def __init__(self, values, vpc, load_balancer):
        self.ecs_cluster = aws.ecs.Cluster(
            "ecs-cluster",

            name = values.ecs_properties["ecs-cluster-name"]
        )

        self.ecs_task_role = aws.iam.Role(
            "ecs-task-execution-role",
            
            name = values.ecs_properties["ecs-task-execution-role-name"],
            assume_role_policy = json.dumps(data.ecs_task_role_policy_document)
        )

        aws.iam.RolePolicyAttachment(
            "ecs-task-execution-role-AmazonECSTaskExecutionRolePolicy",
            
            role = self.ecs_task_role.name,
            policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
        )

        self.ecs_task_definition = aws.ecs.TaskDefinition(
            "ecs-task",
            
            family = values.ecs_properties["ecs-task-family-name"],
            network_mode = "awsvpc",
            cpu = 512,
            memory = 1024,
            requires_compatibilities = ["FARGATE"],
            execution_role_arn = self.ecs_task_role.arn,
            container_definitions = json.dumps(values.ecs_container_definition)
        )

        self.ecs_service = aws.ecs.Service(
            "ecs-service",
            
            name = values.ecs_properties["ecs-service-name"],
            cluster = self.ecs_cluster.arn,
            desired_count = values.ecs_properties["ecs-service-desired-count"],
            launch_type = "FARGATE",
            task_definition = self.ecs_task_definition.arn,
            
            network_configuration = {
                "assign_public_ip": True,
                "subnets": vpc.public_subnet_ids,
                "security_groups": [load_balancer.load_balancer_sg.id]
            },
            
            load_balancers = [
                {
                    "target_group_arn": load_balancer.load_balancer_tg.arn,
                    "container_name": values.ecs_properties["ecs-container-name"],
                    "container_port": values.ecs_properties["ecs-container-port"]
                }
            ],
            
            opts = pulumi.ResourceOptions(
                depends_on = [
                    load_balancer.load_balancer_listner
                ]
            )
        )