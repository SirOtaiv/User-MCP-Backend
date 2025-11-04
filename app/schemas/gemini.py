from pydantic import BaseModel


class PromptResponse(BaseModel):
   name: str
   link: str
   description: str
   score: int
