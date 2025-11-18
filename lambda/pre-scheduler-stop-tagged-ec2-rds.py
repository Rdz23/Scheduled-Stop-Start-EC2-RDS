import boto3
import os

AWS_REGION = "ap-southeast-1"
SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-1:<ACCOUNT#>:scheduler-stop-tagged-ec2-rds"

ec2 = boto3.client('ec2', region_name=AWS_REGION)
rds = boto3.client('rds', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)

def lambda_handler(event, context):
    summary_list = ["This is a pre-stop reminder. The following resources are scheduled to be stopped in 1 hour:\n"]

    # === EC2 Section ===
    ec2_response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Scheduler-Stop-Start', 'Values': ['YES']},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
        ]
    )

    for reservation in ec2_response['Reservations']:
        for instance in reservation['Instances']:
            name_tag = "<No Name>"
            state = instance['State']['Name']  # e.g., "running", "stopped"

            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name_tag = tag['Value']

            if state == "running":
                summary_list.append(f"EC2    : {name_tag}")
            else:
                summary_list.append(f"EC2    : {name_tag}  [Currently Down - {state}]")

    # === RDS Section ===
    rds_instances = rds.describe_db_instances()
    for db in rds_instances['DBInstances']:
        db_id = db['DBInstanceIdentifier']
        db_arn = db['DBInstanceArn']

        tags = rds.list_tags_for_resource(ResourceName=db_arn)['TagList']
        tag_value = next((t['Value'] for t in tags if t['Key'] == 'Scheduler-Stop-Start'), None)

        if tag_value == 'YES':
            db_status = db['DBInstanceStatus']
            if db_status == 'available':
                summary_list.append(f"RDS    : {db_id}")
            else:
                summary_list.append(f"RDS    : {db_id}  [Currently Down - {db_status}]")

    # === Send SNS ===
    message = "\n".join(summary_list)
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Scheduled Stop Reminder - EC2 & RDS (1 Hour Notice)",
            Message=message
        )
        print("SNS notification sent successfully.")
    except Exception as e:
        print(f"Error sending SNS notification: {e}")

    return {
        'statusCode': 200,
        'body': message
    }
