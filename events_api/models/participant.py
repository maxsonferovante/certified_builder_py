from pydantic import BaseModel, Field
from typing import Optional
import json
import random
import string


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
    validation_code: Optional[str] = Field(default_factory= lambda: ''.join(random.choices(string.hexdigits, k=9)), init=False)
        
    def __init__(self, **data):        
        if isinstance(data['details'], str):
            data["details"] = [
                Details(**item) for item in json.loads(data["details"])
            ]

        super().__init__(**data)
        
        
    # criar metodo name_completed
    def name_completed(self):
        return self.first_name + " " + self.last_name
                

    def formated_validation_code(self):
        return f"{self.validation_code[0:3]}-{self.validation_code[3:6]}-{self.validation_code[6:9]}"
