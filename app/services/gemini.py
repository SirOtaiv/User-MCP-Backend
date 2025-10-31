from google import genai
from app.config import settings
from google.genai import types
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from urllib.parse import urlencode

client = genai.Client(api_key=settings.gemini_api_key)

async def create_prompt(prompt: str):
   # 🔹 Monta a URL do servidor MCP com a chave de acesso
   params = {"api_key": settings.mcp_server_api_key}
   url = f"{settings.mcp_server_url}?{urlencode(params)}"

   # 🔹 Conecta ao servidor MCP
   async with streamablehttp_client(url) as (read, write, _):
      async with ClientSession(read, write) as session:
         await session.initialize()

         tools_result = await session.list_tools()
         tools = []
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

      response = client.models.generate_content(
         model=settings.gemini_model,
         contents=(prompt,
            "Responda APENAS em JSON com o seguinte formato:\n"
            " {'name': Nome da pessoa 'description': Uma descrição da pessoa 'occupation': Nome do cargo atual 'xp_time': Tempo no cargo atual 'age': Idade da pessoa }"
         ),
         config=types.GenerateContentConfig(
            temperature=0,
            tools=tools,
         ),
         response_mime_type="application/json"
      )

      candidate = response.candidates[0]
      part = candidate.content.parts[0]

      if getattr(part, "function_call", None):
            fn = part.function_call
            print(f"Chamando tool: {fn.name}")
            tool_result = await session.call_tool(fn.name, fn.args)
            # Retorna o resultado da execução da tool
            return tool_result.content[0].text

      return response.text