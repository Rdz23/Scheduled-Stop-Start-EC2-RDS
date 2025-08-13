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
<img width="856" height="230" alt="image" src="https://github.com/user-attachments/assets/9a335f6a-9600-42be-82ff-f34c0b1f658e" />

## Schedule  (Monday to Friday)
<img width="1081" height="387" alt="image" src="https://github.com/user-attachments/assets/ee3ea938-1918-4762-9c80-968907545f88" />
Cron schedules are defined in EventBridge rules. 
Each Lambda function is triggered at the specified times.
Resources are selected based on the tag: Scheduler-Stop-Start=YES.

## Deployment
1. Prerequisites
AWS CLI configured with admin or deployment role.
Permissions to create Lambda, EventBridge rules, SNS topics, and IAM roles.
S3 bucket for Lambda deployment packages.

2. Setup Steps
Clone Repository

git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>



