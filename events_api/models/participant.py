from pydantic import BaseModel 
import json

class Details(BaseModel):
    event_id: str
    last_checkin: str

class Participant(BaseModel): 
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    cpf: str
    dob: str
    city: str
    details: list[Details]
    created_date: str
    last_update: str
    last_checkin: str
    opt_in: str
        
    def __init__(self, **data):        
        if isinstance(data['details'], str):
            data["details"] = [
                Details(**item) for item in json.loads(data["details"])
            ]
        super().__init__(**data)
        
        
    # criar metodo name_completed
    def name_completed(self):
        return self.first_name + " " + self.last_name
        
        
