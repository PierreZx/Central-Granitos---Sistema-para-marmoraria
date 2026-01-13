import flet as ft
from src.services import firebase_service
from src.views.components.budget_composition import BancadaPiece, Saia, RodoBanca, CompositionManager
from src.views.components.budget_canvas import BudgetCanvas
from src.config import COLOR_PRIMARY, COLOR_WHITE, COLOR_TEXT, BORDER_RADIUS_LG

class BudgetCalculator(ft.UserControl):
    def __init__(self, page: ft.Page, item=None, on_save_item=None, on_cancel=None):
        super().__init__()
        self.page = page
        self.item_para_editar = item
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        
        self.composition = CompositionManager()
        self.pedras = []
        self.pedra_selecionada = None
        self._carregar_pedras()
        
    def _carregar_pedras(self):
        docs = firebase_service.get_collection("estoque")
        self.pedras = [
            {"id": d.get("id"), "nome": d["nome"], "preco_m2": float(d["preco_m2"])}
            for d in docs if "nome" in d and "preco_m2" in d
        ]

    def build(self):
        # 1. Definição dos Inputs
        self.txt_ambiente = ft.TextField(label="Ambiente (ex: Cozinha)", value="Geral", border_radius=10)
        
        self.dd_pedra = ft.Dropdown(
            label="Material",
            border_radius=10,
            options=[ft.dropdown.Option(key=p["id"], text=p["nome"]) for p in self.pedras],
            on_change=self._atualizar_calculos
        )

        self.input_larg = ft.TextField(label="Comprimento (m)", value="1.00", on_change=self._atualizar_calculos, expand=1)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos, expand=1)

        self.check_saia = ft.Checkbox(label="Possui Saia", value=True, on_change=self._atualizar_calculos)
        self.alt_saia = ft.TextField(label="Alt. Saia (m)", value="0.04", width=100, on_change=self._atualizar_calculos)
        
        self.check_rodo = ft.Checkbox(label="Possui Rodobanca", value=True, on_change=self._atualizar_calculos)
        self.alt_rodo = ft.TextField(label="Alt. Rodo (m)", value="0.10", width=100, on_change=self._atualizar_calculos)

        self.canvas_preview = ft.Container(
            content=ft.Text("Aguardando medidas...", color="grey"),
            alignment=ft.alignment.center,
            bgcolor="#f8f9fa",
            border=ft.border.all(1, "grey200"),
            border_radius=10,
            height=300,
            expand=True
        )

        # 2. Resumo de Valores (Sintaxe segura com controls explícitos)
        self.txt_res_area = ft.Text("0.00 m²", weight="bold")
        self.txt_res_preco = ft.Text("R$ 0.00", size=20, weight="bold", color=COLOR_PRIMARY)

        self.resumo_valores = ft.Column(
            spacing=5,
            controls=[
                ft.Row(controls=[ft.Text("Área Total:"), self.txt_res_area]),
                ft.Row(controls=[ft.Text("Preço Total:"), self.txt_res_preco])
            ]
        )

        if self.item_para_editar:
            self._preencher_edicao()

        # 3. Layout Final (Construção do Grid)
        coluna_esquerda = ft.Column(
            width=300,
            spacing=15,
            controls=[
                self.txt_ambiente,
                self.dd_pedra,
                ft.Row(controls=[self.input_larg, self.input_prof]),
                ft.Divider(),
                ft.Text("Acabamentos", weight="bold"),
                ft.Row(controls=[self.check_saia, self.alt_saia]),
                ft.Row(controls=[self.check_rodo, self.alt_rodo])
            ]
        )

        coluna_direita = ft.Column(
            expand=True,
            spacing=15,
            controls=[
                ft.Text("Visualização Técnica", weight="bold"),
                self.canvas_preview,
                self.resumo_valores,
                ft.Row(
                    alignment="end",
                    controls=[
                        ft.TextButton("Cancelar", on_click=self.on_cancel),
                        ft.ElevatedButton("Confirmar Peça", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar)
                    ]
                )
            ]
        )

        return ft.Container(
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_LG,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(controls=[
                        ft.Icon(ft.icons.CALCULATE_ROUNDED, color=COLOR_PRIMARY),
                        ft.Text("Calculadora Técnica de Pedras", size=20, weight="bold")
                    ]),
                    ft.Divider(),
                    ft.Row(
                        expand=True,
                        vertical_alignment="start",
                        controls=[
                            coluna_esquerda,
                            ft.VerticalDivider(width=1),
                            coluna_direita
                        ]
                    )
                ]
            )
        )

    def _preencher_edicao(self):
        it = self.item_para_editar
        self.txt_ambiente.value = it.get("ambiente", "Geral")
        self.input_larg.value = str(it.get("largura", 1.0))
        self.input_prof.value = str(it.get("profundidade", 0.6))
        for p in self.pedras:
            if p["nome"] == it.get("material"):
                self.dd_pedra.value = p["id"]
                self.pedra_selecionada = p
        self._atualizar_calculos()

    def _atualizar_calculos(self, e=None):
        try:
            larg = float(self.input_larg.value.replace(",", "."))
            prof = float(self.input_prof.value.replace(",", "."))
            peca = BancadaPiece(nome=self.txt_ambiente.value, largura=larg, profundidade=prof)
            if self.check_saia.value:
                peca.saia = Saia(altura=float(self.alt_saia.value), lados=["frente"])
            if self.check_rodo.value:
                peca.rodobanca = RodoBanca(altura=float(self.alt_rodo.value), lados=["fundo"])
            self.composition.pecas = [peca]
            self.canvas_preview.content = BudgetCanvas(self.composition)
            area = peca.area_m2()
            preco_m2 = self.pedra_selecionada["preco_m2"] if self.pedra_selecionada else 0
            total = (area * preco_m2) + (peca.metro_linear_saia() * 150)
            self.txt_res_area.value = f"{area:.2f} m²"
            self.txt_res_preco.value = f"R$ {total:,.2f}"
            self.update()
        except Exception as err:
            print(f"Erro no cálculo: {err}")

    def _salvar(self, e):
        if not self.dd_pedra.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecione um material!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.pedra_selecionada = next(p for p in self.pedras if p["id"] == self.dd_pedra.value)
        peca = self.composition.pecas[0]
        item_final = {
            "ambiente": self.txt_ambiente.value,
            "material": self.pedra_selecionada["nome"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "area": peca.area_m2(),
            "preco_total": float(self.txt_res_preco.value.replace("R$ ", "").replace(".", "").replace(",", "."))
        }
        if self.on_save_item:
            self.on_save_item(item_final)