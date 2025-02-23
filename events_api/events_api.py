import json
import logging
import os
from typing import List
from .models.participant import Participant

from PIL import Image
from io import BytesIO

import httpx

logger = logging.getLogger(__name__)

class EventsAPI:
    list_participants: List[Participant] = []
    url_file_certificate: str = ""
    
    def __init__(self,  url_file_certificate: str,   event_start:str , event_end:str ) -> None:
        self.url_file_certificate = url_file_certificate
        self.event_start = event_start
        self.event_end = event_end        
    
    def fetch_participants(self) -> List[Participant]:
        url_participants = "https://python.floripa.br/wp-json/custom/v1/event_checkin"
        response = httpx.get(url_participants)        
        data = response.json()        
        
        logger.info(f"Total de participantes recebidos: {len(data)}")
        for item in data:                        
            participant_new = Participant(**item)
            participant_new.filter_last_checkin(self.event_start, self.event_end)
            
            if participant_new.details.__len__() > 0 and participant_new.details[0].event_id != '':
                logger.info(
                    participant_new
                )
                self.list_participants.append(participant_new)        

        logger.info(f"Total de participantes filtrados: {len(self.list_participants)}")        
        return self.list_participants
    
    def fetch_file_certificate(self,) -> Image:
        url_certificate= self.url_file_certificate
        response = httpx.get(url_certificate)
        img = Image.open(BytesIO(response.content))
        img.save("certificate_models.png")
        return img
    
    
    def exist_sendinblue(self, name_certificate: str) -> bool:
        # Verifica se o certificado já foi enviado para o Sendinblue        
        if not os.path.exists("sendinblue_status.json"):
            with open("sendinblue_status.json", "w") as file:
                json.dump({}, file)
        with open("sendinblue_status.json", "r") as file:
            data = json.load(file)
        return data.get(name_certificate, False)
    
    def save_status_sendinblue(self, name_certificate: str) -> None:
        # Salva o status de envio do certificado no Sendinblue, salvando os dados em um arquivo
        if not os.path.exists("sendinblue_status.json"):
            with open("sendinblue_status.json", "w") as file:
                json.dump({}, file)
        with open("sendinblue_status.json", "r") as file:
            data = json.load(file)
        data[name_certificate] = True
        with open("sendinblue_status.json", "w") as file:
            json.dump(data, file)

    

        
    def save_certificate(self, image_buffer: BytesIO, participant: Participant, name_certificate: str) -> None:    
        if self.exist_sendinblue(name_certificate):
                logger.info(f"Certificate already sent for {participant.first_name} {participant.last_name} ({participant.email})")
                return
        try:
            if self.exist_sendinblue(name_certificate):
                logger.info(f"Certificate already sent for {participant.first_name} {participant.last_name} ({participant.email})")
                return
            url_save_certificate = "https://python.floripa.br/wp-json/event/v1/upload"
            data = {
                "validation_code": participant.validation_code,
                "first_name": participant.first_name,
                "last_name": participant.last_name,
                "email": participant.email,
                "event_id": participant.details[0].event_id,
                "event_date": participant.details[0].last_checkin,
            }
            name_image = name_certificate
            files = {
                "certificate_image": (
                    name_image, image_buffer, "image/png"
                )
            }
            
            max_retries = 3
            attempt = 0
            while attempt < max_retries:
                try:
                    response = httpx.post(url_save_certificate, data=data, files=files, timeout=30)
                    logger.info(f"Response status code: {response.status_code}")
                    if response.status_code == 200:
                        logger.info(f"Certificate saved for {participant.first_name} {participant.last_name} ({participant.email})")
                        self.save_status_sendinblue(name_certificate)
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