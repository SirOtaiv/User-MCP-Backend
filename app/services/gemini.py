from google import genai
from app.config import settings
from google.genai import types
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from urllib.parse import urlencode

client = genai.Client(api_key=settings.gemini_api_key)

async def get_mcp_tools(url: str):
    tools = []
    # Abre a conexão apenas para listar as ferramentas
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            
            for t in tools_result.tools:
                func_decl = {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": {
                        k: v for k, v in (t.inputSchema or {}).items()
                        if k not in ["additionalProperties", "$schema"]
                    },
                }
                tools.append(types.Tool(function_declarations=[func_decl]))
                
    return tools

async def create_prompt(prompt: str):
   # 🔹 Monta a URL do servidor MCP com a chave de acesso
   params = {"api_key": settings.mcp_server_api_key, "profile": settings.mcp_server_profile}
   url = f"{settings.mcp_server_url}?{urlencode(params)}"

   # 🔹 Conecta ao servidor MCP
   tools = await get_mcp_tools(url)

   full_prompt = f"""
   {prompt}

   Com base na descrição da vaga acima, faça uma pesquisa e análise dos 5 melhores candidatos prováveis.
   Para cada candidato, atribua uma pontuação de 0 a 10 e explique o motivo da nota.

   Responda APENAS em JSON, formatado como uma LISTA contendo 5 objetos:

   [
   {{
      "name": "Nome do candidato 1",
      "link": "URL do perfil (string)",
      "score": 9,
      "description": "Breve explicação do motivo da nota"
   }},
   {{
      "name": "Nome do candidato 2",
      "link": "URL do perfil (string)",
      "score": 8,
      "description": "Breve explicação do motivo da nota"
   }},
   ... (e assim por diante até 5)
   ]
   """

   response = client.models.generate_content(
      model=settings.gemini_model,
      contents=[full_prompt],
      config=types.GenerateContentConfig(
         temperature=0,
         tools=tools,
      ),
   )

   candidate = response.candidates[0]
   part = candidate.content.parts[0]

   # Processa a resposta do Gemini (Execução Condicional da Tool)
   if getattr(part, "function_call", None):
      fn = part.function_call
      print(f"Chamando tool: {fn.name}")
      
      async with streamablehttp_client(url) as (read, write, _):
         async with ClientSession(read, write) as session:
               await session.initialize()
               
               tool_result = await session.call_tool(fn.name, fn.args)
               # Retorna o resultado da execução da tool
               return tool_result.content[0].text

   return response.text