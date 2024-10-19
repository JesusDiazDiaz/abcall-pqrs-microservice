import logging

import boto3

sns = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:044162189377:AbcallPqrsTopic'

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')


class Dispatcher:
    def _publish_message(self, message) -> None:
        LOGGER.info("publish message to sns")
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=str(message),
            Subject='New PQRS Incident'
        )

    def publish_command(self, command) -> None:
        self._publish_message(command)