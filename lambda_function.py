import logging
import json
from certified_builder.certified_builder import CertifiedBuilder
from models.participant import Participant
from models.certificate import Certificate
from models.event import Event
from datetime import datetime
import base64
import os
from aws.s3_service import S3Service
from aws.sqs_service import SQSService

# Configure logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicate logs
for handler in logger.handlers:
    logger.removeHandler(handler)

# Add a StreamHandler for CloudWatch
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(handler)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        return super().default(obj)

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

def create_participant_object(participant_data):
    # Create Certificate object
    certificate = Certificate(
        details=participant_data.get('certificate_details'),
        logo=participant_data.get('certificate_logo'),
        background=participant_data.get('certificate_background')
    )
    
    # Create Event object
    event = Event(
        order_id=participant_data.get('order_id'),
        product_id=participant_data.get('product_id'),
        product_name=participant_data.get('product_name'),
        date=datetime.strptime(participant_data.get('order_date'), "%Y-%m-%d %H:%M:%S"),
        time_checkin=datetime.strptime(participant_data.get('time_checkin'), "%Y-%m-%d %H:%M:%S") if participant_data.get('time_checkin') else None,
        checkin_latitude=float(participant_data.get('checkin_latitude')) if participant_data.get('checkin_latitude') else None,
        checkin_longitude=float(participant_data.get('checkin_longitude')) if participant_data.get('checkin_longitude') else None
    )
    
    # Create Participant object
    participant = Participant(
        first_name=participant_data.get('first_name'),
        last_name=participant_data.get('last_name'),
        email=participant_data.get('email'),
        phone=participant_data.get('phone'),
        cpf=participant_data.get('cpf', ''),
        certificate=certificate,
        event=event
    )
    return participant

def format_result(result):
    if isinstance(result, dict):
        formatted = {}
        for key, value in result.items():
            if isinstance(value, (Participant, Certificate, Event)):
                formatted[key] = value.model_dump()
            elif isinstance(value, datetime):
                formatted[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted[key] = value
        return formatted
    return result

def lambda_handler(event, context):
    # Log the start of the Lambda execution
    try:

        logger.info("Starting Lambda execution")    
        body = extract_data_body(event)
        participants_data = body
        
        if not participants_data:
            logger.warning("No participants found in message")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No participants found in message',
                    'message': 'Nenhum participante encontrado para processamento'
                })
            }
        s3_service = S3Service()
        sqs_service = SQSService()

        logger.info(f"Processing {len(participants_data)} participants")
        
        # Create list of participants
        participants = []
        results = []
        
        for participant_data in participants_data:
            try:
                participant = create_participant_object(participant_data)
                participants.append(participant)
            except Exception as e:
                logger.error(f"Error creating participant object: {str(e)}")
                results.append({
                    'participant_data': participant_data,
                    'error': str(e),
                    'success': False
                })
        
        # Generate certificates if we have valid participants
        if participants:
            builder = CertifiedBuilder()
            certificates_results = builder.build_certificates(participants)
            # Format results before adding to response
            formatted_results = []
            
            for result in certificates_results:
                formatted_results.extend(format_result(result))            
                
                if result.get('success'):
                    s3_service.upload_file(result.get('certificate_path'), result.get('certificate_key'))
                
                sqs_service.send_message({
                    "order_id": result.get('participant', {}).get('event', {}).get('order_id', ""),
                    "product_id": result.get('participant', {}).get('event', {}).get('product_id', ""),
                    "product_name": result.get('participant', {}).get('event', {}).get('product_name', ""),
                    "email": result.get('participant', {}).get('email', ""),
                    "certificate_key": result.get('certificate_key', ""),
                    "success": result.get('success', False)
                })
            
            
            logger.info("Certificados gerados com sucesso")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Processamento concluído',
                    'results': results
                }, cls=DateTimeEncoder)
            }
        else:
            logger.warning("No valid participants to process")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No valid participants to process',
                    'message': 'Nenhum participante válido para processamento',
                    'results': results
                }, cls=DateTimeEncoder)
            }
            
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Erro ao gerar certificados'
            })
        }

if __name__ == "__main__":
    lambda_handler({
	"Records": [
		{
			"body": [
				{
					"order_id": 452,
					"first_name": "Jardel",
					"last_name": "Godinho",
					"email": "jardelgodinho@gmail.com",
					"phone": "(48) 98866-7447",
					"cpf": "",
					"city": "São José",
					"product_id": 316,
					"product_name": "Evento de Teste",
					"certificate_details": "In recognition of their participation in the 84st edition of the Python Floripa Community Meeting, held on March 29, 2025, in Florianópolis, Brazil.",
					"certificate_logo": "https://tech.floripa.br/wp-content/uploads/2025/03/84o-Python-Floripa-e1741729144453.png",
					"certificate_background": "https://tech.floripa.br/wp-content/uploads/2025/03/Background.png",
					"order_date": "2025-03-26 20:55:25",
					"checkin_latitude": "-27.5460492",
					"checkin_longitude": "-48.6227075",
					"time_checkin": "2025-03-26 20:55:44"
				},
				{
					"order_id": 317,
					"first_name": "Jardel",
					"last_name": "Godinho",
					"email": "jardel.godinho@gmail.com",
					"phone": "(48) 98866-7447",
					"cpf": "",
					"city": "",
					"product_id": 316,
					"product_name": "Evento de Teste",
					"certificate_details": "In recognition of their participation in the 84st edition of the Python Floripa Community Meeting, held on March 29, 2025, in Florianópolis, Brazil.",
					"certificate_logo": "https://tech.floripa.br/wp-content/uploads/2025/03/84o-Python-Floripa-e1741729144453.png",
					"certificate_background": "https://tech.floripa.br/wp-content/uploads/2025/03/Background.png",
					"order_date": "2025-03-19 06:04:51",
					"checkin_latitude": "-27.5460492",
					"checkin_longitude": "-48.6227075",
					"time_checkin": "2025-03-19 16:04:16"
				}
			]
		}
	]
}, {})