# src/views/components/budget_calculator.py
import flet as ft
from src.services import firebase_service
from src.views.components.budget_composition import BancadaPiece, Acabamento, Abertura, CompositionManager
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
        self.input_larg.value = str(it.get("largura", 2.40))
        self.input_prof.value = str(it.get("profundidade", 0.60))
        
        for p in self.pedras:
            if p["nome"] == it.get("material"):
                self.dd_pedra.value = p["id"]
        
        self._atualizar_calculos()

    def build(self):
        # --- INPUTS PRINCIPAIS ---
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", border_radius=10, on_change=self._atualizar_calculos)
        self.dd_pedra = ft.Dropdown(label="Material do Estoque", border_radius=10, on_change=self._atualizar_calculos)
        
        self.input_larg = ft.TextField(label="Comprimento Total (m)", value="2.40", on_change=self._atualizar_calculos, expand=True)
        self.input_prof = ft.TextField(label="Profundidade Total (m)", value="0.60", on_change=self._atualizar_calculos, expand=True)
        self.input_ml_valor = ft.TextField(label="Mão de Obra Acabamento (ML)", value="130", on_change=self._atualizar_calculos, width=150)

        # --- SELEÇÃO DE LADOS (SAIA) ---
        self.check_saia_frente = ft.Checkbox(label="Frente", value=True, on_change=self._atualizar_calculos)
        self.check_saia_fundo = ft.Checkbox(label="Fundo", on_change=self._atualizar_calculos)
        self.check_saia_esq = ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos)
        self.check_saia_dir = ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos)

        # --- SELEÇÃO DE LADOS (RODOBANCA) ---
        self.check_rodo_fundo = ft.Checkbox(label="Fundo", value=True, on_change=self._atualizar_calculos)
        self.check_rodo_esq = ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos)
        self.check_rodo_dir = ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos)

        # --- CONFIGURAÇÃO TÉCNICA DE FUROS (EIXOS) ---
        self.sw_bojo = ft.Switch(label="Incluir Bojo", value=False, on_change=self._atualizar_calculos)
        self.in_bojo_x = ft.TextField(label="Eixo Cuba (m da Esq.)", value="0.86", on_change=self._atualizar_calculos, width=120)
        
        self.sw_cook = ft.Switch(label="Incluir Cooktop", value=False, on_change=self._atualizar_calculos)
        self.in_cook_x = ft.TextField(label="Eixo Cooktop (m da Esq.)", value="1.90", on_change=self._atualizar_calculos, width=120)

        # --- CONTAINER DO DESENHO ---
        self.canvas_container = ft.Container(
            content=ft.Text("Configure os dados para gerar a planta", color="grey700"),
            height=400, bgcolor="#F8F9FA", border_radius=10, border=ft.border.all(1, "grey300"), alignment=ft.alignment.center
        )

        # --- RESUMO FINANCEIRO ---
        self.txt_res_area = ft.Text("0.00 m²", weight="bold")
        self.txt_res_total = ft.Text("R$ 0.00", size=28, weight="bold", color=COLOR_PRIMARY)

        return ft.Container(
            padding=15, bgcolor=COLOR_WHITE,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Projeto Executivo da Peça", size=22, weight="bold"),
                    self.txt_ambiente,
                    self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof]),
                    self.input_ml_valor,
                    
                    ft.Divider(),
                    ft.Text("Lados com Saia (Azul no Desenho)", weight="bold", size=14),
                    ft.Row([self.check_saia_frente, self.check_saia_fundo, self.check_saia_esq, self.check_saia_dir], wrap=True),
                    
                    ft.Text("Lados com Rodobanca (Vermelho no Desenho)", weight="bold", size=14),
                    ft.Row([self.check_rodo_fundo, self.check_rodo_esq, self.check_rodo_dir], wrap=True),

                    ft.Divider(),
                    ft.Text("Posicionamento de Furos (Eixo)", weight="bold", size=14),
                    ft.Row([self.sw_bojo, self.in_bojo_x], alignment="spaceBetween"),
                    ft.Row([self.sw_cook, self.in_cook_x], alignment="spaceBetween"),

                    ft.Divider(),
                    self.canvas_container,
                    
                    ft.Container(
                        padding=20, bgcolor="#f1f3f4", border_radius=10,
                        content=ft.Column([
                            ft.Row([ft.Text("Área da Pedra:"), self.txt_res_area], alignment="spaceBetween"),
                            ft.Row([ft.Text("Total Estimado:"), self.txt_res_total], alignment="spaceBetween"),
                        ])
                    ),
                    
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=self.on_cancel),
                        ft.ElevatedButton("Salvar Peça no Orçamento", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar, expand=True, height=50)
                    ], spacing=20),
                    ft.Container(height=40)
                ]
            )
        )

    def _atualizar_calculos(self, e=None):
        try:
            if self.dd_pedra.value:
                self.pedra_selecionada = next((p for p in self.pedras if p["id"] == self.dd_pedra.value), None)

            larg = float(self.input_larg.value.replace(",", "."))
            prof = float(self.input_prof.value.replace(",", "."))
            v_ml = float(self.input_ml_valor.value.replace(",", "."))

            peca = BancadaPiece(
                nome=self.txt_ambiente.value, 
                largura=larg, 
                profundidade=prof,
                preco_m2=self.pedra_selecionada["preco_m2"] if self.pedra_selecionada else 0,
                valor_ml=v_ml
            )
            
            # Mapeamento de Lados Saia
            lados_s = []
            if self.check_saia_frente.value: lados_s.append("frente")
            if self.check_saia_fundo.value: lados_s.append("fundo")
            if self.check_saia_esq.value: lados_s.append("esquerda")
            if self.check_saia_dir.value: lados_s.append("direita")
            peca.saia = Acabamento(0.04, lados_s)

            # Mapeamento de Lados Rodo
            lados_r = []
            if self.check_rodo_fundo.value: lados_r.append("fundo")
            if self.check_rodo_esq.value: lados_r.append("esquerda")
            if self.check_rodo_dir.value: lados_r.append("direita")
            peca.rodobanca = Acabamento(0.10, lados_r)

            # Aberturas com Eixo Real
            if self.sw_bojo.value:
                dist_x = float(self.in_bojo_x.value.replace(",", "."))
                peca.aberturas.append(Abertura("bojo", 0.60, 0.40, dist_x, prof/2))
            
            if self.sw_cook.value:
                dist_x = float(self.in_cook_x.value.replace(",", "."))
                peca.aberturas.append(Abertura("cooktop", 0.55, 0.45, dist_x, prof/2))

            self.composition.pecas = [peca]
            
            # Renderiza o desenho técnico (Pillow)
            self.canvas_container.content = BudgetCanvas(self.composition)
            
            # Cálculo de Valor
            area = peca.area_m2()
            total = (area * peca.preco_m2) + (peca.calcular_perimetro_acabamento() * v_ml)
            
            self.txt_res_area.value = f"{area:.2f} m²"
            self.txt_res_total.value = f"R$ {total:,.2f}"
            self.update()
        except Exception as err:
            print(f"Erro Cálculo: {err}")

    def _salvar(self, e):
        if not self.pedra_selecionada:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecione o material!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        peca = self.composition.pecas[0]
        # Limpa string de preço para salvar como float puro
        preco_puro = float(self.txt_res_total.value.replace("R$ ", "").replace(".", "").replace(",", "."))
        
        item_final = {
            "ambiente": self.txt_ambiente.value,
            "material": self.pedra_selecionada["nome"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "area": peca.area_m2(),
            "preco_total": preco_puro,
            # Novos campos técnicos para o PDF ler
            "has_saia": len(peca.saia.lados) > 0 if peca.saia else False,
            "has_rodo": len(peca.rodobanca.lados) > 0 if peca.rodobanca else False
        }
        
        if self.on_save_item:
            self.on_save_item(item_final)