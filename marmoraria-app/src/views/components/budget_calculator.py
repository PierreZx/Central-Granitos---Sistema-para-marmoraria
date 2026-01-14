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
        self.tem_p2 = False
        self.tem_p3 = False

    def build(self):
        # --- CARREGAR DADOS DO ESTOQUE ---
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = []
        for chapa in chapas:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('preco_m2', 0) or 0)
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=f"{nome} - R$ {preco:.2f}/m²"))
            self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- FUNÇÃO PARA TRATAR VÍRGULA E PONTO ---
        def on_num_change(e):
            if e.control.value and "," in e.control.value:
                e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # --- INPUTS BASE ---
        self.txt_ambiente = ft.TextField(label="Ambiente", border_radius=8, height=45, value="Cozinha")
        self.dd_pedra = ft.Dropdown(label="Material", options=opcoes_pedras, border_radius=8, height=45, on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", expand=True, keyboard_type=ft.KeyboardType.NUMBER, on_change=on_num_change)

        # Configuração de Peças (P1, P2 e P3 para formato U)
        def criar_inputs_peca(nome, visivel=True):
            return {
                "l": ft.TextField(label=f"Comp. {nome} (m)", value="1.00", expand=True, on_change=on_num_change, visible=visivel),
                "p": ft.TextField(label=f"Prof. {nome} (m)", value="0.60", expand=True, on_change=on_num_change, visible=visivel),
                "lado": ft.Dropdown(label="Colar na...", value="direita", visible=visivel, options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")], on_change=self.calcular)
            }

        self.p1 = criar_inputs_peca("P1")
        self.p2 = criar_inputs_peca("P2 (L)", False)
        self.p3 = criar_inputs_peca("P3 (U)", False)

        # --- SELETORES DE LADOS (RODO E SAIA) ---
        def seletor_lados():
            return {l: ft.Checkbox(label=l.capitalize()[:3], on_change=self.calcular) for l in ["fundo", "frente", "esquerda", "direita"]}

        self.p1_rodo = seletor_lados(); self.p1_rodo["fundo"].value = True
        self.p1_saia = seletor_lados(); self.p1_saia["frente"].value = True
        self.p2_rodo = seletor_lados(); self.p2_saia = seletor_lados()
        self.p3_rodo = seletor_lados(); self.p3_saia = seletor_lados()

        # --- FUROS ---
        def ctrl_furo(label):
            return {
                "sw": ft.Switch(label=label, on_change=self.calcular),
                "peca": ft.Dropdown(value="P1", options=[ft.dropdown.Option("P1"), ft.dropdown.Option("P2"), ft.dropdown.Option("P3")], width=70, on_change=self.calcular),
                "w": ft.TextField(label="L", value="0.50", width=65, on_change=on_num_change),
                "h": ft.TextField(label="P", value="0.40", width=65, on_change=on_num_change),
                "x": ft.TextField(label="Eixo", value="0.50", width=65, on_change=on_num_change)
            }
        self.f_bojo = ctrl_furo("Bojo")
        self.f_cook = ctrl_furo("Cook")

        self.canvas = cv.Canvas(width=350, height=350, shapes=[])
        self.lbl_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        # Lógica para alternar visibilidade das peças extras
        def toggle_p2(e):
            self.tem_p2 = not self.tem_p2
            self.p2["l"].visible = self.p2["p"].visible = self.p2["lado"].visible = self.tem_p2
            self.calcular()

        def toggle_p3(e):
            self.tem_p3 = not self.tem_p3
            self.p3["l"].visible = self.p3["p"].visible = self.p3["lado"].visible = self.tem_p3
            self.calcular()

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([
                self.txt_ambiente, self.dd_pedra, ft.Row([self.p1["l"], self.p1["p"]]),
                ft.ElevatedButton("+ Peça Lateral (L)", on_click=toggle_p2),
                ft.Row([self.p2["l"], self.p2["p"]]), self.p2["lado"],
                ft.ElevatedButton("+ Peça Lateral (U)", on_click=toggle_p3),
                ft.Row([self.p3["l"], self.p3["p"]]), self.p3["lado"],
                self.txt_acab
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Text("PEÇA 1 (P1)", weight="bold"),
                ft.Row([ft.Text("Rodo:"), *self.p1_rodo.values()], wrap=True),
                ft.Row([ft.Text("Saia:"), *self.p1_saia.values()], wrap=True),
                ft.Divider(),
                ft.Text("PEÇA 2 (P2)", weight="bold"),
                ft.Row([ft.Text("Rodo:"), *self.p2_rodo.values()], wrap=True),
                ft.Row([ft.Text("Saia:"), *self.p2_saia.values()], wrap=True),
                ft.Divider(),
                ft.Text("PEÇA 3 (P3)", weight="bold"),
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
        ], height=320)

        return ft.Container(padding=10, content=ft.Column([
            ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
            ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), height=350, alignment=ft.alignment.center),
            ft.Container(padding=15, bgcolor=COLOR_WHITE, border_radius=10, content=ft.Row([self.lbl_total, ft.ElevatedButton("Salvar", on_click=self.salvar)], alignment="spaceBetween"))
        ], scroll=ft.ScrollMode.ALWAYS))

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            p_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            v_ml = float(self.txt_acab.value or 0)
            
            # SOLUÇÃO DO ERRO: Função to_f definida localmente dentro do cálculo
            def to_f(v): return float(str(v).replace(",",".")) if v else 0.0

            total = 0; ml = 0
            
            def processar_peca(l_ctrl, p_ctrl, rodo, saia):
                l, p = to_f(l_ctrl.value), to_f(p_ctrl.value)
                m = sum(l if k in ["fundo", "frente"] else p for k, v in rodo.items() if v.value)
                m += sum(l if k in ["fundo", "frente"] else p for k, v in saia.items() if v.value)
                return (l * p * p_m2), m

            v1, m1 = processar_peca(self.p1["l"], self.p1["p"], self.p1_rodo, self.p1_saia)
            total += v1; ml += m1
            
            if self.tem_p2:
                v2, m2 = processar_peca(self.p2["l"], self.p2["p"], self.p2_rodo, self.p2_saia)
                total += v2; ml += m2
            
            if self.tem_p3:
                v3, m3 = processar_peca(self.p3["l"], self.p3["p"], self.p3_rodo, self.p3_saia)
                total += v3; ml += m3

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

        # Fator de escala inteligente para manter o desenho visível
        escala_w = 300 / (w1 + w2 + w3 + 0.5)
        escala_h = 220 / (max(h1, h2, h3) + 1.0)
        scale = min(escala_w, escala_h)
        
        # Ponto central da P1
        bx, by = 175 - (w1*scale)/2, 175 - (h1*scale)/2

        def draw_peca_final(w, h, x, y, rodo, saia, juncao=None):
            wp, hp = w*scale, h*scale
            # Pedra
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="fill", color="#F8F8F8")))
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="stroke", color="black", stroke_width=1.5)))
            # Cotas principais
            self.canvas.shapes.append(cv.Text(x+wp/2-10, y-25, f"{w}m", style=ft.TextStyle(size=10, weight="bold")))
            self.canvas.shapes.append(cv.Text(x-45, y+hp/2-5, f"{h}m", style=ft.TextStyle(size=10, weight="bold")))

            # Acabamentos sem bagunça na junção
            conf = {
                "fundo": (x, y, x+wp, y, -12, "red", "R:0.10"),
                "frente": (x, y+hp, x+wp, y+hp, 4, "blue", "S:0.04"),
                "esquerda": (x, y, x, y+hp, -30, "red", "R"),
                "direita": (x+wp, y, x+wp, y+hp, 5, "blue", "S")
            }
            for lado, x1, y1, x2, y2, off, cor, txt in conf.items():
                if lado == juncao: continue
                if rodo[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="red", stroke_width=3)))
                    if lado in ["fundo","frente"]: self.canvas.shapes.append(cv.Text(x+wp/2-15, y1+off, txt, style=ft.TextStyle(size=8, color="red")))
                if saia[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="blue", stroke_width=4)))
                    if lado in ["fundo","frente"]: self.canvas.shapes.append(cv.Text(x+wp/2-15, y1+off, txt, style=ft.TextStyle(size=8, color="blue")))

        # Desenha as 3 peças alinhadas
        draw_peca_final(w1, h1, bx, by, self.p1_rodo, self.p1_saia)
        
        if self.tem_p2:
            lado_p2 = self.p2["lado"].value
            x2 = bx + (w1*scale) if lado_p2 == "direita" else bx - (w2*scale)
            draw_peca_final(w2, h2, x2, by, self.p2_rodo, self.p2_saia, juncao=("esquerda" if lado_p2=="direita" else "direita"))

        if self.tem_p3:
            lado_p3 = self.p3["lado"].value
            x3 = bx + (w1*scale) if lado_p3 == "direita" else bx - (w3*scale)
            draw_peca_final(w3, h3, x3, by, self.p3_rodo, self.p3_saia, juncao=("esquerda" if lado_p3=="direita" else "direita"))

        # Furos (Bojo e Cooktop) 
        for f in [self.f_bojo, self.f_cook]:
            if f["sw"].value:
                alvo_x = bx
                if f["peca"].value == "P2" and self.tem_p2: alvo_x = bx + (w1*scale) if self.p2["lado"].value=="direita" else bx - (w2*scale)
                if f["peca"].value == "P3" and self.tem_p3: alvo_x = bx + (w1*scale) if self.p3["lado"].value=="direita" else bx - (w3*scale)
                
                fx, fw, fh = to_f(f["x"].value)*scale, to_f(f["w"].value)*scale, to_f(f["h"].value)*scale
                self.canvas.shapes.append(cv.Rect(alvo_x+fx-fw/2, by + 10, fw, fh, border_radius=2, paint=ft.Paint(style="stroke", color="blue", stroke_width=1)))
                self.canvas.shapes.append(cv.Text(alvo_x+fx-10, by + fh/2 + 5, "EIXO", style=ft.TextStyle(size=7, color="blue")))

        self.canvas.update()

    def salvar(self, e):
        t = float(self.lbl_total.value.replace("R$ ","").replace(".","").replace(",","."))
        self.on_save_item({"ambiente": self.txt_ambiente.value, "material": self.mapa_precos[self.dd_pedra.value]['nome'] if self.dd_pedra.value else "N/A", "largura": self.p1["l"].value, "profundidade": self.p1["p"].value, "preco_total": t})