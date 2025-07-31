# Salesforce Lead Notification Pipeline

## Overview

This project is designed to **timely notify Salesforce team members** about lead events using AWS Lambda and other AWS services in a serverless architecture.

The system listens for lead events sent from a CRM webhook, delays processing to ensure accurate lead ownership, enriches data from a public source, and finally sends a formatted lead notification to Slack.

## Architecture

The system consists of three AWS Lambda functions, each responsible for a different stage of the lead notification pipeline:

### 1. `crmWebhookHandler`
- **Trigger**: CRM webhook posts event to the source S3 bucket.
- **Responsibility**: When a JSON lead event is saved to the source bucket, this function sends a message to an Amazon SQS queue with a **10-minute delay** to allow time for lead ownership assignment in external systems.

### 2. `crmLeadEnrichmentHandler`
- **Trigger**: Receipt of a message from the SQS queue.
- **Responsibility**: Reads the lead event from the source S3 bucket, **enriches** it with lead owner data from a **public S3 bucket**, and saves the enriched file to a **target folder** in another S3 bucket.

### 3. `crmLeadNotification`
- **Trigger**: Creation of an object in the **target folder** (S3 event).
- **Responsibility**: Reads the enriched lead JSON and generates a **Slack notification message** with relevant lead details for the Salesforce team:
- <img width="730" height="533" alt="image" src="https://github.com/user-attachments/assets/38fd039e-91e3-4a8d-ab41-4e23fe490236" />


## AWS Services Used
-**Amazon API Gateway** – Receives POST requests from the CRM webhook and triggers the crmWebhookHandler Lambda function
- **AWS Lambda** – Event-driven compute for all processing stages
- **Amazon S3** – Source and target buckets for event and enriched files
- **Amazon SQS** – Delayed messaging for lead processing
- **Slack Webhook** – For final lead notifications

## Folder Structure

crm_lead_notifications_aws_project/
├── crmWebhookHandler
│ ├── lambda_function.py
│ ├── requirements.txt
│ └── buildspec.yml
│
├── crmLeadEnrichmentHandler
│ ├── lambda_function.py
│ ├── requirements.txt
│ └── buildspec.yml
│
├── crmLeadNotification
│ ├── lambda_function.py
│ ├── requirements.txt
│ └── buildspec.yml

## Setup & Deployment

Each Lambda function is set up independently and may be deployed using AWS CodePipeline, CodeBuild, or via manual packaging. `requirements.txt` files include any necessary external Python dependencies (e.g., `urllib3`).
