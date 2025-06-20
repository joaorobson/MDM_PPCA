from pathlib import Path
import json
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from models import Autor, Casa, Classificacao, ProjetoLei
import time


def processa_senado(file_path):
    data = json.loads(file_path.read_text())[0]
    projeto_lei = ProjetoLei(
        id=data.get("id"),
        nome=data.get("identificacao", ""),
        nome_original=data.get("identificacaoProcessoInicial", ""),
        outros_nomes
        palavras_chave=(data.get("documento", {}).get("indexacao") or "").split(","),
        autores=[
            Autor(
                nome=autor.get("autor", ""),
                tipo=autor.get("descricaoTipo", ""),
                uf=autor.get("uf", ""),
                sexo=autor.get("sexo", "")
            )
            for autor in data.get("autoriaIniciativa", [])
        ],
        transformado_em_norma=bool(data.get("normaGerada")),
        em_tramitacao=(data.get("tramitando") == "Sim"),
        data_apresentacao=data.get("documento", {}).get("dataApresentacao", ""),
        casa_origem=Casa.CAMARA if data.get("siglaCasaIniciadora") == "CD" else Casa.SENADO,
        ementa=data.get("conteudo", {}).get("ementa", ""),
        classificacoes=[
            Classificacao(
                descricao=c.get("descricao", ""),
                descricao_hierarquica=c.get("descricaoHierarquia", "")
            )
            for c in data.get("classificacoes", [])
        ]
    )
    return projeto_lei.model_dump(mode="json")

def processa_camara(file_path):
    data = json.loads(file_path.read_text())[0]
    try:
        autores_json = json.load(open(f"autores_pls_camara/{data.get('id')}.json"))
    except FileNotFoundError:
        autores_json = []
    autores = [
        Autor(
            nome=autor.get("nome", ""),
            tipo=autor.get("tipo", ""),
            uf="",
            sexo=""
        )
        for autor in autores_json
    ]
    projeto_lei = ProjetoLei(
        id=data.get("id"),
        nome=f"{data.get('siglaTipo', '')} {data.get('numero', '')}/{data.get('ano', '')}",
        nome_original="",
        palavras_chave=(data.get("keywords") or "").split(","),
        autores=autores,
        transformado_em_norma=(data.get("statusProposicao", {}).get("codSituacao") == 1140),
        em_tramitacao=(
            data.get("statusProposicao", {}).get("codSituacao") not in
            [923, 930, 941, 950, 1140, 1222, 1230, 1285, 1292]
        ),
        data_apresentacao=data.get("dataApresentacao", ""),
        casa_origem=Casa.CAMARA if autores_json and autores_json[0].get("codTipo") not in [20000, 21000, 22000, 81003, 81004] else Casa.SENADO,
        ementa=data.get("ementa", ""),
        classificacoes=[]
    )
    return projeto_lei.model_dump(mode="json")
if __name__ == "__main__":

    start_time = time.time()

    # Processar senado
    directory_path = Path("detalhes_pls_senado")
    senado_files = list(directory_path.iterdir())
    with ProcessPoolExecutor(max_workers=4) as executor:
        pls_senado = list(tqdm(executor.map(processa_senado, senado_files), total=len(senado_files)))

    with open("senado_norm.json", "w") as f:
        json.dump(pls_senado, f)

    # Processar câmara
    directory_path = Path("detalhes_pls_camara")
    camara_files = list(directory_path.iterdir())
    with ProcessPoolExecutor(max_workers=4) as executor:
        pls_camara = list(tqdm(executor.map(processa_camara, camara_files), total=len(camara_files)))

    with open("camara_norm.json", "w") as f:
        json.dump(pls_camara, f)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")