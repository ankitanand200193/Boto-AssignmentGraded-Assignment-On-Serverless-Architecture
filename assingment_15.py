import boto3
from datetime import datetime, timezone
import time

def get_date_from_filename(filename):
    try:
        # Extract date from filename format "log-YYYY-MM-DD.txt"
        date_str = filename.split('log-')[1].split('.txt')[0]
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        # If filename doesn't match expected format, return current date
        return datetime.now()

def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Specify your bucket name
    bucket_name = "demo-logs-cleanup-ankit-2025"  # Replace with your bucket name
    
    # Calculate the cutoff date (current date)
    current_date = datetime.now()
    
    # List all objects in the bucket
    try:
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in objects:
            print(f"No objects found in bucket {bucket_name}")
            return {
                'statusCode': 200,
                'body': 'No objects found to process'
            }
        
        # Counter for deleted files
        deleted_count = 0
        
        # Check each object's filename date
        for obj in objects['Contents']:
            filename = obj['Key']
            file_date = get_date_from_filename(filename)
            
            # If file date is from 2023, delete it
            if file_date.year < 2024:
                # Delete objects from 2023
                s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=obj['Key']
                )
                print(f"Deleted old log: {obj['Key']}")
                deleted_count += 1
            else:
                print(f"Keeping recent log: {obj['Key']}")
        
        return {
            'statusCode': 200,
            'body': f'Successfully processed logs. Deleted {deleted_count} old logs.'
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error processing logs: {str(e)}'
        }
