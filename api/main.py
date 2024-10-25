from fastapi import FastAPI, HTTPException
import requests
import time
from cachetools import TTLCache

app = FastAPI()

# Configuração da URL fixa do Dropbox
DROPBOX_URL = "https://dl.dropboxusercontent.com/s/v2fuahx8uxcar2edrkk8m/Filmes_Series.json?rlkey=mjw8j0iw5047eofkcm2wkqwbo&st=do83pnno&dl=1"

# Sessão de requisições persistente e cache com expiração
session = requests.Session()
cache = TTLCache(maxsize=1, ttl=300)  # Cache com 1 item e 5 minutos de expiração (300 segundos)

@app.get("/filmes")
async def obter_filmes():
    # Verifica o cache
    if "filmes_data" in cache:
        return cache["filmes_data"]

    try:
        # Faz a requisição ao link direto do Dropbox usando a sessão persistente
        response = session.get(DROPBOX_URL)
        response.raise_for_status()
        filmes_data = response.json()  # Carrega o conteúdo JSON

        # Armazena no cache para respostas mais rápidas nas próximas requisições
        cache["filmes_data"] = filmes_data

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o link do Dropbox: {str(e)}")
    except ValueError:
        raise HTTPException(status_code=500, detail="Erro ao processar o conteúdo JSON.")

    return filmes_data
