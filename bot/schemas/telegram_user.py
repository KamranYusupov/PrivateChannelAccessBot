from typing import Optional

from pydantic import BaseModel, Field


class TelegramUserBaseSchema(BaseModel):
    telegram_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    
    
class TelegramUserSchema(TelegramUserBaseSchema):
    id: int 
    

class TelegramUserCreateSchema(TelegramUserBaseSchema):
    telegram_id: int = Field(alias="id")
