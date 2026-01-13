# src/views/components/budget_calculator.py

import flet as ft
from src.services import firebase_service
from src.views.components.budget_composition import BancadaPiece, Saia, RodoBanca, CompositionManager, Abertura
from src.views.components.budget_canvas import BudgetCanvas
from src.config import COLOR_PRIMARY, COLOR_WHITE, BORDER_RADIUS_LG

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
        # --- INPUTS PRINCIPAIS ---
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", border_radius=10)
        self.dd_pedra = ft.Dropdown(
            label="Material do Estoque",
            options=[ft.dropdown.Option(key=p["id"], text=p["nome"]) for p in self.pedras],
            on_change=self._atualizar_calculos
        )
        self.input_larg = ft.TextField(label="Largura (m)", value="1.00", on_change=self._atualizar_calculos, expand=True)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos, expand=True)
        self.input_ml_valor = ft.TextField(label="Valor Mão de Obra (ML)", value="130", on_change=self._atualizar_calculos, width=150)

        # --- SELEÇÃO DE LADOS ---
        self.cb_saia_frente = ft.Checkbox(label="Saia Frente", value=True, on_change=self._atualizar_calculos)
        self.cb_saia_esq = ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos)
        self.cb_saia_dir = ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos)
        
        self.cb_rodo_fundo = ft.Checkbox(label="Rodo Fundo", value=True, on_change=self._atualizar_calculos)
        self.cb_rodo_esq = ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos)
        self.cb_rodo_dir = ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos)

        # --- FUROS ---
        self.sw_bojo = ft.Switch(label="Furo de Bojo", value=False, on_change=self._atualizar_calculos)
        self.sw_cook = ft.Switch(label="Furo Cooktop", value=False, on_change=self._atualizar_calculos)

        # --- ÁREA VISUAL ---
        self.canvas_container = ft.Container(
            content=ft.Text("Ajuste os dados..."),
            height=350, bgcolor="#f8f9fa", border_radius=10, border=ft.border.all(1, "grey300")
        )

        self.txt_res_area = ft.Text("0.00 m²", size=16, weight="bold")
        self.txt_res_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        if self.item_para_editar:
            self.page.run_task(self._carregar_edicao)

        return ft.Container(
            padding=15,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Orçamento Técnico", size=24, weight="bold"),
                    self.txt_ambiente,
                    self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof, self.input_ml_valor]),
                    
                    ft.Divider(),
                    ft.Text("Lados com Acabamento (Saia)", weight="bold"),
                    ft.Row([self.cb_saia_frente, self.cb_saia_esq, self.cb_saia_dir]),
                    
                    ft.Text("Lados com Parede (Rodobanca)", weight="bold"),
                    ft.Row([self.cb_rodo_fundo, self.cb_rodo_esq, self.cb_rodo_dir]),

                    ft.Divider(),
                    ft.Row([self.sw_bojo, self.sw_cook]),

                    ft.Divider(),
                    self.canvas_container,
                    
                    ft.Container(
                        padding=15, bgcolor="grey100", border_radius=10,
                        content=ft.Column([
                            ft.Row([ft.Text("Área da Pedra:"), self.txt_res_area], alignment="spaceBetween"),
                            ft.Row([ft.Text("Total Estimado:"), self.txt_res_total], alignment="spaceBetween"),
                        ])
                    ),
                    
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=self.on_cancel),
                        ft.ElevatedButton("Salvar Orçamento", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar, expand=True)
                    ], spacing=20),
                    ft.Container(height=40)
                ]
            )
        )

    async def _carregar_edicao(self):
        it = self.item_para_editar
        self.txt_ambiente.value = it.get("ambiente", "")
        self.input_larg.value = str(it.get("largura", 1.0))
        self.input_prof.value = str(it.get("profundidade", 0.6))
        # Selecionar pedra
        for p in self.pedras:
            if p["nome"] == it.get("material"):
                self.dd_pedra.value = p["id"]
        self._atualizar_calculos()

    def _atualizar_calculos(self, e=None):
        try:
            larg = float(self.input_larg.value or 0)
            prof = float(self.input_prof.value or 0)
            v_ml = float(self.input_ml_valor.value or 0)

            peca = BancadaPiece(nome="Principal", largura=larg, profundidade=prof)
            
            # Lados Saia
            lados_s = []
            if self.cb_saia_frente.value: lados_s.append("frente")
            if self.cb_saia_esq.value: lados_s.append("esquerda")
            if self.cb_saia_dir.value: lados_s.append("direita")
            peca.saia = Saia(altura=0.04, lados=lados_s)

            # Lados Rodo
            lados_r = []
            if self.cb_rodo_fundo.value: lados_r.append("fundo")
            if self.cb_rodo_esq.value: lados_r.append("esquerda")
            if self.cb_rodo_dir.value: lados_r.append("direita")
            peca.rodobanca = RodoBanca(altura=0.10, lados=lados_r)

            # Aberturas
            if self.sw_bojo.value:
                peca.aberturas.append(Abertura("bojo", 0.50, 0.40, 0.4, 0.5))
            if self.sw_cook.value:
                peca.aberturas.append(Abertura("cooktop", 0.55, 0.45, 0.8, 0.5))

            self.composition.pecas = [peca]
            self.canvas_container.content = BudgetCanvas(self.composition)

            # Cálculo Financeiro
            preco_m2 = 0
            if self.dd_pedra.value:
                preco_m2 = next(p["preco_m2"] for p in self.pedras if p["id"] == self.dd_pedra.value)
            
            custo_material = peca.area_m2() * preco_m2
            custo_mao_obra = peca.metro_linear_saia() * v_ml
            total = custo_material + custo_mao_obra

            self.txt_res_area.value = f"{peca.area_m2():.2f} m²"
            self.txt_res_total.value = f"R$ {total:,.2f}"
            self.update()
        except Exception as err:
            print(f"Erro: {err}")

    def _salvar(self, e):
        if not self.dd_pedra.value:
            return
        
        self.pedra_selecionada = next(p for p in self.pedras if p["id"] == self.dd_pedra.value)
        peca = self.composition.pecas[0]
        
        item_final = {
            "ambiente": self.txt_ambiente.value,
            "material": self.pedra_selecionada["nome"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "area": peca.area_m2(),
            "preco_total": float(self.txt_res_total.value.replace("R$ ", "").replace(".", "").replace(",", "."))
        }
        if self.on_save_item:
            self.on_save_item(item_final)