# src/views/components/budget_calculator.py

import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND
from src.services import firebase_service

class BudgetCalculator(ft.UserControl):
    def __init__(self, page, on_save_item, on_cancel, item=None):
        super().__init__()
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        self.item_para_editar = item 
        self.mapa_precos = {}
        
        # Estados para Bancada em U (Até 3 peças)
        self.tem_p2 = False
        self.tem_p3 = False

    def build(self):
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = [ft.dropdown.Option(key=c['id'], text=f"{c.get('nome')} - R$ {float(c.get('preco_m2',0)):.2f}/m²") for c in chapas]
        for c in chapas: self.mapa_precos[c['id']] = {'nome': c.get('nome'), 'preco': float(c.get('preco_m2',0))}

        def on_num_change(e):
            if e.control.value: e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # --- INPUTS BASE ---
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", height=45)
        self.dd_pedra = ft.Dropdown(label="Material", options=opcoes_pedras, height=45, on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", on_change=on_num_change)

        # --- PEÇAS P1, P2 (L), P3 (U) ---
        def criar_inputs_peca(nome, visivel=True):
            return {
                "l": ft.TextField(label=f"Comp. {nome} (m)", value="1.00", expand=True, on_change=on_num_change, visible=visivel),
                "p": ft.TextField(label=f"Prof. {nome} (m)", value="0.60", expand=True, on_change=on_num_change, visible=visivel),
                "lado": ft.Dropdown(label=f"Colar {nome} na...", value="direita", visible=visivel, options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")], on_change=self.calcular)
            }

        self.p1 = criar_inputs_peca("P1")
        self.p2 = criar_inputs_peca("P2 (L)", False)
        self.p3 = criar_inputs_peca("P3 (U)", False)

        # --- ACABAMENTOS (4 LADOS POR PEÇA) ---
        def seletor_lados(titulo):
            return {l: ft.Checkbox(label=l.capitalize()[:3], on_change=self.calcular) for l in ["fundo", "frente", "esquerda", "direita"]}

        # P1
        self.p1_rodo = seletor_lados("Rodo P1"); self.p1_rodo["fundo"].value = True
        self.p1_saia = seletor_lados("Saia P1"); self.p1_saia["frente"].value = True
        # P2
        self.p2_rodo = seletor_lados("Rodo P2")
        self.p2_saia = seletor_lados("Saia P2")
        # P3
        self.p3_rodo = seletor_lados("Rodo P3")
        self.p3_saia = seletor_lados("Saia P3")

        # --- FUROS ---
        def ctrl_furo(label):
            return {
                "sw": ft.Switch(label=label, on_change=self.calcular),
                "peca": ft.Dropdown(value="P1", options=[ft.dropdown.Option("P1"), ft.dropdown.Option("P2"), ft.dropdown.Option("P3")], width=70, on_change=self.calcular),
                "w": ft.TextField(label="Larg", value="0.50", width=65, on_change=on_num_change),
                "h": ft.TextField(label="Prof", value="0.40", width=65, on_change=on_num_change),
                "x": ft.TextField(label="Eixo", value="0.50", width=65, on_change=on_num_change)
            }
        self.f_bojo = ctrl_furo("Bojo")
        self.f_cook = ctrl_furo("Cooktop")

        self.canvas = cv.Canvas(width=350, height=350, shapes=[])
        self.lbl_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        # --- LÓGICA DE BOTÕES L/U ---
        def add_p2(e):
            self.tem_p2 = not self.tem_p2
            self.p2["l"].visible = self.p2["p"].visible = self.p2["lado"].visible = self.tem_p2
            btn_p2.text = "- Remover P2" if self.tem_p2 else "+ Peça Lateral (L)"
            self.calcular()

        def add_p3(e):
            self.tem_p3 = not self.tem_p3
            self.p3["l"].visible = self.p3["p"].visible = self.p3["lado"].visible = self.tem_p3
            btn_p3.text = "- Remover P3" if self.tem_p3 else "+ Peça Lateral (U)"
            self.calcular()

        btn_p2 = ft.ElevatedButton("+ Peça Lateral (L)", on_click=add_p2)
        btn_p3 = ft.ElevatedButton("+ Peça Lateral (U)", on_click=add_p3)

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([
                self.txt_ambiente, self.dd_pedra, ft.Row([self.p1["l"], self.p1["p"]]),
                ft.Divider(), btn_p2, ft.Row([self.p2["l"], self.p2["p"]]), self.p2["lado"],
                ft.Divider(), btn_p3, ft.Row([self.p3["l"], self.p3["p"]]), self.p3["lado"],
                self.txt_acab
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Text("PEÇA 1 (Principal)", weight="bold", size=12),
                ft.Row([ft.Text("Rodo:"), *self.p1_rodo.values()], wrap=True),
                ft.Row([ft.Text("Saia:"), *self.p1_saia.values()], wrap=True),
                ft.Divider(),
                ft.Text("PEÇA 2 (Lateral L)", weight="bold", size=12),
                ft.Row([ft.Text("Rodo:"), *self.p2_rodo.values()], wrap=True),
                ft.Row([ft.Text("Saia:"), *self.p2_saia.values()], wrap=True),
                ft.Divider(),
                ft.Text("PEÇA 3 (Lateral U)", weight="bold", size=12),
                ft.Row([ft.Text("Rodo:"), *self.p3_rodo.values()], wrap=True),
                ft.Row([ft.Text("Saia:"), *self.p3_saia.values()], wrap=True),
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.f_bojo["sw"], self.f_bojo["peca"]]),
                ft.Row([self.f_bojo["w"], self.f_bojo["h"], self.f_bojo["x"]], spacing=5),
                ft.Divider(),
                ft.Row([self.f_cook["sw"], self.f_cook["peca"]]),
                ft.Row([self.f_cook["w"], self.f_cook["h"], self.f_cook["x"]], spacing=5),
            ]))
        ], height=350)

        return ft.Container(padding=10, content=ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()), ft.Text("Projeto U", weight="bold")]),
            ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
            ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), height=350, alignment=ft.alignment.center),
            ft.Container(padding=15, bgcolor=COLOR_WHITE, border_radius=10, content=ft.Row([self.lbl_total, ft.ElevatedButton("Salvar", on_click=self.salvar)], alignment="spaceBetween"))
        ], scroll=ft.ScrollMode.ALWAYS))

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            p_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            v_ml = float(self.txt_acab.value or 0)
            
            total = 0; ml = 0
            
            def calc_peca(txt_l, txt_p, rodo, saia):
                l = float(txt_l.value or 0); p = float(txt_p.value or 0)
                area = l * p
                p_rodo = sum(l if k in ["fundo", "frente"] else p for k, v in rodo.items() if v.value)
                p_saia = sum(l if k in ["fundo", "frente"] else p for k, v in saia.items() if v.value)
                return (area * p_m2), (p_rodo + p_saia)

            # P1
            v_pedra, v_ml_peca = calc_peca(self.p1["l"], self.p1["p"], self.p1_rodo, self.p1_saia)
            total += v_pedra; ml += v_ml_peca
            
            # P2
            if self.tem_p2:
                v_pedra, v_ml_peca = calc_peca(self.p2["l"], self.p2["p"], self.p2_rodo, self.p2_saia)
                total += v_pedra; ml += v_ml_peca
            
            # P3
            if self.tem_p3:
                v_pedra, v_ml_peca = calc_peca(self.p3["l"], self.p3["p"], self.p3_rodo, self.p3_saia)
                total += v_pedra; ml += v_ml_peca

            final = total + (ml * v_ml)
            if self.f_bojo["sw"].value: final += 150
            if self.f_cook["sw"].value: final += 100
            
            self.lbl_total.value = f"R$ {final:,.2f}"
            self.desenhar()
            self.update()
        except: pass

    def desenhar(self):
        self.canvas.shapes.clear()
        
        def to_f(v): return float(str(v).replace(",",".")) if v else 0.0
        
        w1, h1 = to_f(self.p1["l"].value), to_f(self.p1["p"].value)
        w2, h2 = (to_f(self.p2["l"].value), to_f(self.p2["p"].value)) if self.tem_p2 else (0,0)
        w3, h3 = (to_f(self.p3["l"].value), to_f(self.p3["p"].value)) if self.tem_p3 else (0,0)

        scale = min(300/(w1+w2+w3+0.5), 200/(max(h1,h2,h3)+0.5)) * 0.6
        sx, sy = 175, 175 # Centro inicial
        
        # --- DESENHO PEÇA 1 ---
        w1p, h1p = w1*scale, h1*scale
        self.canvas.shapes.append(cv.Rect(sx-w1p/2, sy-h1p/2, w1p, h1p, paint=ft.Paint(style="fill", color="#F5F5F5")))
        self.canvas.shapes.append(cv.Rect(sx-w1p/2, sy-h1p/2, w1p, h1p, paint=ft.Paint(style="stroke", color="black")))
        self.canvas.shapes.append(cv.Text(sx-10, sy-h1p/2-25, f"{w1}m", style=ft.TextStyle(size=10, weight="bold")))

        # --- DESENHO P2 (LATERAL L) ---
        if self.tem_p2:
            w2p, h2p = w2*scale, h2*scale
            ex = sx + w1p/2 if self.p2["lado"].value == "direita" else sx - w1p/2 - w2p
            self.canvas.shapes.append(cv.Rect(ex, sy-h1p/2, w2p, h2p, paint=ft.Paint(style="fill", color="#E0E0E0")))
            self.canvas.shapes.append(cv.Rect(ex, sy-h1p/2, w2p, h2p, paint=ft.Paint(style="stroke", color="black")))
            self.canvas.shapes.append(cv.Text(ex+w2p/2-10, sy-h1p/2-25, f"{w2}m", style=ft.TextStyle(size=10)))

        # --- DESENHO P3 (LATERAL U) ---
        if self.tem_p3:
            w3p, h3p = w3*scale, h3*scale
            # Se P2 foi pra direita, P3 vai pra esquerda por padrão no U
            ux = sx - w1p/2 - w3p if self.p3["lado"].value == "esquerda" else sx + w1p/2
            self.canvas.shapes.append(cv.Rect(ux, sy-h1p/2, w3p, h3p, paint=ft.Paint(style="fill", color="#E0E0E0")))
            self.canvas.shapes.append(cv.Rect(ux, sy-h1p/2, w3p, h3p, paint=ft.Paint(style="stroke", color="black")))

        # --- DESENHO FUROS (COOKTOP E BOJO) ---
        for f in [self.f_bojo, self.f_cook]:
            if f["sw"].value:
                # Localiza a peça alvo
                alvo_x = sx - w1p/2
                if f["peca"].value == "P2" and self.tem_p2: alvo_x = sx + w1p/2 if self.p2["lado"].value == "direita" else sx - w1p/2 - (w2*scale)
                if f["peca"].value == "P3" and self.tem_p3: alvo_x = sx - w1p/2 - (w3*scale) if self.p3["lado"].value == "esquerda" else sx + w1p/2
                
                px = alvo_x + (to_f(f["x"].value) * scale)
                fw, fh = (to_f(f["w"].value) * scale), (to_f(f["h"].value) * scale)
                self.canvas.shapes.append(cv.Rect(px-fw/2, sy-h1p/2 + 10, fw, fh, border_radius=2, paint=ft.Paint(style="stroke", color="blue")))
                self.canvas.shapes.append(cv.Text(px-12, sy-h1p/2 + fh/2 + 5, "EIXO", style=ft.TextStyle(size=7, color="blue")))

        self.canvas.update()

    def salvar(self, e):
        total_puro = float(self.lbl_total.value.replace("R$ ","").replace(".","").replace(",","."))
        self.on_save_item({
            "ambiente": self.txt_ambiente.value, "material": self.mapa_precos[self.dd_pedra.value]['nome'],
            "largura": self.p1["l"].value, "profundidade": self.p1["p"].value, "preco_total": total_puro
        })