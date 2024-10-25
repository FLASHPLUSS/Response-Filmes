from fastapi import FastAPI, HTTPException
import requests
from cachetools import TTLCache

app = FastAPI()

# URL do Dropbox para acessar o arquivo JSON com filmes e séries
DROPBOX_URL = "https://dl.dropboxusercontent.com/s/v2fuahx8uxcar2edrkk8m/Filmes_Series.json?rlkey=mjw8j0iw5047eofkcm2wkqwbo&st=do83pnno&dl=1"

# Sessão de requisições persistente e cache com expiração
session = requests.Session()
cache = TTLCache(maxsize=1, ttl=300)  # Cache de 5 minutos

@app.get("/filmes")
async def obter_filmes():
    # Verifica se os dados estão no cache
    if "filmes_data" in cache:
        return cache["filmes_data"]

    try:
        # Faz a requisição ao link do Dropbox usando a sessão persistente
        response = session.get(DROPBOX_URL)
        response.raise_for_status()
        filmes_data = response.json()  # Carrega o conteúdo JSON

        # Armazena no cache para respostas rápidas nas próximas requisições
        cache["filmes_data"] = filmes_data

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o link do Dropbox: {str(e)}")
    except ValueError:
        raise HTTPException(status_code=500, detail="Erro ao processar o conteúdo JSON.")

    return filmes_data

@app.get("/filmes/{titulo}")
async def obter_filme_por_titulo(titulo: str):
    # Verifica o cache
    if "filmes_data" not in cache:
        await obter_filmes()  # Carrega os dados no cache se ainda não estiverem

    filmes_data = cache["filmes_data"]

    # Busca o filme pelo título
    filme = next((item for item in filmes_data if item.get("Titulo", "").lower() == titulo.lower()), None)

    if filme is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    return filme
