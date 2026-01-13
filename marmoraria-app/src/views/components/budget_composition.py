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
    x_relativo: float  # 0 a 1, posição relativa dentro da peça
    y_relativo: float  # 0 a 1, posição relativa dentro da peça

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
    x: float = 0  # coordenada x para desenho
    y: float = 0  # coordenada y para desenho

    def area_m2(self) -> float:
        """Calcula a área em m² da peça"""
        return round(self.largura * self.profundidade, 4)

    def metro_linear_saia(self) -> float:
        """Calcula o perímetro da saia"""
        if not self.saia: 
            return 0.0
        total = 0.0
        if "frente" in self.saia.lados: total += self.largura
        if "fundo" in self.saia.lados: total += self.largura
        if "esquerda" in self.saia.lados: total += self.profundidade
        if "direita" in self.saia.lados: total += self.profundidade
        return round(total, 3)

class CompositionManager:
    """Gerencia múltiplas peças de bancada"""
    def __init__(self):
        self.pecas: List[BancadaPiece] = []

    def add_peca(self, peca: BancadaPiece):
        self.pecas.append(peca)

    def clear(self):
        self.pecas.clear()
