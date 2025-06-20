import os
from async_collector import AsyncCollector
import json
from pathlib import Path
import time
import asyncio
from itertools import islice


def chunk_dict(data: dict, chunk_size: int):
    it = iter(data.items())
    while True:
        chunk = dict(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk

URL_SENADO_DETALHE_PROCESSO = "https://legis.senado.leg.br/dadosabertos/processo/{}?v=1"
URL_CAMARA_DETALHE_PROCESSO =  "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{}"
URLS_SENADO_DETALHES = {}
URLS_CAMARA_DETALHES = {}
async_collector = AsyncCollector()

""" directory_path = Path("pls_senado")
for file_path in directory_path.iterdir():
    print(file_path)
    if file_path.is_file():
        content = json.loads(file_path.read_text())

        ids = [p['id'] for p in content]
        
        for id_ in ids:
            URLS_SENADO_DETALHES[f"detalhes_pls_senado/{id_}.json"] = [URL_SENADO_DETALHE_PROCESSO.format(id_)] """

directory_path = Path("pls_camara")
for file_path in directory_path.iterdir():
    print(file_path)
    if file_path.is_file():
        content = json.loads(file_path.read_text())

        ids = [p['id'] for p in content]
        
        for id_ in ids:
            URLS_CAMARA_DETALHES[f"detalhes_pls_camara/{id_}.json"] = [URL_CAMARA_DETALHE_PROCESSO.format(id_)]

async def collect_pls_async():

    # chamadas assíncronas
    """ start_time = time.time()
    results = {}
    for i, batch in enumerate(chunk_dict(URLS_SENADO_DETALHES, 40), 1):
        print(f"Starting batch {i} with {len(batch)} file(s)...")
        batch_result = await async_collector.collect(batch)
        results.update(batch_result)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Async Senado) Elapsed time: {elapsed_time:.2f} seconds")

    for filepath in results:
        async_collector.store_data(results[filepath], filepath) """

    start_time = time.time()
    results = {}
    for i, batch in enumerate(chunk_dict(URLS_CAMARA_DETALHES, 40), 1):
        print(f"Starting batch {i} with {len(batch)} file(s)...")
        batch_result = await async_collector.collect(batch)
        results.update(batch_result)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Async Câmara) Elapsed time: {elapsed_time:.2f} seconds")

    for filepath in results:
        async_collector.store_data(results[filepath], filepath)

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