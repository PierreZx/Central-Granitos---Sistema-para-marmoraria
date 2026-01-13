# src/views/components/budget_calculator.py
import flet as ft
from src.services import firebase_service
from src.views.components.budget_composition import BancadaPiece, Saia, RodoBanca, CompositionManager, Abertura
from src.views.components.budget_canvas import BudgetCanvas
from src.config import COLOR_PRIMARY, COLOR_WHITE

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
        self.pedras = [{"id": d.get("id"), "nome": d["nome"], "preco_m2": float(d["preco_m2"])} for d in docs if "nome" in d]
        self.dd_pedra.options = [ft.dropdown.Option(key=p["id"], text=p["nome"]) for p in self.pedras]
        if self.item_para_editar: self._carregar_edicao()
        self.update()

    def build(self):
        self.dd_pedra = ft.Dropdown(label="Material", on_change=self._atualizar_calculos)
        self.input_larg = ft.TextField(label="Largura (m)", value="1.00", on_change=self._atualizar_calculos)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos)
        self.sw_bojo = ft.Switch(label="Bojo", on_change=self._atualizar_calculos)
        self.canvas_area = ft.Container(height=350, alignment=ft.alignment.center)
        self.txt_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        return ft.Container(
            padding=15, bgcolor=COLOR_WHITE,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS, # Scroll para o botão não sumir
                controls=[
                    ft.Text("Orçamento Técnico", size=22, weight="bold"),
                    self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof]),
                    ft.Row([self.sw_bojo]),
                    ft.Divider(),
                    self.canvas_area,
                    ft.Row([ft.Text("Investimento:"), self.txt_total], alignment="spaceBetween"),
                    ft.ElevatedButton("Salvar Peça", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar, expand=True, height=50),
                    ft.TextButton("Cancelar", on_click=self.on_cancel),
                    ft.Container(height=20)
                ]
            )
        )

    def _atualizar_calculos(self, e=None):
        try:
            if self.dd_pedra.value:
                self.pedra_selecionada = next(p for p in self.pedras if p["id"] == self.dd_pedra.value)
            peca = BancadaPiece(nome="Pia", largura=float(self.input_larg.value), profundidade=float(self.input_prof.value))
            if self.sw_bojo.value: peca.aberturas.append(Abertura("bojo", 0.50, 0.40, 0.5, 0.5))
            self.composition.pecas = [peca]
            self.canvas_area.content = BudgetCanvas(self.composition)
            
            p_m2 = self.pedra_selecionada["preco_m2"] if self.pedra_selecionada else 0
            total = peca.area_m2() * p_m2
            self.txt_total.value = f"R$ {total:,.2f}"
            self.update()
        except: pass

    def _salvar(self, e):
        if not self.pedra_selecionada: return
        clean_total = self.txt_total.value.replace("R$ ", "").replace(".", "").replace(",", ".")
        peca = self.composition.pecas[0]
        item = {
            "ambiente": "Cozinha",
            "material": self.pedra_selecionada["nome"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "preco_total": float(clean_total)
        }
        if self.on_save_item: self.on_save_item(item)