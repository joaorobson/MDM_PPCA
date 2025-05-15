import json
import requests

class ProcessesCollector:
    
    def collect(self) -> dict:
        ...

    def collect_sync(self, url: str, headers: dict = {'Content-Type': 'application/json'}) -> dict:
        try:
            data = requests.get(url, headers=headers)
        except Exception as e:
            print(f"Erro: {e}")

        return data.json()

    def store_data(self, data: dict, filepath: str) -> None:
        json.dump(data, open(filepath, "w"))
