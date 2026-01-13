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
        self._atualizar_calculos()

    def build(self):
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", on_change=self._atualizar_calculos)
        self.dd_pedra = ft.Dropdown(label="Material", on_change=self._atualizar_calculos)
        self.input_larg = ft.TextField(label="Largura (m)", value="1.00", on_change=self._atualizar_calculos)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos)
        self.input_ml_valor = ft.TextField(label="Mão de Obra (ML)", value="130", on_change=self._atualizar_calculos)

        self.cb_saia_frente = ft.Checkbox(label="Saia Frente", value=True, on_change=self._atualizar_calculos)
        self.cb_rodo_fundo = ft.Checkbox(label="Rodo Fundo", value=True, on_change=self._atualizar_calculos)

        self.canvas_area = ft.Container(height=320, alignment=ft.alignment.center)
        self.txt_total_res = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        return ft.Container(
            padding=15, bgcolor=COLOR_WHITE,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Orçamento Técnico", size=22, weight="bold"),
                    self.txt_ambiente, self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof]),
                    self.input_ml_valor,
                    ft.Row([self.cb_saia_frente, self.cb_rodo_fundo]),
                    ft.Divider(),
                    self.canvas_area,
                    ft.Row([ft.Text("Total:"), self.txt_total_res], alignment="spaceBetween"),
                    ft.ElevatedButton("Salvar", on_click=self._salvar, expand=True, height=50)
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
            lados_s = ["frente"] if self.cb_saia_frente.value else []
            peca.saia = Saia(altura=0.04, lados=lados_s)

            self.composition.pecas = [peca]
            # FORÇA O RECARREGAMENTO DO CANVAS
            self.canvas_area.content = BudgetCanvas(self.composition)
            
            p_m2 = self.pedra_selecionada["preco_m2"] if self.pedra_selecionada else 0
            total = (peca.area_m2() * p_m2) + (peca.metro_linear_saia() * v_ml)
            
            self.txt_total_res.value = f"R$ {total:,.2f}"
            self.update()
        except: pass

    def _salvar(self, e):
        if not self.pedra_selecionada: return
        
        # LIMPEZA TOTAL DO NÚMERO ANTES DE SALVAR
        clean_total = self.txt_total_res.value.replace("R$ ", "").replace(".", "").replace(",", ".")
        
        peca = self.composition.pecas[0]
        item = {
            "ambiente": self.txt_ambiente.value,
            "material": self.pedra_selecionada["nome"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "preco_total": float(clean_total) # AGORA SALVA O VALOR REAL
        }
        if self.on_save_item:
            self.on_save_item(item)