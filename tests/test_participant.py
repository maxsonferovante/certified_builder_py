import pytest
from events_api.models.participant import Participant, Details
import json

def test_participant_initialization():
    details_json = json.dumps([{"event_id": "1", "last_checkin": "2023-01-01"}])
    participant_data = {
        "id": "123",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "cpf": "12345678901",
        "dob": "1990-01-01",
        "city": "New York",
        "details": details_json,
        "created_date": "2023-01-01",
        "last_update": "2023-01-01",
        "last_checkin": "2023-01-01",
        "opt_in": "yes"
    }

    participant = Participant(**participant_data)

    assert participant.id == "123"
    assert participant.first_name == "John"
    assert participant.last_name == "Doe"
    assert participant.email == "john.doe@example.com"
    assert participant.phone == "1234567890"
    assert participant.cpf == "12345678901"
    assert participant.dob == "1990-01-01"
    assert participant.city == "New York"
    assert len(participant.details) == 1
    assert participant.details[0].event_id == "1"
    assert participant.details[0].last_checkin == "2023-01-01"
    assert participant.created_date == "2023-01-01"
    assert participant.last_update == "2023-01-01"
    assert participant.last_checkin == "2023-01-01"
    assert participant.opt_in == "yes"
    assert len(participant.validation_code) == 9

def test_name_completed():
    participant_data = {
        "id": "123",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "cpf": "12345678901",
        "dob": "1990-01-01",
        "city": "New York",
        "details": [],
        "created_date": "2023-01-01",
        "last_update": "2023-01-01",
        "last_checkin": "2023-01-01",
        "opt_in": "yes"
    }

    participant = Participant(**participant_data)
    assert participant.name_completed() == "John Doe"
    
def test_invalid_email():
        participant_data = {
            "id": "123",
            "first_name": "John",
            "last_name": "Doe",
            "email": 66,
            "phone": "1234567890",
            "cpf": "12345678901",
            "dob": "1990-01-01",
            "city": "New York",
            "details": [],
            "created_date": "2023-01-01",
            "last_update": "2023-01-01",
            "last_checkin": "2023-01-01",
            "opt_in": "yes"
        }

        with pytest.raises(ValueError):
            Participant(**participant_data)

def test_missing_required_field():
    participant_data = {
            "id": "123",
            "first_name": "John",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "cpf": "12345678901",
            "dob": "1990-01-01",
            "city": "New York",
            "details": [],
            "created_date": "2023-01-01",
            "last_update": "2023-01-01",
            "last_checkin": "2023-01-01",
            "opt_in": "yes"
        }

    with pytest.raises(ValueError):
        Participant(**participant_data)

def test_invalid_details_format():
    participant_data = {
            "id": "123",
            "first_name": "John",
            "last_name": "Doe",
            "email": 0,
            "phone": "1234567890",
            "cpf": "12345678901",
            "dob": "1990-01-01",
            "city": "New York",
            "details": "invalid-json",
            "created_date": "2023-01-01",
            "last_update": "2023-01-01",
            "last_checkin": "2023-01-01",
            "opt_in": "yes"
        }

    with pytest.raises(json.JSONDecodeError):
        Participant(**participant_data)

def test_invalid_phone_number():
    participant_data = {
            "id": "123",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": 1,
            "cpf": "12345678901",
            "dob": "1990-01-01",
            "city": "New York",
            "details": [],
            "created_date": "2023-01-01",
            "last_update": "2023-01-01",
            "last_checkin": "2023-01-01",
            "opt_in": "yes"
        }

    with pytest.raises(ValueError):
        Participant(**participant_data)
