import logging
import json
from events_api.events_api import EventsAPI
from certified_builder.certified_builder import CertifiedBuilder

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





""" url_file_certificate='https://python.floripa.br/wp-content/uploads/2025/02/83st-edition-of-the-Python-Floripa-Community-Meeting.png', 
                            event_start='2025-02-22 13:29:00', event_end='2025-02-22 18:30:00' """
def lambda_handler(event, context):
    body = extract_data_body(event)
    url_file_certificate = body['url_file_certificate']
    event_start = body['event_start']
    event_end = body['event_end']
    try:
        logger.info("Iniciando geração de certificados")
        
        events_api = EventsAPI(
            url_file_certificate=url_file_certificate,
            event_start=event_start,
            event_end=event_end
        )
                
        certified_builder = CertifiedBuilder(events_api=events_api)
        
        certified_builder.build_certificates()
        
        logger.info("Certificados gerados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao gerar certificados: {str(e)}", exc_info=True)
        raise

