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
    certified_builder = CertifiedBuilder(EventsAPI())
    
    certified_builder.build_certificates()
    
    logger.info("Certificados gerados com sucesso")
    
except Exception as e:
    logger.error(f"Erro ao gerar certificados: {str(e)}", exc_info=True)
    raise