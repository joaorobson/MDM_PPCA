from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class Casa(Enum):
    CAMARA = "Câmara dos Deputados"
    SENADO = "Senado Federal"

class Autor(BaseModel):
    nome: str
    tipo: str
    uf: str
    sexo: str

class Classificacao(BaseModel):
    descricao: str
    descricao_hierarquica: str


class ProjetoLei(BaseModel):
    id: int
    nome: str
    nome_original: str
    palavras_chave: list
    autores: List[Autor]
    transformado_em_norma: bool
    em_tramitacao: bool
    data_apresentacao: datetime
    casa_origem: Casa
    ementa: str
    classificacoes: Optional[List[Classificacao]] = []
