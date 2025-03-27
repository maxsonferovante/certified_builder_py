import pytest
from unittest.mock import Mock, patch
from PIL import Image
from certified_builder.certified_builder import CertifiedBuilder
from models.participant import Participant
from models.certificate import Certificate
from models.event import Event
from datetime import datetime

@pytest.fixture
def mock_certificate():
    return Certificate(
        details="In recognition of their participation in the 84st edition of the Python Floripa Community Meeting, held on March 29, 2025, in Florianópolis, Brazil.",
        logo="https://tech.floripa.br/wp-content/uploads/2025/03/84o-Python-Floripa-e1741729144453.png",
        background="https://tech.floripa.br/wp-content/uploads/2025/03/Background.png"
    )

@pytest.fixture
def mock_event():
    return Event(
        order_id=452,
        product_id=316,
        product_name="Evento de Teste",
        date=datetime.strptime("2025-03-26 20:55:25", "%Y-%m-%d %H:%M:%S"),
        time_checkin=datetime.strptime("2025-03-26 20:55:44", "%Y-%m-%d %H:%M:%S"),
        checkin_latitude=-27.5460492,
        checkin_longitude=-48.6227075
    )

@pytest.fixture
def mock_participant(mock_certificate, mock_event):
    return Participant(
        first_name="Jardel",
        last_name="Godinho",
        email="jardelgodinho@gmail.com",
        phone="(48) 98866-7447",
        cpf="000.000.000-00",
        certificate=mock_certificate,
        event=mock_event
    )

@pytest.fixture
def mock_certificate_template():
    return Image.new("RGBA", (1920, 1080), (255, 255, 255, 0))

@pytest.fixture
def mock_logo():
    return Image.new("RGBA", (150, 150), (255, 255, 255, 0))

@pytest.fixture
def certified_builder():
    return CertifiedBuilder()

def test_generate_certificate(certified_builder, mock_participant, mock_certificate_template, mock_logo):
    with patch('certified_builder.utils.fetch_file_certificate.fetch_file_certificate', side_effect=[mock_certificate_template, mock_logo]):
        certificate = certified_builder.generate_certificate(mock_participant, mock_certificate_template, mock_logo)
        assert isinstance(certificate, Image.Image)
        assert certificate.size == mock_certificate_template.size
        assert certificate.mode == "RGBA"

def test_create_name_image(certified_builder, mock_participant, mock_certificate_template):
    name_image = certified_builder.create_name_image(mock_participant.name_completed(), mock_certificate_template.size)
    assert isinstance(name_image, Image.Image)
    assert name_image.size == mock_certificate_template.size
    assert name_image.mode == "RGBA"

def test_create_details_image(certified_builder, mock_participant, mock_certificate_template):
    details_image = certified_builder.create_details_image(mock_participant.certificate.details, mock_certificate_template.size)
    assert isinstance(details_image, Image.Image)
    assert details_image.size == mock_certificate_template.size
    assert details_image.mode == "RGBA"

def test_create_validation_code_image(certified_builder, mock_participant, mock_certificate_template):
    validation_code_image = certified_builder.create_validation_code_image(mock_participant.formated_validation_code(), mock_certificate_template.size)
    assert isinstance(validation_code_image, Image.Image)
    assert validation_code_image.size == mock_certificate_template.size
    assert validation_code_image.mode == "RGBA"

def test_build_certificates(certified_builder, mock_participant, mock_certificate_template, mock_logo):
    participants = [mock_participant]
    
    with patch('certified_builder.utils.fetch_file_certificate.fetch_file_certificate', side_effect=[mock_certificate_template, mock_logo]), \
         patch.object(certified_builder, 'save_certificate') as mock_save:
        
        certified_builder.build_certificates(participants)
        
        mock_save.assert_called_once()
        args = mock_save.call_args[0]
        assert isinstance(args[0], Image.Image)
        assert args[1] == mock_participant
        
