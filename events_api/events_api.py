import logging
from typing import List
from .models.participant import Participant

from PIL import Image
from io import BytesIO

import httpx

logger = logging.getLogger(__name__)

class EventsAPI:
    list_participants: List[Participant] = []
    
    def __init__(self, ):
        pass 
    
    def fetch_participants(self, ) -> List[Participant]:
        url_participants = "https://python.floripa.br/wp-json/custom/v1/event_checkin"
        response = httpx.get(url_participants)        
        data = response.json()        
        for item in data:            
            self.list_participants.append(Participant(**item))        
        return self.list_participants
    
    def fetch_file_certificate(self, ) -> Image:
        url_certificate= "https://python.floripa.br/wp-content/uploads/2024/11/Background.png"
        response = httpx.get(url_certificate)
        img = Image.open(BytesIO(response.content))
        img.save("certificate_models.png")
        return img
    
    
    def save_certificate(self, image_buffer: BytesIO, participant: Participant):        
        try:
            url_save_certificate = "https://python.floripa.br/wp-json/event/v1/upload"
            data = {
                "validation_code": participant.validation_code,
                "first_name": participant.first_name,
                "last_name": participant.last_name,
                "email": participant.email,
                "event_id": participant.details[0].event_id,
                "event_date": participant.details[0].last_checkin,
            }
            name_image = participant.name_completed() + "_" + data["event_id"] + "_" + data["event_date"] + "_" + data["validation_code"] + ".png"
            files = {
                "certificate_image": (
                    name_image, image_buffer, "image/png"
                )
            }
            
            max_retries = 3
            attempt = 0
            while attempt < max_retries:
                try:
                    response = httpx.post(url_save_certificate, data=data, files=files)
                    logger.info(f"Response status code: {response.status_code}")
                    if response.status_code == 200:
                        logger.info(f"Certificate saved for {participant.first_name} {participant.last_name} ({participant.email})")
                        break

                    logger.error(f"Error saving certificate for {participant.first_name} {participant.last_name} ({participant.email}): {response.text}")
                    raise Exception(response.json()['message'])

                except Exception as e:
                    attempt += 1
                    logger.error(f"Error saving certificate for {participant.first_name} {participant.last_name} ({participant.email}): {e}")
                    if attempt == max_retries:
                        logger.error(f"Max retries reached for {participant.first_name} {participant.last_name} ({participant.email})")
                        raise
        
        except Exception as e:
            logger.error(f"Error saving certificate for {participant.first_name} {participant.last_name} ({participant.email}): {e}")
            raise