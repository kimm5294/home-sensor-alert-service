from flask import Flask, request, jsonify
from dotenv import load_dotenv
import boto3
import json
import os
import time

load_dotenv()
app = Flask(__name__)

AWS_REGION = os.getenv("AWS_REGION")
SQS_ALERTS_URL = os.getenv("SQS_ALERTS_URL")
SNS_ARN = os.getenv("SNS_ARN")

if not AWS_REGION or not SQS_ALERTS_URL or not SNS_ARN:
    raise ValueError("Missing required environment variables")

sqs = boto3.client('sqs', region_name=AWS_REGION)
SQS_URL = SQS_ALERTS_URL
sns = boto3.client('sns', region_name=AWS_REGION)

print("Alert service started. Listening for messages...")

while True:
    event = sqs.receive_message(
        QueueUrl=SQS_ALERTS_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=10
    )

    messages = event.get('Messages', [])

    for msg in messages:
        try:
            data = json.loads(msg["Body"])

            alert = f"Home Security Alert! Sensor: {data['sensor_name']}, Event: {data['event']}, Time: {time.ctime(data['timestamp'])}"

            sns.publish(
                TopicArn=SNS_ARN,
                Subject="Home Security Alert",
                Message=alert
            )

            sqs.delete_message(
                QueueUrl=SQS_ALERTS_URL,
                ReceiptHandle=msg["ReceiptHandle"]
            )

        except Exception as e:
            print("Error sending alert:", e)
