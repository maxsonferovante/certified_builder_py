import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
from events_api.events_api import EventsAPI
from events_api.models.participant import Participant


@pytest.fixture
def events_api():
    return EventsAPI()

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
        "details": "[{\"event_id\":\"ab01\",\"last_checkin\":\"2024-11-12 21:41:38\"}]",
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

def test_save_certificate(events_api):
    participant = Participant(
        id = "4",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        dob="1990-01-01",
        cpf="12345678901",
        city="New York",
        details=[{"event_id":"ab01","last_checkin":"2024-11-12 21:41:38"}],
        created_date="2024-11-12 21:41:38",
        last_update="2024-11-12 21:41:38",
        last_checkin="2024-11-12 21:41:38",
        opt_in="1"
    )
    image_buffer = BytesIO(b'test image content')
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success"}
    
    with patch('httpx.post', return_value=mock_response):
        with patch('events_api.events_api.Participant.name_completed', return_value="John Doe"):
            assert events_api.save_certificate(image_buffer, participant) == None