from pydantic import BaseModel


class PromptResponse(BaseModel):
   name: str
   url: str
   title: str
   score: float
   reason: str