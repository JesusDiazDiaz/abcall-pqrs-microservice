import json
import logging

import boto3

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:044162189377:AbcallPqrsTopic'

sqs = boto3.client('sqs')
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/044162189377/AbcallPqrs'

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')


class Dispatcher:
    def _publish_message(self, message) -> None:
        LOGGER.info("publish message to sns")
        # sns.publish(
        #     TopicArn=SNS_TOPIC_ARN,
        #     Message=str(json.dumps(message)),
        #     Subject='New PQRS Incident'
        # )
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

    def publish_command(self, command) -> None:
        self._publish_message(command)