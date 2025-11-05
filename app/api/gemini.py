import json
import re
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
      match = re.search(r"```(?:json)?\s*([\s\S]*?)```", prompt_response_str)

      if match:
         json_string = match.group(1).strip()
      else:
         json_string = prompt_response_str.strip()

      data = json.loads(json_string)

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
      # Se falhou após a limpeza, a resposta ainda não é um JSON válido
      raise HTTPException(
         status_code=500,
         detail=f"A resposta do modelo não foi um JSON válido: {prompt_response_str}"
      )
   except Exception as e:
      # Captura outros erros de processamento
      raise HTTPException(
         status_code=500,
         detail=f"Erro desconhecido ao processar a resposta do modelo: {e}. Resposta bruta: {prompt_response_str}"
      )
