import boto3
import os

AWS_REGION = "ap-southeast-1"
SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-1:<ACCOUNT#>:scheduler-stop-tagged-ec2-rds"

ec2 = boto3.client('ec2', region_name=AWS_REGION)
rds = boto3.client('rds', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)

def lambda_handler(event, context):
    summary_list = []

    # ========== EC2 SECTION ==========
    print(" Checking EC2 instances with tag Scheduler-Stop-Start=YES...")

    ec2_response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Scheduler-Stop-Start', 'Values': ['YES']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    for reservation in ec2_response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name_tag = "<No Name>"
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name_tag = tag['Value']
            print(f" Stopping EC2: {name_tag} ({instance_id})")
            ec2.stop_instances(InstanceIds=[instance_id])
            summary_list.append(f"EC2    : {name_tag}")

    # ========== RDS SECTION ==========
    print(" Checking RDS instances with tag Scheduler-Stop-Start=YES...")

    rds_instances = rds.describe_db_instances()
    for db in rds_instances['DBInstances']:
        db_id = db['DBInstanceIdentifier']
        db_arn = db['DBInstanceArn']

        tag_response = rds.list_tags_for_resource(ResourceName=db_arn)
        tag_value = next((tag['Value'] for tag in tag_response['TagList'] if tag['Key'] == 'Scheduler-Stop-Start'), None)

        if tag_value == 'YES' and db['DBInstanceStatus'] == 'available':
            print(f" Stopping RDS: {db_id}")
            rds.stop_db_instance(DBInstanceIdentifier=db_id)
            summary_list.append(f"RDS    : {db_id}")

    # ========== SUMMARY REPORT ==========
    print("\n📋 Summary Report")
    if not summary_list:
        summary = "No EC2 or RDS instances were stopped."
    else:
        summary_lines = "\n".join(f"- {line}" for line in summary_list)
        summary = f" Stopped the following resources as per schedule 7PM :\n{summary_lines}"

    print(summary)

    # ========== SEND SNS ==========
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Scheduled Stop Report - DEV EC2 & RDS",
            Message=summary
        )
        print("📨 SNS notification sent.")
    except Exception as e:
        print(f" Failed to send SNS notification: {str(e)}")

    return {
        'statusCode': 200,
        'body': summary

    }
