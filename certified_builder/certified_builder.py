from events_api.events_api import EventsAPI
from events_api.models.participant import Participant

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class CertifiedBuilder:
    def __init__(self, events_api: EventsAPI):
        self.events_api = events_api

    def build_certificates(self):
        participants = self.events_api.fetch_participants()

        for participant in participants:
            print(f"Gerando certificado para {participant.name_completed()}")
            
            # Fetch certificate template par o participante atual e o evento para o qual ele está inscrito
            certificate_template = self.events_api.fetch_file_certificate()
            
            self.generate_certificate(participant, certificate_template.copy())

    def generate_certificate(self, participant: Participant, certificate_template: Image):
        name_image = self.create_name_image(participant.name_completed(), certificate_template.size)
        certificate_template.paste(name_image, (0, 0), name_image)
        certificate_template.save(f"certificates/{participant.name_completed()}.png")
        print (f"Certificado gerado para {participant.name_completed()} e salvo em certificates/{participant.name_completed()}.png")
        

    def create_name_image(self, name: str, size: tuple) -> Image:
        name_image = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(name_image)
        font = ImageFont.truetype("fonts/static/OpenSans-Regular.ttf", 50)
        position = self.calculate_text_position(name, font, draw, size)
        draw.text(position, name, fill=(0, 0, 0), align="center", font=font)
        return name_image

    def calculate_text_position(self, text: str, font: ImageFont, draw: ImageDraw, size: tuple) -> tuple:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
        return position
