import boto3

REGION = "ap-southeast-1"
SNS_ARN = "arn:aws:sns:ap-southeast-1:665634427675:scheduler-start-tagged-ec2-rds"

ec2 = boto3.client('ec2', region_name=REGION)
rds = boto3.client('rds', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

def lambda_handler(event, context):
    summary = []

    # EC2: Find and start tagged EC2 instances
    ec2_response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Scheduler-Stop-Start", "Values": ["YES"]},
            {"Name": "instance-state-name", "Values": ["stopped"]}
        ]
    )

    for reservation in ec2_response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), "<No Name>")
            print(f" Starting EC2: {name_tag} ({instance_id})")
            ec2.start_instances(InstanceIds=[instance_id])
            summary.append(f"EC2    : {name_tag} ({instance_id})")

    # RDS: Find and start tagged RDS instances
    rds_instances = rds.describe_db_instances()['DBInstances']

    for db in rds_instances:
        db_id = db['DBInstanceIdentifier']
        status = db['DBInstanceStatus']
        arn = db['DBInstanceArn']

        tag_list = rds.list_tags_for_resource(ResourceName=arn)['TagList']
        tag_value = next((tag['Value'] for tag in tag_list if tag['Key'] == 'Scheduler-Stop-Start'), None)

        if tag_value == 'YES' and status == 'stopped':
            print(f"Starting RDS: {db_id}")
            rds.start_db_instance(DBInstanceIdentifier=db_id)
            summary.append(f"RDS    : {db_id}")

    # SNS Notification
    if summary:
        report = "\n".join([f"  - {line}" for line in summary])
        message = f"Started the following resources as per schedule at 5AM :\n{report}"
    else:
        message = f"ℹNo tagged EC2 or RDS instances were started in region {REGION}."

    print("Sending SNS Notification...")
    sns.publish(
        TopicArn=SNS_ARN,
        Subject="Scheduled Start Report - DEV EC2 & RDS",
        Message=message
    )

    return {"statusCode": 200, "body": message}