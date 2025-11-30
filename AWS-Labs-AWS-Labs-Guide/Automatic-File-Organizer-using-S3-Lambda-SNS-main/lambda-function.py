import boto3
import os

s3 = boto3.client('s3')
sns = boto3.client('sns')

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:FileOrganizerNotifications"

FOLDER_MAP = {
    'images': ['.jpg', '.jpeg', '.png', '.gif'],
    'pdfs': ['.pdf'],
    'logs': ['.log', '.txt'],
}

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    if '/' in key:  # Skip if already inside a folder
        return {'status': 'File already organized'}
    
    file_ext = os.path.splitext(key)[1].lower()
    folder = 'others'
    
    for f, exts in FOLDER_MAP.items():
        if file_ext in exts:
            folder = f
            break
    
    new_key = f"{folder}/{key}"
    
    # Copy to new folder
    s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=new_key)
    
    # Delete original
    s3.delete_object(Bucket=bucket, Key=key)
    
    # Send SNS notification
    message = f"File '{key}' has been organized into folder '{folder}' in bucket '{bucket}'."
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="S3 File Organized Notification"
    )
    
    return {'status': f'File moved to {new_key} and notification sent'}
