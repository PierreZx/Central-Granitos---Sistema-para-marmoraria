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
        # --- 1. CAMPOS DE ENTRADA (TOP) ---
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", border_radius=10)
        self.dd_pedra = ft.Dropdown(
            label="Material",
            border_radius=10,
            options=[ft.dropdown.Option(key=p["id"], text=p["nome"]) for p in self.pedras],
            on_change=self._atualizar_calculos
        )
        self.input_larg = ft.TextField(label="Comprimento (m)", value="1.00", on_change=self._atualizar_calculos, expand=True)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos, expand=True)

        # --- 2. ACABAMENTOS ---
        self.check_saia = ft.Checkbox(label="Saia", value=True, on_change=self._atualizar_calculos)
        self.alt_saia = ft.TextField(label="Alt. (m)", value="0.04", width=80, on_change=self._atualizar_calculos)
        self.check_rodo = ft.Checkbox(label="Rodo", value=True, on_change=self._atualizar_calculos)
        self.alt_rodo = ft.TextField(label="Alt. (m)", value="0.10", width=80, on_change=self._atualizar_calculos)

        # --- 3. ÁREA DE DESENHO (FIXA) ---
        self.canvas_container = ft.Container(
            content=ft.Text("Ajuste as medidas para ver o desenho", color="grey700"),
            alignment=ft.alignment.center,
            bgcolor="#f8f9fa",
            border=ft.border.all(1, "grey300"),
            border_radius=10,
            height=250, # Altura fixa para não sumir no mobile
        )

        # --- 4. RESUMO FINANCEIRO ---
        self.txt_res_area = ft.Text("0.00 m²", weight="bold", size=16)
        self.txt_res_preco = ft.Text("R$ 0.00", size=22, weight="bold", color=COLOR_PRIMARY)

        # Se for edição, carrega os dados
        if self.item_para_editar:
            self.page.run_task(self._preencher_edicao_atrasado)

        # MONTAGEM FINAL DA TELA
        return ft.Container(
            padding=15,
            bgcolor=COLOR_WHITE,
            content=ft.Column(
                tight=True,
                scroll=ft.ScrollMode.ALWAYS, # Scroll obrigatório para mobile
                controls=[
                    ft.Row([ft.Icon(ft.icons.CALCULATE), ft.Text("Calculadora Técnica", size=20, weight="bold")]),
                    ft.Divider(),
                    
                    # Seção de Medidas
                    self.txt_ambiente,
                    self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof], spacing=10),
                    
                    ft.Divider(),
                    ft.Text("Acabamentos", weight="bold"),
                    ft.Row([self.check_saia, self.alt_saia, self.check_rodo, self.alt_rodo], wrap=True),
                    
                    ft.Divider(),
                    ft.Text("Desenho Técnico", weight="bold"),
                    self.canvas_container,
                    
                    ft.Divider(),
                    ft.Column([
                        ft.Row([ft.Text("Área:"), self.txt_res_area], alignment="spaceBetween"),
                        ft.Row([ft.Text("Total:"), self.txt_res_preco], alignment="spaceBetween"),
                    ]),
                    
                    ft.Divider(),
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=self.on_cancel),
                        ft.ElevatedButton("Salvar Peça", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar, expand=True)
                    ], spacing=20),
                    ft.Container(height=50) # Espaço extra no final
                ]
            )
        )

    async def _preencher_edicao_atrasado(self):
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
            self.canvas_container.content = BudgetCanvas(self.composition)
            
            area = peca.area_m2()
            preco_m2 = self.pedra_selecionada["preco_m2"] if self.pedra_selecionada else 0
            # Regra de negócio: Pedra + Mão de obra (ML da saia * 150)
            total = (area * preco_m2) + (peca.metro_linear_saia() * 150)
            
            self.txt_res_area.value = f"{area:.2f} m²"
            self.txt_res_preco.value = f"R$ {total:,.2f}"
            self.update()
        except Exception as err:
            print(f"Erro cálculo: {err}")

    def _salvar(self, e):
        if not self.dd_pedra.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecione o material!"))
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