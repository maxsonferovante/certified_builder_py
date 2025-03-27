import logging
import json
from certified_builder.certified_builder import CertifiedBuilder
from models.participant import Participant
from models.certificate import Certificate
from models.event import Event
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


def extract_data_body(event):
    try:        
        logger.info("Event recebido : {}".format(event))
        record = event['Records'][0]
        if isinstance(record['body'], str):
            body = json.loads(record['body'])
            return body
        else:
            return record['body']
    except Exception as e:
        logger.error(f"Erro ao extrair dados do body: {str(e)}", exc_info=True)
        raise

def create_participants_list(data):
    participants = []
    for item in data:
        # Create certificate object if certificate details exist
        certificate = None
        if 'certificate_details' in item and 'certificate_logo' in item and 'certificate_background' in item:
            certificate = Certificate(
                details=item['certificate_details'],
                logo=item['certificate_logo'],
                background=item['certificate_background']
            )

        # Create event object
        event = None
        if all(key in item for key in ['order_id', 'product_id', 'product_name', 'order_date', 'time_checkin', 'checkin_latitude', 'checkin_longitude']):
            event = Event(
                order_id=item['order_id'],
                product_id=item['product_id'],
                product_name=item['product_name'],
                date=datetime.strptime(item['order_date'], '%Y-%m-%d %H:%M:%S'),
                time_checkin=datetime.strptime(item['time_checkin'], '%Y-%m-%d %H:%M:%S'),
                checkin_latitude=float(item['checkin_latitude']) if item['checkin_latitude'] else 0.0,
                checkin_longitude=float(item['checkin_longitude']) if item['checkin_longitude'] else 0.0
            )

        participant = Participant(
            first_name=item['first_name'],
            last_name=item['last_name'],
            email=item['email'],
            phone=item['phone'],
            cpf=item['cpf'],
            certificate=certificate,
            event=event
        )
        participants.append(participant)
    return participants

def lambda_handler(event, context):
    body = extract_data_body(event)
    participants_data = body['participants']  # New field expected in the body    
    try:
        logger.info("Iniciando geração de certificados")
        
        # Create list of participants
        participants = create_participants_list(participants_data)
        logger.info(f"Created {len(participants)} participants")
        
                
        certified_builder = CertifiedBuilder()
        
        certified_builder.build_certificates(participants)
        
        logger.info("Certificados gerados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao gerar certificados: {str(e)}", exc_info=True)
        raise

