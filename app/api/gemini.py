from fastapi import APIRouter, HTTPException, status

from app.schemas.communs import ListResponse
from app.services.gemini import create_prompt
from app.schemas.gemini import PromptResponse

router = APIRouter()

@router.post("/", 
    response_model=ListResponse[PromptResponse],
    status_code=status.HTTP_201_CREATED,
)
async def handle_prompt(body: str):
    prompt_response = await create_prompt(body)
    if not prompt_response:
        raise HTTPException(
            status_code=500, 
            detail="Não foi possível realizar a busca no banco de dados."
        )
    
    return prompt_response
