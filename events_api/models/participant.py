from pydantic import BaseModel, Field
from typing import Optional
import json
import random
import string
from datetime import datetime


class Details(BaseModel):
    event_id: str
    last_checkin: str

    def __str__(self):
        return f"Details: {self.event_id} - {self.last_checkin}"

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

    def __str__(self):
        return f"Participant: {self.first_name} {self.last_name} - {self.email} - {self.details[0].event_id} - {self.details[0].last_checkin}"   

    def filter_last_checkin(self, event_start:str , event_end:str):        

        # Convert string dates to datetime objects for comparison
        self.details = [
            event for event in self.details 
            if datetime.strptime(event.last_checkin, '%Y-%m-%d %H:%M:%S') > datetime.strptime(event_start, '%Y-%m-%d %H:%M:%S')
            and datetime.strptime(event.last_checkin, '%Y-%m-%d %H:%M:%S') < datetime.strptime(event_end, '%Y-%m-%d %H:%M:%S')
        ]

        
    # criar metodo name_completed
    def name_completed(self):
        self.first_name = self.first_name.lower()
        self.last_name = self.last_name.lower()
        
        name_completed = self.first_name + " " + self.last_name
        if len(name_completed.split(" ")) > 3:
            self.first_name = name_completed.split()[0]
            self.last_name = name_completed.split()[1] + " " + name_completed.split()[-1]
            name_completed = self.first_name + " " + self.last_name
        
        return name_completed.title()
    
                

    def formated_validation_code(self):
        self.validation_code = self.validation_code.upper()
        return f"{self.validation_code[0:3]}-{self.validation_code[3:6]}-{self.validation_code[6:9]}"

    def create_name_certificate(self):        
        name_certificate = self.name_completed() + "_" + self.details[0].event_id + "_" + self.formated_validation_code() + ".png"
        name_certificate = name_certificate.replace(" ", "_")
        return name_certificate