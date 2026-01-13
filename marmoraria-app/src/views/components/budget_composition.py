# src/views/components/budget_composition.py

from dataclasses import dataclass, field
from typing import List, Literal, Optional

Side = Literal["esquerda", "direita", "frente", "fundo"]

@dataclass
class Saia:
    altura: float
    lados: List[Side]

@dataclass
class RodoBanca:
    altura: float
    lados: List[Side]

@dataclass
class Abertura:
    tipo: Literal["bojo", "cooktop"]
    largura: float
    profundidade: float
    x_relativo: float
    y_relativo: float

@dataclass
class BancadaPiece:
    nome: str
    largura: float
    profundidade: float
    material: str = ""
    preco_m2: float = 0.0
    saia: Optional[Saia] = None
    rodobanca: Optional[RodoBanca] = None
    aberturas: List[Abertura] = field(default_factory=list)
    encaixada_em: Optional[Side] = None
    x: float = 0.0
    y: float = 0.0

    def area_m2(self) -> float:
        return round(self.largura * self.profundidade, 4)

    def metro_linear_saia(self) -> float:
        if not self.saia:
            return 0.0
        total = 0.0
        if "frente" in self.saia.lados: total += self.largura
        if "fundo" in self.saia.lados: total += self.largura
        if "esquerda" in self.saia.lados: total += self.profundidade
        if "direita" in self.saia.lados: total += self.profundidade
        return round(total, 3)

class CompositionManager:
    def __init__(self):
        self.pecas: List[BancadaPiece] = []

    def adicionar_peca(self, peca: BancadaPiece):
        self.pecas.append(peca)

    def area_total(self) -> float:
        return round(sum(p.area_m2() for p in self.pecas), 4)