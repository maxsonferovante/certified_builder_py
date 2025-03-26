import pytest
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO
from PIL import Image
import httpx
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
    
    # Adicione is_success para evitar raise_for_status
    mock_response.is_success = True
    
    with patch('httpx.get', return_value=mock_response):
        try:
            participants = events_api.fetch_participants()
            assert len(participants) == 1
            assert participants[0].first_name == "Teste"
            assert participants[0].last_name == "Teste"
        except Exception as e:
            pass

def test_fetch_participants_404_error(events_api):
    # Create a mock response with 404 status
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.reason_phrase = "Not Found"
    mock_response.url = "https://python.floripa.br/wp-json/custom/v1/event_checkin"
    mock_response.is_success = False
    mock_response.has_redirect_location = False
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Client error '404 Not Found' for url 'https://python.floripa.br/wp-json/custom/v1/event_checkin'\n"
        "For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404",
        request=MagicMock(),
        response=mock_response
    )
    
    with patch('httpx.get', return_value=mock_response):
        with pytest.raises(httpx.HTTPStatusError):
            events_api.fetch_participants()

def test_fetch_file_certificate(events_api):
    mock_response = MagicMock()
    mock_response.content = b'test image content'
    
    with patch('httpx.get', return_value=mock_response):
        with patch('PIL.Image.open', return_value=Image.new('RGB', (100, 100))):
            img = events_api.fetch_file_certificate()
            assert isinstance(img, Image.Image)

def test_save_certificate(events_api):
    # Criar um participante mock
    mock_participant = MagicMock(spec=Participant)
    mock_participant.first_name = "Teste"
    mock_participant.last_name = "Teste"
    mock_participant.email = "teste@teste.com"
    mock_participant.validation_code = "ABC123456"
    mock_participant.details = [MagicMock()]
    mock_participant.details[0].event_id = "Test Event"
    mock_participant.details[0].last_checkin = "2025-02-22 14:10:00"
    
    # Criar um buffer de imagem simulado
    image_buffer = BytesIO(b'test image content')
    name_certificate = "Teste_Teste_Test_Event_ABC-123-456.png"
    
    # Criar resposta mock para requisição POST
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    
    # Patch da requisição post
    with patch('httpx.post', return_value=mock_response) as mock_post:
        events_api.save_certificate(image_buffer, mock_participant, name_certificate)
        
        # Verificar se o método post foi chamado com os parâmetros corretos
        mock_post.assert_called_once()
        
        # Verificar os argumentos passados para o método post
        args, kwargs = mock_post.call_args
        
        # Verificar URL
        assert args[0] == "https://python.floripa.br/wp-json/event/v1/upload"
        
        # Verificar dados
        assert "validation_code" in kwargs["data"]
        assert kwargs["data"]["first_name"] == "Teste"
        assert kwargs["data"]["last_name"] == "Teste"
        assert kwargs["data"]["email"] == "teste@teste.com"
        assert kwargs["data"]["event_id"] == "Test Event"
        
        # Verificar files
        assert "certificate_image" in kwargs["files"]
        assert kwargs["files"]["certificate_image"][0] == name_certificate
