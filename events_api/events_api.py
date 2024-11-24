from typing import List
from .models.participant import Participant

from PIL import Image
from io import BytesIO

import httpx

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