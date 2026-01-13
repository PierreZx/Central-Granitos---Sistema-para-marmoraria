from dataclasses import dataclass, field
from typing import List, Literal, Optional

Side = Literal["esquerda", "direita", "frente", "fundo"]

# =========================
# MODELOS BASE
# =========================

@dataclass
class Saia:
    altura: float  # metros
    lados: List[Side]

    def metro_linear(self, largura: float, profundidade: float) -> float:
        total = 0.0
        if "frente" in self.lados:
            total += largura
        if "fundo" in self.lados:
            total += largura
        if "esquerda" in self.lados:
            total += profundidade
        if "direita" in self.lados:
            total += profundidade
        return round(total, 3)


@dataclass
class RodoBanca:
    altura: float
    lados: List[Side]

    def metro_linear(self, largura: float, profundidade: float) -> float:
        total = 0.0
        if "frente" in self.lados:
            total += largura
        if "fundo" in self.lados:
            total += largura
        if "esquerda" in self.lados:
            total += profundidade
        if "direita" in self.lados:
            total += profundidade
        return round(total, 3)


@dataclass
class Abertura:
    tipo: Literal["bojo", "cooktop"]
    largura: float
    profundidade: float
    offset_x: float  # distância da esquerda
    offset_y: float  # distância do fundo


# =========================
# PEÇA DE BANCADA
# =========================

@dataclass
class BancadaPiece:
    nome: str
    largura: float        # metros
    profundidade: float   # metros
    saia: Optional[Saia] = None
    rodobanca: Optional[RodoBanca] = None
    aberturas: List[Abertura] = field(default_factory=list)
    encaixada_em: Optional[Side] = None

    def area_m2(self) -> float:
        return round(self.largura * self.profundidade, 4)

    def perimetro(self) -> float:
        return round(2 * (self.largura + self.profundidade), 3)

    def metro_linear_saia(self) -> float:
        if not self.saia:
            return 0.0
        return self.saia.metro_linear(self.largura, self.profundidade)

    def metro_linear_rodobanca(self) -> float:
        if not self.rodobanca:
            return 0.0
        return self.rodobanca.metro_linear(self.largura, self.profundidade)

    def validar(self) -> List[str]:
        erros = []

        if self.largura <= 0 or self.profundidade <= 0:
            erros.append(f"{self.nome}: medidas inválidas")

        # Se possui saia em todos os lados, não pode estar encaixada
        if self.saia and set(self.saia.lados) == {"esquerda", "direita", "frente", "fundo"}:
            if self.encaixada_em:
                erros.append(
                    f"{self.nome}: possui saia em todos os lados e está encaixada ({self.encaixada_em})"
                )

        # Validar aberturas
        for a in self.aberturas:
            if a.offset_x + a.largura > self.largura:
                erros.append(f"{self.nome}: abertura {a.tipo} ultrapassa largura")
            if a.offset_y + a.profundidade > self.profundidade:
                erros.append(f"{self.nome}: abertura {a.tipo} ultrapassa profundidade")

        return erros


# =========================
# COMPOSIÇÃO (L / U)
# =========================

class CompositionManager:
    def __init__(self):
        self.pecas: List[BancadaPiece] = []

    def adicionar_peca(self, peca: BancadaPiece):
        self.pecas.append(peca)

    def encaixar_peca(
        self,
        peca: BancadaPiece,
        referencia: Optional[BancadaPiece] = None,
        lado: Optional[Side] = None
    ):
        peca.encaixada_em = lado
        self.pecas.append(peca)

    def area_total(self) -> float:
        return round(sum(p.area_m2() for p in self.pecas), 4)

    def metro_linear_saia_total(self) -> float:
        return round(sum(p.metro_linear_saia() for p in self.pecas), 3)

    def metro_linear_rodobanca_total(self) -> float:
        return round(sum(p.metro_linear_rodobanca() for p in self.pecas), 3)

    def validar_composicao(self) -> List[str]:
        erros = []
        for p in self.pecas:
            erros.extend(p.validar())
        return erros

    def resumo_profissional(self) -> dict:
        return {
            "pecas": len(self.pecas),
            "area_total_m2": self.area_total(),
            "metro_linear_saia": self.metro_linear_saia_total(),
            "metro_linear_rodobanca": self.metro_linear_rodobanca_total(),
            "erros": self.validar_composicao()
        }


# =========================
# FUNÇÕES DE CÁLCULO (BANCADA L / U)
# =========================

def calcular_bancada_L(
    ambiente: str,
    material: str,
    lado_a: float,
    lado_b: float,
    profundidade: float,
    preco_m2: float,
    preco_ml: float = 130
) -> dict:
    area = (lado_a + lado_b) * profundidade
    ml_total = lado_a + lado_b
    preco_total = (area * preco_m2) + (ml_total * preco_ml)

    return {
        "ambiente": ambiente,
        "material": f"{material} (Bancada em L)",
        "largura": max(lado_a, lado_b),
        "profundidade": profundidade,
        "area": round(area, 2),
        "preco_total": round(preco_total, 2)
    }


def calcular_bancada_U(
    ambiente: str,
    material: str,
    lado_a: float,
    lado_b: float,
    lado_c: float,
    profundidade: float,
    preco_m2: float,
    preco_ml: float = 130
) -> dict:
    area = (lado_a + lado_b + lado_c) * profundidade
    ml_total = lado_a + lado_b + lado_c
    preco_total = (area * preco_m2) + (ml_total * preco_ml)

    return {
        "ambiente": ambiente,
        "material": f"{material} (Bancada em U)",
        "largura": max(lado_a, lado_b, lado_c),
        "profundidade": profundidade,
        "area": round(area, 2),
        "preco_total": round(preco_total, 2)
    }
