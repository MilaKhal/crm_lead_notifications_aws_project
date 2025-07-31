import json
import boto3
import urllib.request

s3 = boto3.client('s3')

SOURCE_BUCKET = 'de-crm-project'
PUBLIC_BUCKET = 'dea-lead-owner'
TARGET_PREFIX = 'target/'

def lambda_handler(event, context):
    try:
        # SQS event can contain multiple messages, loop through all
        for record in event['Records']:
            # SQS message body is a JSON string of the original webhook event
            body = json.loads(record['body'])

            # Extract lead_id from the webhook event message body
            lead_id = (
                body.get("lead_id") or
                body.get("event", {}).get("lead_id") or
                (body.get("events", [{}])[0].get("lead_id") if isinstance(body.get("events"), list) else None)
            )
            if not lead_id:
                print("lead_id not found in SQS message, skipping record")
                continue

            # Construct the key to the source file where first Lambda saved raw event
            source_key = f"source/crm_event_{lead_id}.json"

            # Get the source file from S3 (raw event)
            source_obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=source_key)
            lead_data = json.loads(source_obj['Body'].read().decode('utf-8'))

            # Fetch the public lead owner JSON from public bucket URL
            public_url = f"https://{PUBLIC_BUCKET}.s3.us-east-1.amazonaws.com/{lead_id}.json"
            with urllib.request.urlopen(public_url) as response:
                owner_data = json.loads(response.read().decode('utf-8'))

            # Merge datasets - owner_data fields overwrite lead_data on key conflicts
            merged_data = {**lead_data, **owner_data}

            # Write merged data to target folder
            target_key = f"{TARGET_PREFIX}merged_{lead_id}.json"
            s3.put_object(
                Bucket=SOURCE_BUCKET,
                Key=target_key,
                Body=json.dumps(merged_data),
                ContentType='application/json'
            )
            print(f"Merged lead data saved to {target_key}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Processed all records successfully"})
        }

    except Exception as e:
        print(f"Error processing records: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
