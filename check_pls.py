import os
from async_collector import AsyncCollector
import json
from pathlib import Path
import time
import asyncio
from itertools import islice

directory_path = Path("pls_camara")


URLS_DETALHES = {}
pls = os.listdir('detalhes_pls_camara')




for file_path in directory_path.iterdir():
    if file_path.is_file():
        content = json.loads(file_path.read_text())

        ids = [p['id'] for p in content]
        
        for id_ in ids:
            if not os.path.exists(f'detalhes_pls_camara/{id_}.json'):
                print(id_)