from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    order_id: int
    product_id: int
    product_name: str
    date: datetime
    time_checkin: datetime
    checkin_latitude: float
    checkin_longitude: float
    