# src/views/components/budget_composition.py

class Saia:
    def __init__(self, altura: float = 0.04, lados: list = None):
        self.altura = altura
        self.lados = lados or ["frente"] # Lados onde haverá saia (acabamento)

class RodoBanca:
    def __init__(self, altura: float = 0.10, lados: list = None):
        self.altura = altura
        self.lados = lados or ["fundo"] # Lados onde haverá rodobanca (parede)

class BancadaPiece:
    def __init__(self, nome: str, largura: float, profundidade: float, material: str = ""):
        self.nome = nome
        self.largura = largura  # Em metros
        self.profundidade = profundidade  # Em metros
        self.material = material
        self.saia = None
        self.rodobanca = None
        
        # Para o Canvas Interativo (posicionamento na tela)
        self.x = 0
        self.y = 0

    def area_m2(self) -> float:
        """Calcula a área da pedra principal."""
        return self.largura * self.profundidade

    def metro_linear_saia(self) -> float:
        """Calcula o total de metros lineares de saia baseado nos lados escolhidos."""
        total = 0
        if self.saia:
            if "frente" in self.saia.lados: total += self.largura
            if "esquerda" in self.saia.lados: total += self.profundidade
            if "direita" in self.saia.lados: total += self.profundidade
        return total

    def area_rodobanca(self) -> float:
        """Calcula a área total das rodobancas (que também consomem material)."""
        total_ml = 0
        if self.rodobanca:
            if "fundo" in self.rodobanca.lados: total_ml += self.largura
            if "esquerda" in self.rodobanca.lados: total_ml += self.profundidade
            if "direita" in self.rodobanca.lados: total_ml += self.profundidade
            return total_ml * self.rodobanca.altura
        return 0

class CompositionManager:
    """Gerencia a lista de peças que formam uma bancada (ex: L ou U)."""
    def __init__(self):
        self.pecas = []

    def adicionar_peca(self, peca: BancadaPiece):
        self.pecas.append(peca)

    def calcular_total_area(self) -> float:
        """Soma a área de todas as peças e suas rodobancas."""
        return sum(p.area_m2() + p.area_rodobanca() for p in self.pecas)