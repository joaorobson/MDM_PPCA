from pathlib import Path
import json
from models import Autor, Casa, Classificacao, ProjetoLei
import time
from tqdm import tqdm
# SENADO
start_time = time.time()

""" directory_path = Path("detalhes_pls_senado")
pls_senado = []
senado_files = [str(p) for p in directory_path.iterdir() if p.is_file()][:1000]

for file_path in tqdm(senado_files):
    file_path = Path(file_path)
    data = json.loads(file_path.read_text())[0]
    projeto_lei = ProjetoLei(
        id=data["id"],
        nome=data["identificacao"],
        nome_original=data["identificacaoProcessoInicial"],
        palavras_chave=data["documento"]["indexacao"].split(","),
        autores=[Autor(nome=autor["autor"], tipo=autor["descricaoTipo"], uf=autor.get("uf", ""), sexo=autor.get("sexo","")) for autor in data["autoriaIniciativa"]],
        transformado_em_norma=True if data["normaGerada"] else False,
        em_tramitacao=True if data["tramitando"] == "Sim" else False,
        data_apresentacao=data["documento"]["dataApresentacao"],
        casa_origem=Casa.CAMARA if data["siglaCasaIniciadora"] == "CD" else Casa.SENADO,
        ementa=data["conteudo"]["ementa"],
        classificacoes=[Classificacao(descricao=c["descricao"], descricao_hierarquica=c["descricaoHierarquia"]) for c in data["classificacoes"]])
    pls_senado.append(projeto_lei.model_dump(mode="json"))

json.dump(pls_senado, open('senado_norm.json', 'w')) """

directory_path = Path("detalhes_pls_camara")

def get_autores(nomes_autores, detalhes_autores):
    autores = []
    for autor in detalhes_autores:
        autor_info_gerais = [nome_autor for nome_autor in nomes_autores if nome_autor["uri"] == autor["uri"]]
        if len(autor_info_gerais) == 1:
            autor_info_gerais = autor_info_gerais[0]
        #print(autor_info_gerais["nome"])
        if "deputados" in autor["uri"]:
            autores.append(Autor(nome=autor_info_gerais["nome"], 
                                tipo=autor_info_gerais["tipo"], 
                                uf=autor["ultimoStatus"]["siglaUf"], 
                                sexo=autor["sexo"]))
        elif "orgaos" in autor["uri"]:
            if "SENADO FEDERAL" in autor_info_gerais["nome"]:
                autores.append(Autor(nome=autor_info_gerais["nome"].replace("SENADO FEDERAL - ", ""), 
                        tipo="Senador(a)", 
                        uf="", 
                        sexo=""))
            else:   
                autores.append(Autor(nome=autor["apelido"], 
                        tipo=autor["tipoOrgao"], 
                        uf="", 
                        sexo=""))
    return autores


pls_camara = []
camara_files = [str(p) for p in directory_path.iterdir() if p.is_file()]
for file_path in (pbar:= tqdm(camara_files)):
    pbar.set_postfix_str(file_path)
    file_path = Path(file_path)

    data = json.loads(file_path.read_text())[0]
    autores_json = json.load(open(f"autores_pls_camara/{data['id']}.json", 'r'))
    detalhes_autores_json = json.load(open(f"detalhes_autores_pls_camara/{data['id']}.json", 'r'))
    autores = get_autores(autores_json, detalhes_autores_json)
    keywords = data["keywords"]
    projeto_lei = ProjetoLei(
        id=data["id"],
        nome=f"{data['siglaTipo']} {data['numero']}/{data['ano']}",
        nome_original="",
        palavras_chave=data["keywords"].split(",") if data["keywords"] != None else [],
        autores=autores,
        transformado_em_norma=True if data["statusProposicao"]["codSituacao"] == 1140 else False,
        em_tramitacao=False if data["statusProposicao"]["codSituacao"]  in [923, 930, 941, 950, 1140, 1222, 1230, 1285, 1292] else True,
        data_apresentacao=data["dataApresentacao"],
        casa_origem=Casa.CAMARA if autores_json[0]["codTipo"] not in [20000, 21000, 22000, 81003, 81004] else Casa.SENADO,
        ementa=data["ementa"],
        classificacoes=[]) # consultar temas em /proposicoes/2317637/temas
    pls_camara.append(projeto_lei.model_dump(mode="json"))
json.dump(pls_camara, open('camara_norm_2.json', 'w'))


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")