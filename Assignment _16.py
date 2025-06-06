import boto3
import os
import json

def get_ec2_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances

def check_disk_space(instance_id):
    ssm = boto3.client('ssm')
    command = "df -h / | grep -v Filesystem | awk '{print $5}' | sed 's/%//'"
    
    try:
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command]}
        )
        command_id = response['Command']['CommandId']
        return command_id
    except Exception as e:
        print(f"Error sending command to instance {instance_id}: {str(e)}")
        return None

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    
    # Get all running EC2 instances
    instances = get_ec2_instances()
    print(f"Found {len(instances)} running instances")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully')
    }
