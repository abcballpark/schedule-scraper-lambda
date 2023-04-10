from datetime import datetime
from attrs import define

@define
class Game:
    time: datetime
    division: str
    location: str
    home: str
    away: str
