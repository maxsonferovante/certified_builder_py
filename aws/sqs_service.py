from aws.boto_aws import get_instance_aws, ServiceNameAWS
from config import config
from typing import Dict
import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class SQSService:
    def __init__(self):
        self.aws = get_instance_aws(ServiceNameAWS.SQS)
        self.queue_url = config.QUEUE_URL        

    def send_message(self, message: Dict):
        try:
            # Add MessageGroupId for FIFO queue
            # Using order_id as MessageGroupId to ensure messages for the same order are processed in order
            message_group_id = str(message.get('order_id', 'default'))
            
            response = self.aws.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
                MessageGroupId=message_group_id,
                MessageDeduplicationId=f"{message_group_id}_{message.get('email', '')}"  # Ensure unique messages per order/email
            )
            logger.info(f"Mensagem enviada com sucesso: {response['MessageId']}")
            return response
        except ClientError as e:
            logger.error(f"Erro ao enviar mensagem para a fila {self.queue_url}: {str(e)}")
            raise
