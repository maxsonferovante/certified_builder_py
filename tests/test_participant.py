import pytest
from models.participant import Participant
from models.certificate import Certificate
from models.event import Event
from datetime import datetime
from pydantic import ValidationError

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

def test_participant_initialization(mock_certificate, mock_event):
    participant = Participant(
        first_name="Jardel",
        last_name="Godinho",
        email="jardelgodinho@gmail.com",
        phone="(48) 98866-7447",
        cpf="000.000.000-00",
        certificate=mock_certificate,
        event=mock_event
    )

    assert participant.first_name == "Jardel"
    assert participant.last_name == "Godinho"
    assert participant.email == "jardelgodinho@gmail.com"
    assert participant.phone == "(48) 98866-7447"
    assert participant.cpf == "000.000.000-00"
    assert participant.certificate == mock_certificate
    assert participant.event == mock_event
    assert len(participant.validation_code) == 9

def test_name_completed(mock_certificate, mock_event):
    participant = Participant(
        first_name="Jardel",
        last_name="Godinho",
        email="jardelgodinho@gmail.com",
        phone="(48) 98866-7447",
        cpf="000.000.000-00",
        certificate=mock_certificate,
        event=mock_event
    )
    assert participant.name_completed() == "Jardel Godinho"

def test_formated_validation_code(mock_certificate, mock_event):
    participant = Participant(
        first_name="Jardel",
        last_name="Godinho",
        email="jardelgodinho@gmail.com",
        phone="(48) 98866-7447",
        cpf="000.000.000-00",
        certificate=mock_certificate,
        event=mock_event
    )
    formatted_code = participant.formated_validation_code()
    assert len(formatted_code) == 11  # XXX-XXX-XXX
    assert formatted_code[3] == '-'
    assert formatted_code[7] == '-'

def test_create_name_certificate(mock_certificate, mock_event):
    participant = Participant(
        first_name="Jardel",
        last_name="Godinho",
        email="jardelgodinho@gmail.com",
        phone="(48) 98866-7447",
        cpf="000.000.000-00",
        certificate=mock_certificate,
        event=mock_event
    )
    name_certificate = participant.create_name_certificate()
    assert name_certificate.endswith(".png")
    assert "Jardel_Godinho" in name_certificate
    assert "Evento_de_Teste" in name_certificate
    assert participant.formated_validation_code() in name_certificate

def test_invalid_email(mock_certificate, mock_event):
    with pytest.raises(ValidationError) as exc_info:
        Participant(
            first_name="Jardel",
            last_name="Godinho",
            email="invalid-email",
            phone="(48) 98866-7447",
            cpf="000.000.000-00",
            certificate=mock_certificate,
            event=mock_event
        )
    assert "value is not a valid email address" in str(exc_info.value)

def test_missing_required_field(mock_certificate, mock_event):
    with pytest.raises(ValidationError):
        Participant(
            first_name="Jardel",
            email="jardelgodinho@gmail.com",
            phone="(48) 98866-7447",
            cpf="000.000.000-00",
            certificate=mock_certificate,
            event=mock_event
        )

def test_name_completed_with_multiple_names(mock_certificate, mock_event):
    participant = Participant(
        first_name="Jardel Silva",
        last_name="Godinho Santos",
        email="jardelgodinho@gmail.com",
        phone="(48) 98866-7447",
        cpf="000.000.000-00",
        certificate=mock_certificate,
        event=mock_event
    )
    completed_name = participant.name_completed()
    assert len(completed_name.split()) == 3
    assert completed_name == "Jardel Silva Santos"
    
    