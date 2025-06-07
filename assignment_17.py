import boto3
import time
from datetime import datetime

def lambda_handler(event, context):
    # Initialize EC2 client
    ec2 = boto3.client('ec2')
    
    # Instance IDs to look for snapshots
    instance_ids = ['i-0052f4aae7909657e']
    
    try:
        for instance_id in instance_ids:
            # First, get the AZ of the original instance
            instance_response = ec2.describe_instances(InstanceIds=[instance_id])
            original_instance = instance_response['Reservations'][0]['Instances'][0]
            availability_zone = original_instance['Placement']['AvailabilityZone']
            
            print(f"Using Availability Zone: {availability_zone}")
            
            # Get the most recent snapshot for this instance
            snapshots = ec2.describe_snapshots(
                Filters=[
                    {
                        'Name': 'tag:InstanceId',
                        'Values': [instance_id]
                    }
                ],
                OwnerIds=['self']
            )
            
            if not snapshots['Snapshots']:
                print(f"No snapshots found for instance {instance_id}")
                continue
                
            # Sort snapshots by date and get the most recent one
            latest_snapshot = sorted(snapshots['Snapshots'], 
                                  key=lambda x: x['StartTime'],
                                  reverse=True)[0]
            
            snapshot_id = latest_snapshot['SnapshotId']
            print(f"Found latest snapshot: {snapshot_id}")
            
            # Create a new volume from the snapshot
            volume = ec2.create_volume(
                SnapshotId=snapshot_id,
                AvailabilityZone=availability_zone,
                TagSpecifications=[
                    {
                        'ResourceType': 'volume',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': f'Restored-from-{instance_id}'
                            }
                        ]
                    }
                ]
            )
            
            print(f"Created new volume: {volume['VolumeId']}")
            
            # Wait for volume to be available
            waiter = ec2.get_waiter('volume_available')
            waiter.wait(VolumeIds=[volume['VolumeId']])
            
            # Launch new EC2 instance
            new_instance = ec2.run_instances(
                ImageId=original_instance['ImageId'],
                InstanceType=original_instance['InstanceType'],
                MaxCount=1,
                MinCount=1,
                SecurityGroupIds=[sg['GroupId'] for sg in original_instance['SecurityGroups']],
                SubnetId=original_instance['SubnetId'],
                Placement={
                    'AvailabilityZone': availability_zone
                },
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': f'Restored-{instance_id}-{datetime.now().strftime("%Y-%m-%d-%H-%M")}'
                            }
                        ]
                    }
                ]
            )
            
            new_instance_id = new_instance['Instances'][0]['InstanceId']
            print(f"Created new instance: {new_instance_id}")
            
            # Wait for instance to be running
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[new_instance_id])
            
            # Attach the volume to new instance using /dev/xvdf
            try:
                ec2.attach_volume(
                    Device='/dev/xvdf',  # Using a different device name
                    InstanceId=new_instance_id,
                    VolumeId=volume['VolumeId']
                )
                print(f"Attached volume {volume['VolumeId']} to instance {new_instance_id}")
            except Exception as e:
                print(f"Error attaching volume: {str(e)}")
                # If first attempt fails, try alternative device name
                try:
                    ec2.attach_volume(
                        Device='/dev/sdf',  # Alternative device name
                        InstanceId=new_instance_id,
                        VolumeId=volume['VolumeId']
                    )
                    print(f"Attached volume {volume['VolumeId']} to instance {new_instance_id} using alternative device name")
                except Exception as e2:
                    print(f"Error attaching volume with alternative name: {str(e2)}")
                    raise e2
            
            print(f"Successfully restored instance {instance_id} to new instance {new_instance_id}")
            
        return {
            'statusCode': 200,
            'body': 'Successfully restored instances from snapshots'
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error restoring instances: {str(e)}'
        }
