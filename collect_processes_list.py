from datetime import datetime
from sync_collector import SyncCollector
from async_collector import AsyncCollector
import time
import asyncio
import json
from urllib.parse import urlparse, parse_qs

URL_API_PROCESSOS_SENADO = "https://legis.senado.leg.br/dadosabertos/processo?siglaTipoDocumento={}&dataInicioApresentacao={}&dataFimApresentacao={}&v=1"
URL_API_PROCESSOS_CAMARA =  "https://dadosabertos.camara.leg.br/api/v2/proposicoes?siglaTipo={}&dataApresentacaoInicio={}&dataApresentacaoFim={}&pagina={}&itens=100"

sync_collector = SyncCollector()
async_collector = AsyncCollector()

year_range = range(2000, 2025)

TIPOS_PROCESSOS_SENADO = ["PROJETO_LEI_ORDINARIA", "PROJETO_LEI_COMPLEMENTAR"]
TIPOS_PROCESSOS_CAMARA = ["PL", "PLP"]

URLS_SENADO = {}
URLS_CAMARA = {}


""" for year in year_range:
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    for tipo_processo in TIPOS_PROCESSOS_SENADO:
        URLS_SENADO[f"pls_senado/{tipo_processo}_{year}.json"] = [URL_API_PROCESSOS_SENADO.format(tipo_processo, start_date, end_date)]

    for tipo_processo in TIPOS_PROCESSOS_CAMARA:    
        URLS_CAMARA[f"pls_camara/{tipo_processo}_{year}.json"] = []
        URLS_CAMARA[f"pls_camara/{tipo_processo}_{year}.json"].append(URL_API_PROCESSOS_CAMARA.format(tipo_processo, start_date, end_date, 1))
        
        data = sync_collector.collect(URL_API_PROCESSOS_CAMARA.format(tipo_processo, start_date, end_date, 1))
        links = data.get("links", [])
        last_page_link = [link for link in links if link.get("rel") == "last"]
        if last_page_link:
            last_page = last_page_link[0].get("href")
            parsed_url = urlparse(last_page)
            query_params = parse_qs(parsed_url.query)
            last_page = int(query_params.get("pagina", [1])[0])  # default to 1 if missing
            for page in range(2, last_page + 1):
                URLS_CAMARA[f"pls_camara/{tipo_processo}_{year}.json"].append(URL_API_PROCESSOS_CAMARA.format(tipo_processo, start_date, end_date, page))

json.dump(URLS_CAMARA, open("urls_camara.json", "w"))
json.dump(URLS_SENADO, open("urls_senado.json", "w")) """

URLS_CAMARA = json.load(open("urls_camara.json", "r"))
URLS_SENADO = json.load(open("urls_senado.json", "r"))

def collect_pls_sync():
    start_time = time.time()
    data_per_file = {}

    # chamadas sequenciais

    # SENADO
    for filename in URLS_SENADO:
        data_per_file[filename] = []
        for url in URLS_SENADO[filename]:
            print(url)
            data = sync_collector.collect(url)
            data_per_file[filename].extend(data)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Sync Senado) Elapsed time: {elapsed_time:.2f} seconds")

    # CÂMARA
    for filename in URLS_CAMARA:
        data_per_file[filename] = []
        for url in URLS_CAMARA[filename]:
            print(url)
            data = sync_collector.collect(url)
            data_per_file[filename].extend(data.get("dados", []))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Sync Câmara) Elapsed time: {elapsed_time:.2f} seconds")

    for filepath in data_per_file:
        sync_collector.store_data(data_per_file[filepath], filepath)

async def collect_pls_async():

    # chamadas assíncronas
    start_time = time.time()

    await async_collector.collect(URLS_SENADO)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Async Senado) Elapsed time: {elapsed_time:.2f} seconds")

    start_time = time.time()

    await async_collector.collect(URLS_CAMARA)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Async Câmara) Elapsed time (async): {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    #collect_pls_sync()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(collect_pls_async())
    except RuntimeError:
        # fallback for closed loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(collect_pls_async())