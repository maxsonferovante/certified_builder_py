import logging
from typing import List
from models.participant import Participant
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from certified_builder.utils.fetch_file_certificate import fetch_file_certificate
import textwrap

FONT_NAME="certified_builder/fonts/PinyonScript/PinyonScript-Regular.ttf"
VALIDATION_CODE="certified_builder/fonts/ChakraPetch/ChakraPetch-SemiBold.ttf"
DETAILS_FONT="certified_builder/fonts/ChakraPetch/ChakraPetch-Regular.ttf"
TEXT_COLOR = (0, 0, 0)  # Define black color as constant

logger = logging.getLogger(__name__)

class CertifiedBuilder:
        
    def build_certificates(self, participants: List[Participant]):
        logger.info(f"Iniciando geração de {len(participants)} certificados")
        for participant in participants:
            certificate_template = fetch_file_certificate(participant.certificate.background)
            logo = fetch_file_certificate(participant.certificate.logo)
            certificate_generated = self.generate_certificate(participant, certificate_template.copy(), logo)            
            self.save_certificate(certificate_generated, participant)
            logger.info(f"Certificado gerado para {participant.name_completed()} com codigo de validação {participant.formated_validation_code()}")

    def generate_certificate(self, participant: Participant, certificate_template: Image, logo: Image):
        # Create transparent layer for text and logo
        overlay = Image.new("RGBA", certificate_template.size, (255, 255, 255, 0))
        
        # Resize logo to fit in top-left corner (e.g. 150x150 pixels)
        logo_size = (150, 150)
        logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
        
        # Paste logo in top-left corner with padding
        padding = 50
        overlay.paste(logo, (padding, padding), logo)
        
        # Add name
        name_image = self.create_name_image(participant.name_completed(), certificate_template.size)
        overlay.paste(name_image, (0, 0), name_image)
        
        # Add details text below name
        details_image = self.create_details_image(participant.certificate.details, certificate_template.size)
        # Calculate position for details (100 pixels below the name)
        name_center_y = certificate_template.size[1] // 2  # Center of the image
        details_y = name_center_y + 50  # 50 pixels below the center
        
        # Create a new image for details with correct position
        details_with_position = Image.new("RGBA", certificate_template.size, (255, 255, 255, 0))
        details_with_position.paste(details_image, (0, details_y), details_image)
        
        # Merge details with overlay
        overlay = Image.alpha_composite(overlay, details_with_position)
        
        # Add validation code
        validation_code_image = self.create_validation_code_image(participant.formated_validation_code(), certificate_template.size)
        overlay.paste(validation_code_image, (0, 0), validation_code_image)
        
        # Merge overlay with template
        result = Image.new("RGBA", certificate_template.size, (255, 255, 255, 0))
        result.paste(certificate_template, (0, 0))
        result = Image.alpha_composite(result, overlay)
        
        return result

    def create_name_image(self, name: str, size: tuple) -> Image:
        name_image = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(name_image)
        font = ImageFont.truetype(FONT_NAME, 70)
        position = self.calculate_text_position(name, font, draw, size)
        draw.text(position, name, fill=TEXT_COLOR, font=font)
        return name_image

    def create_details_image(self, details: str, size: tuple) -> Image:
        details_image = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(details_image)
        font = ImageFont.truetype(DETAILS_FONT, 18)

        # Split text into three lines
        words = details.split()
        total_words = len(words)
        words_per_line = total_words // 3
        
        # Create three balanced lines
        line1 = ' '.join(words[:words_per_line])
        line2 = ' '.join(words[words_per_line:words_per_line*2])
        line3 = ' '.join(words[words_per_line*2:])
        
        # Calculate positions for all three lines
        line_height = font.size + 10  # Add 10 pixels spacing between lines
        
        # Get the width of the longest line to center all lines
        line1_bbox = draw.textbbox((0, 0), line1, font=font)
        line2_bbox = draw.textbbox((0, 0), line2, font=font)
        line3_bbox = draw.textbbox((0, 0), line3, font=font)
        
        # Calculate vertical center position for all three lines
        total_height = line_height * 3
        start_y = 0  # Start from top since position will be handled in generate_certificate
        
        # Draw each line centered
        x1 = (size[0] - (line1_bbox[2] - line1_bbox[0])) / 2
        x2 = (size[0] - (line2_bbox[2] - line2_bbox[0])) / 2
        x3 = (size[0] - (line3_bbox[2] - line3_bbox[0])) / 2
        
        # Draw text with explicit black color
        draw.text((x1, start_y), line1, fill=TEXT_COLOR, font=font)
        draw.text((x2, start_y + line_height), line2, fill=TEXT_COLOR, font=font)
        draw.text((x3, start_y + line_height * 2), line3, fill=TEXT_COLOR, font=font)
        
        return details_image

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
        draw.text(position, validation_code, fill=TEXT_COLOR, font=font)
        return validation_code_image
    
    def calculate_validation_code_position(self, validation_code: str, font: ImageFont, draw: ImageDraw, size: tuple) -> tuple:
        text_bbox = draw.textbbox((0, 0), validation_code, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = (size[0] - text_width - 50, size[1] - text_height - 40)        
        return position
    
    def save_certificate(self, certificate: Image, participant: Participant):                            
        name_certificate = participant.create_name_certificate()            
        image_buffer = BytesIO()
        certificate.save(image_buffer, format="PNG")
        certificate.save(f"certificates/{name_certificate}")
        image_buffer.seek(0)        
        # self.events_api.save_certificate(image_buffer, participant, name_certificate)