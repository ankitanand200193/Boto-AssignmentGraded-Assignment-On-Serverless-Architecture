import boto3
from datetime import datetime

def lambda_handler(event, context):
    """
    AWS Lambda function to manage EC2 instances based on tags:
    - Stops instances with Action:Auto-Stop-Ankit tag
    - Starts instances with Action:Auto-Start-Ankit tag
    """
    print(f"Starting EC2 instance management - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize boto3 EC2 client
    ec2_client = boto3.client('ec2')
    
    # Find and stop instances with Auto-Stop-Ankit tag
    stop_response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['Auto-Stop-Ankit']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    # Process instances to stop
    instances_to_stop = []
    for reservation in stop_response['Reservations']:
        for instance in reservation['Instances']:
            instances_to_stop.append(instance['InstanceId'])
    
    if instances_to_stop:
        print(f"Stopping instances: {instances_to_stop}")
        ec2_client.stop_instances(InstanceIds=instances_to_stop)
    else:
        print("No running instances found with Auto-Stop-Ankit tag")
    
    # Find and start instances with Auto-Start-Ankit tag
    start_response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['Auto-Start-Ankit']},
            {'Name': 'instance-state-name', 'Values': ['stopped']}
        ]
    )
    
    # Process instances to start
    instances_to_start = []
    for reservation in start_response['Reservations']:
        for instance in reservation['Instances']:
            instances_to_start.append(instance['InstanceId'])
    
    if instances_to_start:
        print(f"Starting instances: {instances_to_start}")
        ec2_client.start_instances(InstanceIds=instances_to_start)
    else:
        print("No stopped instances found with Auto-Start-Ankit tag")
    
    # Return results for logging
    return {
        'statusCode': 200,
        'instancesStopped': instances_to_stop,
        'instancesStarted': instances_to_start
    }
