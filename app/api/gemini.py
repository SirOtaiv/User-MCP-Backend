import json
from json import JSONDecodeError
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.schemas.communs import ListResponse
from app.services.gemini import create_prompt
from app.schemas.gemini import PromptResponse
class PromptRequest(BaseModel):
    prompt: str

router = APIRouter()

@router.post("/", 
    response_model=ListResponse[PromptResponse],
    status_code=status.HTTP_201_CREATED,
)
async def handle_prompt(request: PromptRequest):
   prompt_response_str = await create_prompt(request.prompt)
   if not prompt_response_str:
      raise HTTPException(
         status_code=500, 
         detail="Não foi possível realizar a busca no banco de dados."
      )
   
   try:
      data = json.loads(prompt_response_str)

      # Verifica se o que veio é realmente uma lista
      if not isinstance(data, list):
         raise HTTPException(
               status_code=500,
               detail=f"A resposta do modelo foi um JSON, mas não uma lista: {prompt_response_str}"
         )
      return ListResponse(
         count=len(data),
         rows=data
      )

   except JSONDecodeError:
      raise HTTPException(
         status_code=500,
         detail=f"A resposta do modelo não foi um JSON válido: {prompt_response_str}"
      )
