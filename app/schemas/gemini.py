from pydantic import BaseModel


class PromptResponse(BaseModel):
   name: str
   description: str
   occupation: str
   xp_time: int
   age: int
