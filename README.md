# AWS Stop/Start Scheduler – DEV & QA EC2/RDS

## Overview
This project automates **scheduled start/stop of tagged EC2 and RDS instances** in AWS **DEV** and **QA** environments to reduce costs during non-working hours.  
It uses **AWS Lambda**, **Amazon EventBridge**, and **Amazon SNS** for orchestration, notifications, and execution.

## Features
The Scheduler Stop/Start mechanism automates EC2 and RDS instance lifecycle management for DEV and QA environments based on tag-based filtering.
Helps reduce costs by turning off non-critical workloads after business hours.
Tag-driven logic ensures flexibility and control per resource.
Tag used for control:
Scheduler-Stop-Start=YES

## Architecture
<img width="656" height="130" alt="image" src="https://github.com/user-attachments/assets/9a335f6a-9600-42be-82ff-f34c0b1f658e" />

## Schedule  (Monday to Friday)
<img width="881" height="187" alt="image" src="https://github.com/user-attachments/assets/ee3ea938-1918-4762-9c80-968907545f88" />
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

 4. IAM Policy Example

   
 5. Testing
    Dry-run: Modify Lambda to log resource IDs instead of stopping them.
    Tag test resources and trigger EventBridge manually.
    Verify SNS notification email delivery.

  6. Back-out Plan
       Disable all EventBridge rules:
       aws events disable-rule --name scheduler-stop-tagged-event-rule
       aws events disable-rule --name scheduler-start-tagged-event-rule
       aws events disable-rule --name pre-scheduler-stop-tagged-event-rule

  7. Notifications
      SNS subject lines:
     Scheduled Stop Alerts - DEV EC2 & RDS (pre-stop)
     Scheduled Stop Report - DEV EC2 & RDS (post-stop)

    


