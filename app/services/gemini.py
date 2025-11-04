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
   **NOVO PROMPT RECOMENDADO:**

   Você é um Agente de Recrutamento de Alto Nível (Headhunter) especializado em pesquisa e análise de perfis profissionais.

   ## FLUXO DE TRABALHO:
   1.  **OBRIGATORIAMENTE**, utilize a ferramenta de pesquisa de perfis (`profile-researcher`) para buscar candidatos que correspondam à descrição da vaga a seguir.
   2.  Analise os resultados obtidos pela ferramenta.
   3.  Se a ferramenta não retornar resultados, você deve indicar isso e explicar o porquê (por exemplo, "A busca com os termos X, Y e Z não gerou resultados.").
   4.  Com base nos dados dos 5 candidatos mais promissores encontrados (ou nos 5 melhores que encontrar), preencha o JSON de resposta.

   ## INSTRUÇÕES DA FERRAMENTA:
   * Ao preencher o campo `keywords` da ferramenta `search_linkedin_profiles`, use **APENAS 3 a 5 termos-chave concisos separados por vírgula**, focando no CARGO, TECNOLOGIAS e LOCALIDADE.
   * **NÃO** inclua frases completas ou termos de qualificação como "3 anos de experiência", "comunicação" ou "habilidade".

   Exemplo de argumento desejado: `engenheiro de software, java, são paulo`

   ## DESCRIÇÃO DA VAGA:
   {prompt}

   ## REGRAS DE SAÍDA:
   * Para cada candidato, atribua uma pontuação de 0 a 10 e explique o motivo da nota, baseando-se *apenas* nas informações encontradas pela ferramenta.
   * Responda **APENAS** em JSON, formatado como a LISTA de 5 objetos solicitada.
   * Os campos do json de cada item da lista tem os seguintes campos: name (Nome da pessoa apenas), url (Link do perfil), title, score e reason
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
      print(f"Argumentos da tool: {fn.args}")
      
      async with streamablehttp_client(url) as (read, write, _):
         async with ClientSession(read, write) as session:
               await session.initialize()
               
               tool_result = await session.call_tool(fn.name, fn.args)

      tool_output = tool_result.content[0].text

      contents_for_phase_2 = [
         types.Content(role="user", parts=[types.Part(text=full_prompt)]),
         types.Content(
            role="model",
            parts=[types.Part(function_call=fn)]
         ),
         types.Content(
            role="function",
            parts=[types.Part.from_function_response(
               name=fn.name,
               response={"result": tool_output},
            )]
         )
      ]

      second_response = client.models.generate_content(
         model=settings.gemini_model,
         contents=contents_for_phase_2,
         config=types.GenerateContentConfig(temperature=0)
      )

      final_response_text = second_response.text

   return final_response_text