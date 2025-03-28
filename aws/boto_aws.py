from boto3 import client
from enum import Enum
from config import config

class ServiceNameAWS(Enum):
    S3 = 's3'
    SQS = 'sqs'

def get_instance_aws(service_name: ServiceNameAWS):
    return client(
        service_name.value,
        region_name=config.REGION,
        aws_access_key_id=config.KEY_ACCESS,
        aws_secret_access_key=config.KEY_SECRET
    )
