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
        # --- INPUTS BÁSICOS ---
        self.dd_pedra = ft.Dropdown(
            label="Material do Estoque",
            options=[ft.dropdown.Option(key=p["id"], text=p["nome"]) for p in self.pedras],
            on_change=self._atualizar_calculos
        )
        self.input_larg = ft.TextField(label="Comprimento (m)", value="1.00", on_change=self._atualizar_calculos, expand=True)
        self.input_prof = ft.TextField(label="Profundidade (m)", value="0.60", on_change=self._atualizar_calculos, expand=True)
        self.input_ml_valor = ft.TextField(label="Valor ML Mão de Obra", value="130", on_change=self._atualizar_calculos, width=150)

        # --- SELEÇÃO DE LADOS (SAIA E RODO) ---
        self.lados_saia = {
            "frente": ft.Checkbox(label="Frente", value=True, on_change=self._atualizar_calculos),
            "fundo": ft.Checkbox(label="Fundo", on_change=self._atualizar_calculos),
            "esquerda": ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos),
            "direita": ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos),
        }
        self.lados_rodo = {
            "fundo": ft.Checkbox(label="Fundo", value=True, on_change=self._atualizar_calculos),
            "frente": ft.Checkbox(label="Frente", on_change=self._atualizar_calculos),
            "esquerda": ft.Checkbox(label="Esq.", on_change=self._atualizar_calculos),
            "direita": ft.Checkbox(label="Dir.", on_change=self._atualizar_calculos),
        }

        # --- FUROS (BOJO / COOKTOP) ---
        self.check_bojo = ft.Checkbox(label="Incluir Bojo", on_change=self._atualizar_calculos)
        self.bojo_w = ft.TextField(label="Larg. Bojo", value="0.50", visible=False, width=100, on_change=self._atualizar_calculos)
        self.bojo_h = ft.TextField(label="Prof. Bojo", value="0.40", visible=False, width=100, on_change=self._atualizar_calculos)

        self.check_cook = ft.Checkbox(label="Incluir Cooktop", on_change=self._atualizar_calculos)
        self.cook_w = ft.TextField(label="Larg. Cook", value="0.55", visible=False, width=100, on_change=self._atualizar_calculos)

        # --- ÁREA VISUAL ---
        self.canvas_container = ft.Container(
            content=ft.Text("Carregando projeto..."),
            height=300, bgcolor="#f8f9fa", border_radius=10, border=ft.border.all(1, "grey300")
        )

        self.txt_res_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        return ft.Container(
            padding=15,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Configuração Técnica da Peça", size=20, weight="bold"),
                    self.dd_pedra,
                    ft.Row([self.input_larg, self.input_prof, self.input_ml_valor]),
                    
                    ft.Divider(),
                    ft.Text("Lados com Saia (Acabamento)", weight="bold"),
                    ft.Row(list(self.lados_saia.values()), wrap=True),
                    
                    ft.Text("Lados com Rodobanca (Parede)", weight="bold"),
                    ft.Row(list(self.lados_rodo.values()), wrap=True),

                    ft.Divider(),
                    ft.Text("Aberturas e Furos", weight="bold"),
                    ft.Row([self.check_bojo, self.bojo_w, self.bojo_h]),
                    ft.Row([self.check_cook, self.cook_w]),

                    ft.Divider(),
                    self.canvas_container,
                    
                    ft.Row([ft.Text("Investimento:"), self.txt_res_total], alignment="spaceBetween"),
                    ft.ElevatedButton("Finalizar e Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self._salvar, height=50)
                ]
            )
        )

    def _atualizar_calculos(self, e=None):
        try:
            # Visibilidade dos campos de furos
            self.bojo_w.visible = self.bojo_h.visible = self.check_bojo.value
            self.cook_w.visible = self.check_cook.value
            
            larg = float(self.input_larg.value or 0)
            prof = float(self.input_prof.value or 0)
            v_ml = float(self.input_ml_valor.value or 0)

            # Criar Peça Técnica
            peca = BancadaPiece(nome="Peça", largura=larg, profundidade=prof)
            
            # Definir Lados
            lados_s = [k for k, v in self.lados_saia.items() if v.value]
            peca.saia = Saia(altura=0.04, lados=lados_s)
            
            lados_r = [k for k, v in self.lados_rodo.items() if v.value]
            peca.rodobanca = RodoBanca(altura=0.10, lados=lados_r)

            # Adicionar Aberturas
            if self.check_bojo.value:
                peca.aberturas.append(Abertura(tipo="bojo", largura=float(self.bojo_w.value), profundidade=float(self.bojo_h.value), offset_x=0.2, offset_y=0.1))

            self.composition.pecas = [peca]
            self.canvas_container.content = BudgetCanvas(self.composition)

            # Lógica Financeira Real
            preco_m2 = next((p["preco_m2"] for p in self.pedras if p["id"] == self.dd_pedra.value), 0)
            
            custo_pedra = peca.area_m2() * preco_m2
            custo_mao_obra = peca.metro_linear_saia() * v_ml
            # Adicional por furo (ex: R$ 50 por furo)
            custo_furos = len(peca.aberturas) * 50 

            total = custo_pedra + custo_mao_obra + custo_furos
            self.txt_res_total.value = f"R$ {total:,.2f}"
            self.update()
        except Exception as err:
            print(f"Erro: {err}")

        async def _preencher_edicao_atrasado(self):
            it = self.item_para_editar
            if not it: return
            
            # Medidas Básicas
            self.txt_ambiente.value = it.get("ambiente", "Geral")
            self.input_larg.value = str(it.get("largura", 1.0))
            self.input_prof.value = str(it.get("profundidade", 0.6))
            
            # Material
            for p in self.pedras:
                if p["nome"] == it.get("material"):
                    self.dd_pedra.value = p["id"]
                    self.pedra_selecionada = p

            # Acabamentos (Lados da Saia)
            saia_data = it.get("saia", {})
            lados_s = saia_data.get("lados", [])
            for lado, cb in self.lados_saia.items():
                cb.value = lado in lados_s
                
            # Acabamentos (Lados da Rodobanca)
            rodo_data = it.get("rodobanca", {})
            lados_r = rodo_data.get("lados", [])
            for lado, cb in self.lados_rodo.items():
                cb.value = lado in lados_r

            # Aberturas (Furos)
            abs_list = it.get("aberturas", [])
            self.check_bojo.value = any(a["tipo"] == "bojo" for a in abs_list)
            self.check_cook.value = any(a["tipo"] == "cooktop" for a in abs_list)

            self._atualizar_calculos()

    def _salvar(self, e):
        if not self.dd_pedra.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecione o material!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Busca os dados da pedra selecionada
        self.pedra_selecionada = next(p for p in self.pedras if p["id"] == self.dd_pedra.value)
        
        # A peça técnica atualizada pela função _atualizar_calculos
        peca = self.composition.pecas[0]
        
        # Montagem do objeto final para o Firebase
        item_final = {
            "ambiente": self.txt_ambiente.value,
            "material": self.pedra_selecionada["nome"],
            "material_id": self.pedra_selecionada["id"],
            "largura": peca.largura,
            "profundidade": peca.profundidade,
            "area": peca.area_m2(),
            # Limpeza do preço para garantir que seja um número puro
            "preco_total": float(self.txt_res_total.value.replace("R$ ", "").replace(".", "").replace(",", ".")),
            
            # Dados detalhados de acabamento para o PDF e manutenção
            "saia": {
                "altura": float(self.alt_saia.value),
                "lados": peca.saia.lados if peca.saia else []
            },
            "rodobanca": {
                "altura": float(self.alt_rodo.value),
                "lados": peca.rodobanca.lados if peca.rodobanca else []
            },
            
            # Flags simplificadas para o PDF service antigo se necessário
            "has_saia": peca.saia is not None and len(peca.saia.lados) > 0,
            "has_rodo": peca.rodobanca is not None and len(peca.rodobanca.lados) > 0,

            # Lista de aberturas (Bojo/Cooktop)
            "aberturas": [
                {
                    "tipo": ab.tipo,
                    "largura": ab.largura,
                    "profundidade": ab.profundidade,
                    "offset_x": ab.offset_x,
                    "offset_y": ab.offset_y
                } for ab in peca.aberturas
            ]
        }
        
        if self.on_save_item:
            self.on_save_item(item_final)