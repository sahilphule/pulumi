import pulumi_aws as aws

linux_ami = aws.ec2.get_ami(
    most_recent = True,
    owners = ["137112412989"],

    filters = [
        {
            "name": "name",
            "values": ["al2023-ami-2023.5.20240819.0-kernel-6.1-x86_64"]
        },
        {
            "name": "virtualization-type",
            "values": ["hvm"]
        }
    ]
)