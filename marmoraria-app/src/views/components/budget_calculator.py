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
        
    def did_mount(self):
        self._carregar_pedras()

    def _carregar_pedras(self):
        docs = firebase_service.get_collection("estoque")
        self.pedras = [
            {"id": d.get("id"), "nome": d["nome"], "preco_m2": float(d["preco_m2"])}
            for d in docs if "nome" in d and "preco_m2" in d
        ]
        self.dd_pedra.options = [ft.dropdown.Option(key=p["id"], text=p["nome"]) for p in self.pedras]
        
        if self.item_para_editar:
            self._carregar_edicao()
        
        self.update()

    def _carregar_edicao(self):
        it = self.item_para_editar
        self.txt_ambiente.value = it.get("ambiente", "Cozinha")
        self.input_larg.value = str(it.get("largura", 1.0))
        self.input_prof.value = str(it.get("profundidade", 0.6))
        for p in self.pedras:
            if p["nome"] == it.get("material"):
                self.dd_pedra.value = p["id"]
                self.pedra_selecionada = p
        self._atualizar_calculos()

    def build(self):
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", border_radius=10, on_change=self._atualizar_calculos)
        self.dd_pedra = ft.Dropdown(label="Material do Estoque", border_radius=10, on_change=self._atualizar_calculos)
        self.input_larg = ft.TextField(label="Largura (m)", value="1.00", on_change=self._atualizar_calculos, expand=1)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos, expand=1)
        self.input_ml_valor = ft.TextField(label="Valor Mão de Obra (ML)", value="130", on_change=self._atualizar_calculos, width=120)

        self.cb_saia_frente = ft.Checkbox(label="Frente", value=True, on_change=self._atualizar_calculos)
        self.cb_saia_esq = ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos)
        self.cb_saia_dir = ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos)
        self.cb_rodo_fundo = ft.Checkbox(label="Fundo", value=True, on_change=self._atualizar_calculos)
        self.cb_rodo_esq = ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos)
        self.cb_rodo_dir = ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos)

        self.sw_bojo = ft.Switch(label="Furo Bojo", value=False, on_change=self._atualizar_calculos)
        self.sw_cook = ft.Switch(label="Furo Cooktop", value=False, on_change=self._atualizar_calculos)

        self.canvas_area = ft.Container(content=ft.Text("Aguardando material...", color="grey"), height=320, bgcolor="#F8F9FA", border_radius=10, border=ft.border.all(1, "grey300"), alignment=ft.alignment.center)
        self.txt_area_res = ft.Text("0.00 m²", weight="bold")
        self.txt_total_res = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        return ft.Container(
            padding=15, bgcolor=COLOR_WHITE,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Configuração Técnica", size=22, weight="bold"),
                    self.txt_ambiente, self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof, self.input_ml_valor], spacing=10),
                    ft.Divider(),
                    ft.Text("Lados com Saia (Azul)", weight="bold", size=12),
                    ft.Row([self.cb_saia_frente, self.cb_saia_esq, self.cb_saia_dir]),
                    ft.Text("Lados com Rodobanca (Vermelho)", weight="bold", size=12),
                    ft.Row([self.cb_rodo_fundo, self.cb_rodo_esq, self.cb_rodo_dir]),
                    ft.Divider(),
                    ft.Row([self.sw_bojo, self.sw_cook], alignment="center"),
                    ft.Divider(),
                    ft.Text("Desenho em Planta", weight="bold"),
                    self.canvas_area,
                    ft.Container(
                        padding=20, bgcolor="grey100", border_radius=10,
                        content=ft.Column([
                            ft.Row([ft.Text("Área da Pedra:"), self.txt_area_res], alignment="spaceBetween"),
                            ft.Row([ft.Text("Investimento Total:"), self.txt_total_res], alignment="spaceBetween"),
                        ])
                    ),
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=self.on_cancel),
                        ft.ElevatedButton("Salvar Peça", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar, expand=True, height=50)
                    ], spacing=20),
                    ft.Container(height=30)
                ]
            )
        )

    def _atualizar_calculos(self, e=None):
        try:
            if self.dd_pedra.value:
                self.pedra_selecionada = next((p for p in self.pedras if p["id"] == self.dd_pedra.value), None)

            larg = float(self.input_larg.value or 0)
            prof = float(self.input_prof.value or 0)
            v_ml = float(self.input_ml_valor.value or 0)

            peca = BancadaPiece(nome="Pia", largura=larg, profundidade=prof)
            lados_s = []
            if self.cb_saia_frente.value: lados_s.append("frente")
            if self.cb_saia_esq.value: lados_s.append("esquerda")
            if self.cb_saia_dir.value: lados_s.append("direita")
            peca.saia = Saia(altura=0.04, lados=lados_s)
            
            lados_r = []
            if self.cb_rodo_fundo.value: lados_r.append("fundo")
            if self.cb_rodo_esq.value: lados_r.append("esquerda")
            if self.cb_rodo_dir.value: lados_r.append("direita")
            peca.rodobanca = RodoBanca(altura=0.10, lados=lados_r)

            if self.sw_bojo.value: peca.aberturas.append(Abertura("bojo", 0.50, 0.40, 0.5, 0.5))
            if self.sw_cook.value: peca.aberturas.append(Abertura("cooktop", 0.55, 0.45, 0.8, 0.5))

            self.composition.pecas = [peca]
            self.canvas_area.content = BudgetCanvas(self.composition)
            
            p_m2 = self.pedra_selecionada["preco_m2"] if self.pedra_selecionada else 0
            # Corrigido cálculo: (Área * Preço m2) + (Metro Linear Saia * Preço ML)
            total = (peca.area_m2() * p_m2) + (peca.metro_linear_saia() * v_ml)
            
            self.txt_area_res.value = f"{peca.area_m2():.2f} m²"
            self.txt_total_res.value = f"R$ {total:,.2f}"
            self.update()
        except Exception as err:
            print(f"Erro Cálculo: {err}")

    def _salvar(self, e):
        if not self.pedra_selecionada:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecione um material!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Garante que o valor final seja salvo como número
        valor_final = float(self.txt_total_res.value.replace("R$ ", "").replace(".", "").replace(",", "."))
        
        peca = self.composition.pecas[0]
        item = {
            "ambiente": self.txt_ambiente.value,
            "material": self.pedra_selecionada["nome"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "area": peca.area_m2(),
            "preco_total": valor_final
        }
        if self.on_save_item:
            self.on_save_item(item)