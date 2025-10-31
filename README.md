This is a [FastAPI](https://fastapi.tiangolo.com/) project

## Getting Started

First, to run in development you may need to create a `.env` file in the root of the project.

This `.env` file should contain the given variables:

|Name|Description|Example|
|-|-|-|
|SWAGGER_SERVERS_LIST|List of servers divided by `,` that are passed to the [servers](https://swagger.io/docs/specification/api-host-and-base-path/) property of OpenAPI|`/,/api`|
|GEMINI_API_KEY|Chave de Api do Google Gemini||
|GEMINI_MODEL|Modelo a ser usado do Google Gemini|`gemini-2.5-flash`|


use pip to install dependencies

```bash
pip install -r requirements.txt
```

run the development server:

```bash
fastapi dev app/main.py
```

The API will be available at [http://localhost:3000/](http://localhost:3000/).

> You can find the docs at [http://localhost:3000/docs](http://localhost:3000/docs)

## Learn More

To leare more about FastAPI, take a look at the following resources:

- [FastAPI Documentation](https://fastapi.tiangolo.com/learn/) - learn about FastAPI features and API.
