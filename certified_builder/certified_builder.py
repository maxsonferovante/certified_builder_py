import logging
from typing import List
from models.participant import Participant
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from certified_builder.utils.fetch_file_certificate import fetch_file_certificate
import tempfile

FONT_NAME = os.path.join(os.path.dirname(__file__), "fonts/PinyonScript/PinyonScript-Regular.ttf")
VALIDATION_CODE = os.path.join(os.path.dirname(__file__), "fonts/ChakraPetch/ChakraPetch-SemiBold.ttf")
DETAILS_FONT = os.path.join(os.path.dirname(__file__), "fonts/ChakraPetch/ChakraPetch-Regular.ttf")
TEXT_COLOR = (0, 0, 0)

logger = logging.getLogger(__name__)

class CertifiedBuilder:
    def __init__(self):
        # Ensure temp directory exists
        self.temp_dir = "/tmp/certificates"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def build_certificates(self, participants: List[Participant]):
        """Build certificates for all participants."""
        try:
            logger.info(f"Iniciando geração de {len(participants)} certificados")
            results = []
            
            for participant in participants:
                try:
                    # Download template and logo with error handling
                    certificate_template = self._download_image(participant.certificate.background)
                    logo = self._download_image(participant.certificate.logo)
                    
                    # Generate and save certificate
                    certificate_generated = self.generate_certificate(participant, certificate_template, logo)
                    certificate_path = self.save_certificate(certificate_generated, participant)
                    
                    results.append({
                        "participant": participant.model_dump(),
                        "certificate_path": certificate_path,
                        "success": True
                    })
                    
                    logger.info(f"Certificado gerado para {participant.name_completed()} com codigo de validação {participant.formated_validation_code()}")
                except Exception as e:
                    logger.error(f"Erro ao gerar certificado para {participant.name_completed()}: {str(e)}")
                    results.append({
                        "participant": participant.model_dump(),
                        "error": str(e),
                        "success": False
                    })
            
            return results
        except Exception as e:
            logger.error(f"Erro geral na geração de certificados: {str(e)}")
            raise

    def _download_image(self, url: str) -> Image:
        """Download and open image with error handling."""
        try:
            return fetch_file_certificate(url)
        except Exception as e:
            logger.error(f"Erro ao baixar imagem de {url}: {str(e)}")
            raise RuntimeError(f"Error downloading image from {url}: {str(e)}")

    def generate_certificate(self, participant: Participant, certificate_template: Image, logo: Image):
        """Generate a certificate for a participant."""
        try:
            # Create transparent layer for text and logo
            overlay = Image.new("RGBA", certificate_template.size, (255, 255, 255, 0))
            
            # Optimize logo size
            logo_size = (150, 150)
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            
            # Paste logo
            padding = 50
            overlay.paste(logo, (padding, padding), logo)
            
            # Add name
            name_image = self.create_name_image(participant.name_completed(), certificate_template.size)
            overlay.paste(name_image, (0, 0), name_image)
            
            # Add details
            details_image = self.create_details_image(participant.certificate.details, certificate_template.size)
            name_center_y = certificate_template.size[1] // 2
            details_y = name_center_y + 50
            
            details_with_position = Image.new("RGBA", certificate_template.size, (255, 255, 255, 0))
            details_with_position.paste(details_image, (0, details_y), details_image)
            overlay = Image.alpha_composite(overlay, details_with_position)
            
            # Add validation code
            validation_code_image = self.create_validation_code_image(participant.formated_validation_code(), certificate_template.size)
            overlay.paste(validation_code_image, (0, 0), validation_code_image)
            
            # Merge and optimize final image
            result = Image.new("RGBA", certificate_template.size, (255, 255, 255, 0))
            result.paste(certificate_template, (0, 0))
            result = Image.alpha_composite(result, overlay)
            
            return result
        except Exception as e:
            logger.error(f"Erro ao gerar certificado: {str(e)}")
            raise

    def create_name_image(self, name: str, size: tuple) -> Image:
        """Create image with participant's name."""
        try:
            name_image = Image.new("RGBA", size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(name_image)
            font = ImageFont.truetype(FONT_NAME, 70)
            position = self.calculate_text_position(name, font, draw, size)
            draw.text(position, name, fill=TEXT_COLOR, font=font)
            return name_image
        except Exception as e:
            logger.error(f"Erro ao criar imagem do nome: {str(e)}")
            raise

    def create_details_image(self, details: str, size: tuple) -> Image:
        """Create image with certificate details."""
        try:
            details_image = Image.new("RGBA", size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(details_image)
            font = ImageFont.truetype(DETAILS_FONT, 18)

            words = details.split()
            total_words = len(words)
            words_per_line = total_words // 3
            
            line1 = ' '.join(words[:words_per_line])
            line2 = ' '.join(words[words_per_line:words_per_line*2])
            line3 = ' '.join(words[words_per_line*2:])
            
            line_height = font.size + 10
            
            line1_bbox = draw.textbbox((0, 0), line1, font=font)
            line2_bbox = draw.textbbox((0, 0), line2, font=font)
            line3_bbox = draw.textbbox((0, 0), line3, font=font)
            
            start_y = 0
            
            x1 = (size[0] - (line1_bbox[2] - line1_bbox[0])) / 2
            x2 = (size[0] - (line2_bbox[2] - line2_bbox[0])) / 2
            x3 = (size[0] - (line3_bbox[2] - line3_bbox[0])) / 2
            
            draw.text((x1, start_y), line1, fill=TEXT_COLOR, font=font)
            draw.text((x2, start_y + line_height), line2, fill=TEXT_COLOR, font=font)
            draw.text((x3, start_y + line_height * 2), line3, fill=TEXT_COLOR, font=font)
            
            return details_image
        except Exception as e:
            logger.error(f"Erro ao criar imagem dos detalhes: {str(e)}")
            raise

    def create_validation_code_image(self, validation_code: str, size: tuple) -> Image:
        """Create image with validation code."""
        try:
            validation_code_image = Image.new("RGBA", size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(validation_code_image)
            font = ImageFont.truetype(VALIDATION_CODE, 20)
            position = self.calculate_validation_code_position(validation_code, font, draw, size)
            draw.text(position, validation_code, fill=TEXT_COLOR, font=font)
            return validation_code_image
        except Exception as e:
            logger.error(f"Erro ao criar imagem do código de validação: {str(e)}")
            raise

    def calculate_text_position(self, text: str, font: ImageFont, draw: ImageDraw, size: tuple) -> tuple:
        """Calculate centered position for text."""
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return ((size[0] - text_width) / 2, (size[1] - text_height) / 2)

    def calculate_validation_code_position(self, validation_code: str, font: ImageFont, draw: ImageDraw, size: tuple) -> tuple:
        """Calculate position for validation code."""
        text_bbox = draw.textbbox((0, 0), validation_code, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return (size[0] - text_width - 50, size[1] - text_height - 40)

    def save_certificate(self, certificate: Image, participant: Participant) -> str:
        """Save certificate to temporary directory."""
        try:
            name_certificate = participant.create_name_certificate()
            file_path = os.path.join(self.temp_dir, name_certificate)
            
            # Optimize image before saving
            certificate = certificate.convert('RGB')
            certificate.save(file_path, format="PNG", optimize=True)
            
            return file_path
        except Exception as e:
            logger.error(f"Erro ao salvar certificado: {str(e)}")
            raise