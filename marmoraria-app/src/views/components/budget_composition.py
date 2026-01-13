# src/views/components/budget_composition.py
from dataclasses import dataclass, field
from typing import List, Literal, Optional

# Definição dos lados para acabamentos independentes
Side = Literal["esquerda", "direita", "frente", "fundo"]

@dataclass
class Acabamento:
    """Define altura e em quais lados o acabamento (Saia ou Rodo) será aplicado"""
    altura: float
    lados: List[Side]

@dataclass
class Abertura:
    """Define o tipo de furo, tamanho e a posição exata (eixo) na peça"""
    tipo: Literal["bojo", "cooktop"]
    largura: float
    profundidade: float
    # Distância do eixo (centro do furo) em relação às bordas (em metros)
    distancia_esquerda: float 
    distancia_fundo: float

@dataclass
class BancadaPiece:
    """A peça principal com todas as propriedades técnicas para desenho e cálculo"""
    nome: str
    largura: float        # Medida X total em metros
    profundidade: float   # Medida Y total em metros
    material: str = ""
    preco_m2: float = 0.0
    valor_ml: float = 0.0  # Valor da mão de obra por metro linear de acabamento
    
    # Acabamentos independentes por lado
    saia: Optional[Acabamento] = None
    rodobanca: Optional[Acabamento] = None
    
    # Lista de furos (podem ser vários bojos ou cooktops)
    aberturas: List[Abertura] = field(default_factory=list)

    def area_m2(self) -> float:
        """Calcula a área líquida da pedra em metros quadrados"""
        return round(self.largura * self.profundidade, 4)

    def calcular_perimetro_acabamento(self) -> float:
        """Calcula o total de metros lineares que receberão acabamento (Saia ou Rodo)"""
        total = 0.0
        # Criamos um set de lados que possuem algum tipo de acabamento para não cobrar duas vezes o mesmo lado
        lados_com_trabalho = set()
        if self.saia:
            lados_com_trabalho.update(self.saia.lados)
        if self.rodobanca:
            lados_com_trabalho.update(self.rodobanca.lados)
            
        for lado in lados_com_trabalho:
            if lado in ["frente", "fundo"]:
                total += self.largura
            if lado in ["esquerda", "direita"]:
                total += self.profundidade
        return round(total, 3)

class CompositionManager:
    """Gerenciador para suportar bancadas compostas (ex: Formato em L)"""
    def __init__(self):
        self.pecas: List[BancadaPiece] = []

    def adicionar_peca(self, peca: BancadaPiece):
        self.pecas.append(peca)

    def area_total(self) -> float:
        return round(sum(p.area_m2() for p in self.pecas), 4)

    def custo_total_pecas(self) -> float:
        total = 0.0
        for p in self.pecas:
            custo_material = p.area_m2() * p.preco_m2
            custo_mao_obra = p.calcular_perimetro_acabamento() * p.valor_ml
            total += (custo_material + custo_mao_obra)
        return round(total, 2)