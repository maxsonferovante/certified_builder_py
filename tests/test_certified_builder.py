import pytest
from unittest.mock import Mock, patch
from PIL import Image
from certified_builder.certified_builder import CertifiedBuilder
from events_api.models.participant import Participant

@pytest.fixture
def mock_events_api():
    return Mock()

@pytest.fixture
def certified_builder(mock_events_api):
    return CertifiedBuilder(mock_events_api)

@pytest.fixture
def mock_participant():
    participant = Mock(spec=Participant)
    participant.name_completed.return_value = "John Doe"
    participant.validation_code = "123456"
    return participant

@pytest.fixture
def mock_certificate_template():
    return Image.new("RGBA", (800, 600), (255, 255, 255, 0))

def test_build_certificates(certified_builder, mock_events_api, mock_participant, mock_certificate_template):
    mock_events_api.fetch_participants.return_value = [mock_participant]
    mock_events_api.fetch_file_certificate.return_value = mock_certificate_template

    with patch.object(certified_builder, 'generate_certificate', return_value=mock_certificate_template) as mock_generate_certificate, \
         patch.object(certified_builder, 'save_certificate') as mock_save_certificate:
        certified_builder.build_certificates()

        mock_events_api.fetch_participants.assert_called_once()
        mock_events_api.fetch_file_certificate.assert_called_once()
        mock_generate_certificate.assert_called_once_with(mock_participant, mock_certificate_template)
        mock_save_certificate.assert_called_once_with(mock_certificate_template, mock_participant)
        
def test_create_name_image(certified_builder, mock_participant, mock_certificate_template):
    name_image = certified_builder.create_name_image(mock_participant.name_completed(), mock_certificate_template.size)
    assert name_image.size == mock_certificate_template.size

def test_create_validation_code_image(certified_builder, mock_participant, mock_certificate_template):
    validation_code_image = certified_builder.create_validation_code_image(mock_participant.validation_code, mock_certificate_template.size)
    assert validation_code_image.size == mock_certificate_template.size
    assert validation_code_image.mode == "RGBA"
    

def test_save_certificate(certified_builder, mock_participant, mock_certificate_template, mock_events_api):
    with patch("builtins.open", new_callable=Mock):
        certified_builder.save_certificate(mock_certificate_template, mock_participant)
        mock_events_api.save_certificate.assert_called_once()