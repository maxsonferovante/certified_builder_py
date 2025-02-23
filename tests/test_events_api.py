import pytest
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO
from PIL import Image
from events_api.events_api import EventsAPI
from events_api.models.participant import Participant


@pytest.fixture
def events_api():
    return EventsAPI(
        url_file_certificate="http://exemplo.com/certificate",
        event_start='2025-02-22 13:29:00', event_end='2025-02-22 18:30:00'
    )

def test_fetch_participants(events_api):
    mock_response = MagicMock()
    mock_response.json.return_value = [
         {
        "id": "4",
        "first_name": "Teste",
        "last_name": "Teste",
        "email": "teste@testando.com",
        "phone": "(48) 98866-7447",
        "cpf": "006.701.959-52",
        "dob": "1983-03-28",
        "city": "teste",
        "details": "[{\"event_id\":\"ab01\",\"last_checkin\":\"2025-02-22 13:45:00\"}]",
        "created_date": "2024-11-12 21:41:38",
        "last_update": "2024-11-12 21:41:38",
        "last_checkin": "2024-11-12 21:41:38",
        "opt_in": "1",
        }
    ]
    
    with patch('httpx.get', return_value=mock_response):
        participants = events_api.fetch_participants()
        assert len(participants) == 1
        assert participants[0].first_name == "Teste"
        assert participants[0].last_name == "Teste"

def test_fetch_file_certificate(events_api):
    mock_response = MagicMock()
    mock_response.content = b'test image content'
    
    with patch('httpx.get', return_value=mock_response):
        with patch('PIL.Image.open', return_value=Image.new('RGB', (100, 100))):
            img = events_api.fetch_file_certificate()
            assert isinstance(img, Image.Image)

