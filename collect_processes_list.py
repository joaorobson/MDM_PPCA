from datetime import datetime
from processes_collector import ProcessesCollector

URL_API_PROCESSOS_SENADO = "https://legis.senado.leg.br/dadosabertos/processo?siglaTipoDocumento={}&dataInicioApresentacao={}&dataFimApresentacao={}&v=1"
URL_API_PROCESSOS_CAMARA =  "https://dadosabertos.camara.leg.br/api/v2/proposicoes?siglaTipo=PL,PLP&dataApresentacaoInicio={}&dataApresentacaoFim={}"

collector = ProcessesCollector()

year_range = range(2000, 2025)

TIPOS_PROCESSOS = ["PROJETO_LEI_ORDINARIA", "PROJETO_LEI_COMPLEMENTAR"]

for tipo_processo in TIPOS_PROCESSOS:
    for year in year_range:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        print(start_date, end_date)

        data = collector.collect_sync(URL_API_PROCESSOS_SENADO.format(tipo_processo, start_date, end_date))
        collector.store_data(data, f"pls_senado/{tipo_processo}_{year}.json")
        break
    break

print(data)



