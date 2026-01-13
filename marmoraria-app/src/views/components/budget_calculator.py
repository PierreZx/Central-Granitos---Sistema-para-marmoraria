import flet as ft
from src.services.firebase_service import firebase_db


# =========================
# CONFIGURAÇÕES GERAIS
# =========================
COLLECTION_PEDRAS = "estoque"
PRECO_METRO_LINEAR_PADRAO = 130.0


# =========================
# MODELO DE PEÇA
# =========================
class BancadaPeca:
    def __init__(self, comprimento: float, profundidade: float):
        self.comprimento = comprimento
        self.profundidade = profundidade

    @property
    def area(self) -> float:
        return self.comprimento * self.profundidade

    @property
    def metro_linear(self) -> float:
        # 🔥 Mão de obra é calculada SOMENTE pelo comprimento frontal
        return self.comprimento


# =========================
# FUNÇÃO DE CÁLCULO (DOMÍNIO)
# =========================
def calcular_bancada_reta(
    ambiente: str,
    material: str,
    comprimento: float,
    profundidade: float,
    preco_m2: float,
    preco_ml: float
) -> dict:
    area = comprimento * profundidade
    valor_material = area * preco_m2
    valor_mao_obra = comprimento * preco_ml
    preco_total = valor_material + valor_mao_obra

    return {
        "ambiente": ambiente,
        "material": material,
        "largura": comprimento,
        "profundidade": profundidade,
        "area": round(area, 2),
        "preco_material": round(valor_material, 2),
        "preco_mao_obra": round(valor_mao_obra, 2),
        "preco_total": round(preco_total, 2)
    }


# =========================
# COMPONENTE PRINCIPAL
# =========================
class BudgetCalculator(ft.UserControl):
    def __init__(self, page: ft.Page, on_save_item=None, on_cancel=None):
        super().__init__()
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel

        self.pedras = []
        self.pedra_selecionada = None

        self._carregar_pedras()

    # ---------------------
    # FIREBASE
    # ---------------------
    def _carregar_pedras(self):
        self.pedras.clear()
        docs = firebase_db.collection(COLLECTION_PEDRAS).stream()
        for doc in docs:
            data = doc.to_dict()
            if "nome" in data and "preco_m2" in data:
                self.pedras.append({
                    "id": doc.id,
                    "nome": data["nome"],
                    "preco_m2": float(data["preco_m2"]),
                })

    # ---------------------
    # CÁLCULO
    # ---------------------
    def _recalcular(self, _=None):
        if not self.pedra_selecionada:
            return

        try:
            comprimento = float(self.input_comprimento.value)
            profundidade = float(self.input_profundidade.value)
            preco_ml = float(self.input_preco_ml.value)
        except (ValueError, TypeError):
            return

        peca = BancadaPeca(comprimento, profundidade)

        custo_material = peca.area * self.pedra_selecionada["preco_m2"]
        custo_mao_obra = peca.metro_linear * preco_ml
        total = custo_material + custo_mao_obra

        self.txt_area.value = f"{peca.area:.2f} m²"
        self.txt_ml.value = f"{peca.metro_linear:.2f} m"
        self.txt_material.value = f"R$ {custo_material:,.2f}"
        self.txt_mao_obra.value = f"R$ {custo_mao_obra:,.2f}"
        self.txt_total.value = f"R$ {total:,.2f}"

        self.update()

    # ---------------------
    # UI
    # ---------------------
    def build(self):
        self.dropdown_pedra = ft.Dropdown(
            label="Material (estoque)",
            options=[
                ft.dropdown.Option(
                    key=p["id"],
                    text=f'{p["nome"]} - R$ {p["preco_m2"]:.2f}/m²'
                )
                for p in self.pedras
            ],
            on_change=self._on_pedra_change
        )

        self.input_comprimento = ft.TextField(
            label="Comprimento (m)",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular
        )

        self.input_profundidade = ft.TextField(
            label="Profundidade (m)",
            value="0.60",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular
        )

        self.input_preco_ml = ft.TextField(
            label="Preço por metro linear (mão de obra)",
            value=str(PRECO_METRO_LINEAR_PADRAO),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular
        )

        self.txt_area = ft.Text("0.00 m²")
        self.txt_ml = ft.Text("0.00 m")
        self.txt_material = ft.Text("R$ 0.00")
        self.txt_mao_obra = ft.Text("R$ 0.00")
        self.txt_total = ft.Text(
            "R$ 0.00",
            size=20,
            weight=ft.FontWeight.BOLD
        )

        return ft.Column(
            spacing=12,
            controls=[
                ft.Text("Cálculo de Bancada Reta", size=20, weight=ft.FontWeight.BOLD),

                self.dropdown_pedra,

                self.input_comprimento,
                self.input_profundidade,
                self.input_preco_ml,

                ft.Divider(),

                ft.Row([ft.Text("Área:"), self.txt_area]),
                ft.Row([ft.Text("Metro linear:"), self.txt_ml]),
                ft.Row([ft.Text("Material:"), self.txt_material]),
                ft.Row([ft.Text("Mão de obra:"), self.txt_mao_obra]),

                ft.Divider(),

                ft.Row([ft.Text("Total:"), self.txt_total]),

                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.TextButton("Cancelar", on_click=self.on_cancel),
                        ft.ElevatedButton("Salvar", on_click=lambda _: self._salvar())
                    ]
                )
            ]
        )

    # ---------------------
    # EVENTOS
    # ---------------------
    def _on_pedra_change(self, e):
        pedra_id = e.control.value
        self.pedra_selecionada = next(
            (p for p in self.pedras if p["id"] == pedra_id),
            None
        )
        self._recalcular()

    def _salvar(self):
        if not self.on_save_item or not self.pedra_selecionada:
            return

        try:
            comprimento = float(self.input_comprimento.value)
            profundidade = float(self.input_profundidade.value)
            preco_ml = float(self.input_preco_ml.value)
        except (ValueError, TypeError):
            return

        item = calcular_bancada_reta(
            ambiente="Ambiente",
            material=self.pedra_selecionada["nome"],
            comprimento=comprimento,
            profundidade=profundidade,
            preco_m2=self.pedra_selecionada["preco_m2"],
            preco_ml=preco_ml
        )

        self.on_save_item(item)
