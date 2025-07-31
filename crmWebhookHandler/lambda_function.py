import json
import boto3

sqs = boto3.client('sqs')
s3 = boto3.client('s3')

QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/921746223461/crm-delay-queue'
BUCKET_NAME = "de-crm-project"

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        lead_id = body.get("lead_id")
        if not lead_id:
            if "event" in body and isinstance(body["event"], dict):
                lead_id = body["event"].get("lead_id")
            elif "events" in body and isinstance(body["events"], list):
                for evt in body["events"]:
                    if isinstance(evt, dict) and "lead_id" in evt:
                        lead_id = evt["lead_id"]
                        break

        if not lead_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing lead_id in payload"})
            }

        filename = f"crm_event_{lead_id}"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f'source/{filename}.json',
            Body=json.dumps(body).encode('utf-8'),
            ContentType='application/json'
        )

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(body),
            DelaySeconds=600  # Delay for 10 minutes
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook received, saved, and queued with delay'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
