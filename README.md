# AWS Stop/Start Scheduler – DEV & QA EC2/RDS

## Overview
This project automates **scheduled start/stop of tagged EC2 and RDS instances** in AWS **DEV** and **QA** environments to reduce costs during non-working hours. It uses **AWS Lambda**, **Amazon EventBridge**, and **Amazon SNS** for orchestration, notifications, and execution.

## Features
The Scheduler Stop/Start mechanism automates EC2 and RDS instance lifecycle management for DEV and QA environments based on tag-based filtering.
Helps reduce costs by turning off non-critical workloads after business hours.
Tag-driven logic ensures flexibility and control per resource.
Tag used for control:
Scheduler-Stop-Start=YES

## Architecture
<img width="656" height="130" alt="image" src="https://github.com/user-attachments/assets/9a335f6a-9600-42be-82ff-f34c0b1f658e" />

## Schedule  (Monday to Friday)
<img width="881" height="187" alt="image" src="https://github.com/user-attachments/assets/ee3ea938-1918-4762-9c80-968907545f88" />  \
Cron schedules are defined in EventBridge rules. 
Each Lambda function is triggered at the specified times.
Resources are selected based on the tag: Scheduler-Stop-Start=YES.

## Deployment
1. Prerequisites
AWS CLI configured with admin or deployment role.
Permissions to create Lambda, EventBridge rules, SNS topics, and IAM roles.
S3 bucket for Lambda deployment packages.

2. Setup Steps
   A. Clone Repository

      git clone https://github.com/<your-org>/<your-repo>.git
      cd <your-repo>

   B. Create IAM Role and Policy
      Attach the customer-managed policy with EC2, RDS, and SNS permissions.
      Trust relationship: lambda.amazonaws.com.

   C. Deploy Lambda Functions
      zip -r scheduler-start.zip start_lambda/
      aws lambda create-function --function-name scheduler-start-tagged-ec2-rds \
    --zip-file fileb://scheduler-start.zip \
    --handler lambda_function.lambda_handler \
    --runtime python3.13 \
    --role arn:aws:iam::<account-id>:role/<lambda-role>

     Repeat for:
       pre-scheduler-stop-tagged-ec2-rds
       scheduler-stop-tagged-ec2-rds

   D. Configure EventBridge Rules
       aws events put-rule \
       --name scheduler-stop-tagged-event-rule \
       --description "Stop tagged EC2/RDS - Mon-Fri at 7PM GMT+8" \
       --schedule-expression "cron(0 11 ? * MON-FRI *)"

   E. Subscribe SNS Recipients
      aws sns subscribe \
      --topic-arn arn:aws:sns:ap-southeast-1:<account-id>:scheduler-stop-tagged-ec2-rds \
      --protocol email \
      --notification-endpoint you@example.com

 3. IAM Policy Example

   
 4. Testing
    Dry-run: Modify Lambda to log resource IDs instead of stopping them.
    Tag test resources and trigger EventBridge manually.
    Verify SNS notification email delivery.

 5. Back-out Plan
       Disable all EventBridge rules:
       aws events disable-rule --name scheduler-stop-tagged-event-rule
       aws events disable-rule --name scheduler-start-tagged-event-rule
       aws events disable-rule --name pre-scheduler-stop-tagged-event-rule

 6. Notifications
      SNS subject lines:
     Scheduled Stop Alerts - DEV EC2 & RDS (pre-stop)
     Scheduled Stop Report - DEV EC2 & RDS (post-stop)

 ## Manual Procedure – Stop Non-Prod EC2 & RDS  
    **EC2 Stop Procedure**
      1. Log in to the AWS console using your IAM account
      2. Navigate using the search bar, or directly via:
      3. EC2 Instances → EC2 | Instances | ap-southeast-1
      4. Search for the non-prod instance name (e.g., tEST-Instance).
      5. Select the instance by ticking the checkbox.
      6. Open the Instance State dropdown → Stop Instance.
      7. Click Stop.

    **RDS Stop Procedure**
       1. Navigate to  Databases → Aurora and RDS | ap-southeast-1
       2. Select the target RDS instance.
       3. Open Actions → Stop temporarily

 ## Manual Procedure – Start Non-Prod EC2 & RDS  
     **EC2 Start Procedure**
       1. Log in to AWS console using your IAM account.
       2. Navigate to:
           EC2 Instances → EC2 | Instances | ap-southeast-1
       3. Search for the non-prod instance (e.g., TEST-Instance)
       4. Tick the checkbox to select the instance.
       5. Open the Instance State dropdown → Start Instance
       6. Click "Start"

## Permissions & Guardrails
   Ensure all Production servers are configured with appropriate protections.
   API Protection Settings:

   --no-disable-api-stop       (Enable API Stop protection)
   --enable-api-termination    (Enable Termination protection)

A dedicated IAM policy/group will be used to control non-prod access, e.g.:
   NON-PROD_EC2-RDS-START-STOP
