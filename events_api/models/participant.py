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
        self.first_name = self.first_name.lower()
        self.last_name = self.last_name.lower()
        
        name_completed = self.first_name + " " + self.last_name
        if len(name_completed.split(" ")) > 3:
            self.first_name = name_completed.split()[0]
            self.last_name = name_completed.split()[1] + " " + name_completed.split()[-1]
            name_completed = self.first_name + " " + self.last_name
        
        return name_completed.capitalize()
    
                

    def formated_validation_code(self):
        self.validation_code = self.validation_code.upper()
        return f"{self.validation_code[0:3]}-{self.validation_code[3:6]}-{self.validation_code[6:9]}"
