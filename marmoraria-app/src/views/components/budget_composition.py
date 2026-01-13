# src/views/components/budget_composition.py
from dataclasses import dataclass, field
from typing import List, Literal, Optional

# Definição dos 4 lados possíveis para acabamentos
Side = Literal["esquerda", "direita", "frente", "fundo"]

@dataclass
class Acabamento:
    altura: float
    lados: List[Side]

@dataclass
class BancadaPiece:
    nome: str
    largura: float        # Comprimento (m)
    profundidade: float   # Largura/Prof (m)
    material: str = ""
    preco_m2: float = 0.0
    valor_ml: float = 0.0  # Preço por metro linear
    saia: Optional[Acabamento] = None
    rodobanca: Optional[Acabamento] = None

    def area_m2(self) -> float:
        """Calcula a área total da pedra"""
        return round(self.largura * self.profundidade, 4)

    def total_ml_acabamento(self) -> float:
        """Soma o metro linear de todos os lados que possuem Saia ou Rodo"""
        total = 0.0
        # Usamos um conjunto para não cobrar duas vezes se o lado tiver saia E rodo
        lados_ativos = set()
        if self.saia: lados_ativos.update(self.saia.lados)
        if self.rodobanca: lados_ativos.update(self.rodobanca.lados)
        
        for lado in lados_ativos:
            if lado in ["frente", "fundo"]: total += self.largura
            if lado in ["esquerda", "direita"]: total += self.profundidade
        return round(total, 3)

class CompositionManager:
    def __init__(self):
        self.pecas: List[BancadaPiece] = []