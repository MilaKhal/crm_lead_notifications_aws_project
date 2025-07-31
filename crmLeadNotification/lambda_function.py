import json
import datetime
import os
import urllib3
import boto3

# make sure to save SLACK_WEBHOOK_URL as an environment variable

s3 = boto3.client('s3')
http = urllib3.PoolManager()

def lambda_handler(event, context):

    # Get bucket and object key
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']


    # Only process files in the /target/ folder
    if not object_key.startswith("target/"):
        print("Skipping non-target file.")
        return

    # Get object content
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    data = json.loads(response['Body'].read().decode('utf-8'))
    
    # Extract details
    lead_id = data['lead_id']
    lead_owner = data['lead_owner']
    created_date = datetime.datetime.fromisoformat(data['date_created'].replace('Z', '+00:00'))
    status_label = data['status_label']
    funnel = data['funnel']
    email = data['lead_email']

    # Slack message
    slack_message = {
        "text": f"""
            🚨 *New Lead Alert!*
            *Lead ID:* {lead_id}
            *Created:* {created_date.strftime('%Y-%m-%d %H:%M:%S')}
            *Owner:* {lead_owner}
            *Status:* {status_label}
            *Funnel:* {funnel}
            *Email*: {email}
        """
    }
    print(f"Slack Message: {slack_message}")

    # Send to Slack
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    response = http.request(
        'POST',
        webhook_url,
        body=json.dumps(slack_message).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    print(f"Slack notification sent. Status: {response.status}")
    print("Slack response body:", response.data.decode('utf-8'))
