from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from .certificate import Certificate
from .event import Event

import random
import string

class Participant(BaseModel): 
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    cpf: str    
    validation_code: Optional[str] = Field(default_factory= lambda: ''.join(random.choices(string.hexdigits, k=9)), init=False)
    certificate: Optional[Certificate] = None
    event: Optional[Event] = None

    def __str__(self):
        return f"Participant: {self.first_name} {self.last_name} - {self.email}"   

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
        name_certificate = self.name_completed() + self.event.product_name + "_" + self.formated_validation_code() + ".png"
        name_certificate = name_certificate.replace(" ", "_")
        return name_certificate