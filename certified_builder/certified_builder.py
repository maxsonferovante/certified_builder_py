import logging
from events_api.events_api import EventsAPI
from events_api.models.participant import Participant

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

FONT_NAME="certified_builder/fonts/PinyonScript/PinyonScript-Regular.ttf"
VALIDATION_CODE="certified_builder/fonts/ChakraPetch/ChakraPetch-SemiBold.ttf"

logger = logging.getLogger(__name__)

class CertifiedBuilder:
    def __init__(self, events_api: EventsAPI):
        self.events_api = events_api

    def exist(self, name_participant: str):
        for name in os.listdir("certificates"):
            if name_participant.replace(" ", "_") in name:
                return True
        return False

    def build_certificates(self):
        participants = self.events_api.fetch_participants()
        # Fetch certificate template par o participante atual e o evento para o qual ele está inscrito
        certificate_template = self.events_api.fetch_file_certificate()
        
        for participant in participants:
            if not self.exist(participant.name_completed()):
                certificate_generated = self.generate_certificate(participant, certificate_template.copy())            
                self.save_certificate(certificate_generated, participant)
                logger.info(f"Certificado gerado para {participant.name_completed()} com codigo de validação {participant.formated_validation_code()}")
            else:
                logger.info(f"Certificado já gerado para {participant.name_completed()}")

    def generate_certificate(self, participant: Participant, certificate_template: Image):        
        name_image = self.create_name_image(participant.name_completed(), certificate_template.size)        
        validation_code_image = self.create_validation_code_image(participant.formated_validation_code(), certificate_template.size)        
        name_image.paste(validation_code_image, (0, 0), validation_code_image)
        certificate_template.paste(name_image, (0, 0), name_image)        
        return certificate_template

    def create_name_image(self, name: str, size: tuple) -> Image:
        name_image = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(name_image)
        font = ImageFont.truetype(FONT_NAME, 70)
        position = self.calculate_text_position(name, font, draw, size)
        draw.text(position, name, fill=(0, 0, 0), align="center", font=font)
        return name_image

    def calculate_text_position(self, text: str, font: ImageFont, draw: ImageDraw, size: tuple) -> tuple:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
        return position


    def create_validation_code_image(self, validation_code: str, size: tuple) -> Image:
        validation_code_image = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(validation_code_image)
        font = ImageFont.truetype(VALIDATION_CODE, 20)        
        position = self.calculate_validation_code_position(validation_code, font, draw, size)        
        draw.text(position, validation_code, fill=(0, 0, 0), align="center", font=font)
        return validation_code_image
    
    def calculate_validation_code_position(self, validation_code: str, font: ImageFont, draw: ImageDraw, size: tuple) -> tuple:
        text_bbox = draw.textbbox((0, 0), validation_code, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = (size[0] - text_width - 50, size[1] - text_height - 40)        
        return position
    
    def save_certificate(self, certificate: Image, participant: Participant):                    
        # o nome da imagem terá o id do evento, a data do evento e o código de validação e o nome do participante, sem acentos e em maiúsculas, separados por underline
        name_certificate = participant.create_name_certificate()

        certificate.save(f"certificates/{name_certificate}")            
            
        image_buffer = BytesIO()
        certificate.save(image_buffer, format="PNG")
        image_buffer.seek(0)        
        self.events_api.save_certificate(image_buffer, participant, name_certificate)