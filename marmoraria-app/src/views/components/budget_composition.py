# src/views/components/budget_composition.py
from dataclasses import dataclass, field
from typing import List, Literal, Optional

# Define os lados possíveis para acabamentos e encaixes
Side = Literal["esquerda", "direita", "frente", "fundo"]

@dataclass
class Abertura:
    tipo: Literal["bojo", "cooktop"]
    largura: float
    profundidade: float
    x_relativo: float  # Posição do eixo (0 a 1)
    y_relativo: float  # Posição vertical (0 a 1)

@dataclass
class BancadaPiece:
    nome: str
    largura: float
    profundidade: float
    material: str = ""
    preco_m2: float = 0.0
    preco_total: float = 0.0
    aberturas: List[Abertura] = field(default_factory=list)
    
    # Lógica para o "L" e "U"
    lado_encaixe: Optional[Side] = None  # Onde esta peça se "cola" na anterior
    
    def area_m2(self) -> float:
        return round(self.largura * self.profundidade, 4)

class CompositionManager:
    """Gerencia o conjunto de peças que formam uma bancada completa"""
    def __init__(self):
        self.pecas: List[BancadaPiece] = []

    def adicionar_peca(self, peca: BancadaPiece):
        self.pecas.append(peca)

    def limpar(self):
        self.pecas = []

    def calcular_total_composicao(self) -> float:
        return sum(p.preco_total for p in self.pecas)