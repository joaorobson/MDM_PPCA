import os
from async_collector import AsyncCollector
import json
from pathlib import Path
import time
import asyncio
from itertools import islice
import re

def chunk_dict(data: dict, chunk_size: int):
    it = iter(data.items())
    while True:
        chunk = dict(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk

URL_CAMARA_TEMAS_PROCESSO =  "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{}/temas"
URLS_CAMARA_TEMAS = {}
async_collector = AsyncCollector()

""" 
directory_path = Path("detalhes_pls_camara")
for file_path in directory_path.iterdir():
    if file_path.is_file():
        print(file_path.as_posix())
        id_ = re.findall('\d+', file_path.as_posix())
        if len(id_) == 1:
            id_ = id_[0]
            URLS_CAMARA_TEMAS[f"temas_pls_camara/{id_}.json"] = [URL_CAMARA_TEMAS_PROCESSO.format(id_)]

json.dump(URLS_CAMARA_TEMAS, open("urls_camara_temas.json", "w"))
 """

URLS_CAMARA_TEMAS = json.load(open("urls_camara_temas.json", "r"))
async def collect_pls_async():

    # chamadas assíncronas

    start_time = time.time()
    results = {}
    for i, batch in enumerate(chunk_dict(URLS_CAMARA_TEMAS, 40), 1):
        print(f"Starting batch {i} with {len(batch)} file(s)...")
        batch_result = await async_collector.collect(batch)
        results.update(batch_result)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"(Async Câmara) Elapsed time: {elapsed_time:.2f} seconds")

    for filepath in results:
        async_collector.store_data(results[filepath], filepath)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(collect_pls_async())
    except RuntimeError:
        # fallback for closed loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(collect_pls_async())