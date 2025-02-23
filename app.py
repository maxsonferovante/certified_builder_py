import logging

from events_api.events_api import EventsAPI

from certified_builder.certified_builder import CertifiedBuilder


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('certificates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando geração de certificados")
    
    events_api = EventsAPI(url_file_certificate='https://python.floripa.br/wp-content/uploads/2025/02/83st-edition-of-the-Python-Floripa-Community-Meeting.png', 
                           event_start='2025-02-22 13:29:00', event_end='2025-02-22 18:30:00')

    
    certified_builder = CertifiedBuilder(events_api=events_api)
    
    certified_builder.build_certificates()
    
    logger.info("Certificados gerados com sucesso")
    
except Exception as e:
    logger.error(f"Erro ao gerar certificados: {str(e)}", exc_info=True)
    raise