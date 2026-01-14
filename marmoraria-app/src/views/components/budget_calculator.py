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

    def to_f(self, v):
        try:
            val = str(v).strip().replace(",", ".")
            return float(val) if val else 0.0
        except:
            return 0.0

    def build(self):
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = [ft.dropdown.Option(key=c['id'], text=f"{c.get('nome')} - R$ {float(c.get('preco_m2',0)):.2f}/m²") for c in chapas]
        for c in chapas: 
            self.mapa_precos[c['id']] = {'nome': c.get('nome'), 'preco': float(c.get('preco_m2',0))}

        def on_num_change(e):
            if e.control.value and "," in e.control.value:
                e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # --- CAMPOS DE ENTRADA ---
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", height=45)
        self.dd_pedra = ft.Dropdown(label="Material", options=opcoes_pedras, height=45, on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", on_change=on_num_change)

        def criar_inputs_peca(nome, visivel=True):
            return {
                "l": ft.TextField(label=f"Comp. {nome} (m)", value="1.00", expand=True, on_change=on_num_change, visible=visivel),
                "p": ft.TextField(label=f"Prof. {nome} (m)", value="0.60", expand=True, on_change=on_num_change, visible=visivel),
                "lado": ft.Dropdown(label="Posição", value="direita" if nome != "P1" else None, visible=visivel, 
                                   options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")], on_change=self.calcular)
            }

        self.p1 = criar_inputs_peca("P1")
        self.p2 = criar_inputs_peca("P2 (L)", False)
        self.p3 = criar_inputs_peca("P3 (U)", False)

        def seletor_lados():
            return {l: ft.Checkbox(label=l.capitalize()[:3], on_change=self.calcular) for l in ["fundo", "frente", "esquerda", "direita"]}

        self.p1_rodo = seletor_lados(); self.p1_rodo["fundo"].value = True
        self.p1_saia = seletor_lados(); self.p1_saia["frente"].value = True
        self.p2_rodo = seletor_lados(); self.p2_saia = seletor_lados()
        self.p3_rodo = seletor_lados(); self.p3_saia = seletor_lados()

        def ctrl_furo(label):
            return {
                "sw": ft.Switch(label=label, on_change=self.calcular),
                "peca": ft.Dropdown(value="P1", options=[ft.dropdown.Option("P1"), ft.dropdown.Option("P2"), ft.dropdown.Option("P3")], width=75, on_change=self.calcular),
                "w": ft.TextField(label="L", value="0.50", width=65, on_change=on_num_change),
                "h": ft.TextField(label="P", value="0.40", width=65, on_change=on_num_change),
                "x": ft.TextField(label="X", value="0.50", width=65, on_change=on_num_change)
            }
        self.f_bojo = ctrl_furo("Bojo")
        self.f_cook = ctrl_furo("Cook")

        # Canvas com tamanho fixo para não dar erro de posicionamento
        self.canvas = cv.Canvas(width=350, height=350, shapes=[])
        self.lbl_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        def toggle_p(e, n):
            if n == 2: self.tem_p2 = not self.tem_p2; p, v = self.p2, self.tem_p2
            else: self.tem_p3 = not self.tem_p3; p, v = self.p3, self.tem_p3
            p["l"].visible = p["p"].visible = p["lado"].visible = v
            self.calcular()

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([
                self.txt_ambiente, self.dd_pedra, 
                ft.Row([self.p1["l"], self.p1["p"]]),
                ft.Row([ft.ElevatedButton("+ P2", on_click=lambda e: toggle_p(e, 2)), ft.ElevatedButton("+ P3", on_click=lambda e: toggle_p(e, 3))]),
                ft.Column([ft.Row([self.p2["l"], self.p2["p"]]), self.p2["lado"]]),
                ft.Column([ft.Row([self.p3["l"], self.p3["p"]]), self.p3["lado"]]),
                self.txt_acab
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Text("P1", weight="bold"), ft.Row([*self.p1_rodo.values()], wrap=True), ft.Row([*self.p1_saia.values()], wrap=True),
                ft.Divider(), ft.Text("P2", weight="bold"), ft.Row([*self.p2_rodo.values()], wrap=True), ft.Row([*self.p2_saia.values()], wrap=True),
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.f_bojo["sw"], self.f_bojo["peca"]]),
                ft.Row([self.f_bojo["w"], self.f_bojo["h"], self.f_bojo["x"]], spacing=5),
            ]))
        ], height=280)

        return ft.Container(padding=10, content=ft.Column([
            ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
            ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), height=350, alignment=ft.alignment.center),
            ft.Container(padding=15, bgcolor=COLOR_WHITE, border_radius=10, content=ft.Row([self.lbl_total, ft.ElevatedButton("Salvar", on_click=self.salvar)], alignment="spaceBetween"))
        ], scroll=ft.ScrollMode.ALWAYS))

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            p_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            v_ml = self.to_f(self.txt_acab.value)
            total_m2 = 0; total_ml = 0
            def calc_peca(l_ctrl, p_ctrl, rodo, saia):
                l, p = self.to_f(l_ctrl.value), self.to_f(p_ctrl.value)
                ml = 0
                for k, v in rodo.items():
                    if v.value: ml += (l if k in ["fundo", "frente"] else p)
                for k, v in saia.items():
                    if v.value: ml += (l if k in ["fundo", "frente"] else p)
                return (l * p * p_m2), ml
            v1, m1 = calc_peca(self.p1["l"], self.p1["p"], self.p1_rodo, self.p1_saia)
            total_m2 += v1; total_ml += m1
            if self.tem_p2:
                v2, m2 = calc_peca(self.p2["l"], self.p2["p"], self.p2_rodo, self.p2_saia)
                total_m2 += v2; total_ml += m2
            if self.tem_p3:
                v3, m3 = calc_peca(self.p3["l"], self.p3["p"], self.p3_rodo, self.p3_saia)
                total_m2 += v3; total_ml += m3
            total_final = total_m2 + (total_ml * v_ml)
            if self.f_bojo["sw"].value: total_final += 150
            if self.f_cook["sw"].value: total_final += 100
            self.lbl_total.value = f"R$ {total_final:,.2f}"
            self.desenhar()
            self.update()
        except: pass

    def desenhar(self):
        self.canvas.shapes.clear()
        w1, h1 = max(0.01, self.to_f(self.p1["l"].value)), max(0.01, self.to_f(self.p1["p"].value))
        w2, h2 = (self.to_f(self.p2["l"].value), self.to_f(self.p2["p"].value)) if self.tem_p2 else (0,0)
        w3, h3 = (self.to_f(self.p3["l"].value), self.to_f(self.p3["p"].value)) if self.tem_p3 else (0,0)

        # Escala rigorosa
        total_w = w1 + (w2 if self.tem_p2 else 0) + (w3 if self.tem_p3 else 0)
        max_h = max(h1, h2, h3)
        scale = min(280 / max(0.1, total_w), 280 / max(0.1, max_h))

        # Posicionamento Central Fixo no Canvas 350x350
        offset_x = 175 - (total_w * scale) / 2
        p1_x = offset_x + (w2 * scale if (self.tem_p2 and self.p2["lado"].value == "esquerda") else 0)
        if self.tem_p3 and self.p3["lado"].value == "esquerda": p1_x += (w3 * scale)
        p1_y = 175 - (max_h * scale) / 2

        def draw_peca(w, h, x, y, rodo, saia, j_esq, j_dir):
            wp, hp = w*scale, h*scale
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="fill", color="#F5F5F5")))
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="stroke", color="black", stroke_width=1)))
            
            # Medida da Peça
            self.canvas.shapes.append(cv.Text(x + wp/2 - 10, y + hp/2 - 5, f"{w}x{h}", style=ft.TextStyle(size=10, weight="bold")))

            lados = {"fundo": (x,y,x+wp,y, "f"), "frente": (x,y+hp,x+wp,y+hp, "fr"), "esquerda": (x,y,x,y+hp, "e"), "direita": (x+wp,y,x+wp,y+hp, "d")}
            for lado, (x1, y1, x2, y2, tag) in lados.items():
                if (lado == "esquerda" and j_esq) or (lado == "direita" and j_dir): continue
                # Desenha Rodobanca (Vermelho)
                if rodo[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="red", stroke_width=3)))
                    # Texto da medida do rodobanca
                    tx, ty = (x1+x2)/2, (y1+y2)/2
                    self.canvas.shapes.append(cv.Text(tx-5, ty-15 if lado=="fundo" else ty+5, f"R:{w if lado in ['fundo','frente'] else h}m", style=ft.TextStyle(size=8, color="red")))
                # Desenha Saia (Azul)
                if saia[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="blue", stroke_width=4)))
                    tx, ty = (x1+x2)/2, (y1+y2)/2
                    self.canvas.shapes.append(cv.Text(tx-5, ty+5 if lado=="fundo" else ty-15, f"S:{w if lado in ['fundo','frente'] else h}m", style=ft.TextStyle(size=8, color="blue")))

        # P1 e laterais
        j1_e = (self.tem_p2 and self.p2["lado"].value == "esquerda") or (self.tem_p3 and self.p3["lado"].value == "esquerda")
        j1_d = (self.tem_p2 and self.p2["lado"].value == "direita") or (self.tem_p3 and self.p3["lado"].value == "direita")
        draw_peca(w1, h1, p1_x, p1_y, self.p1_rodo, self.p1_saia, j1_e, j1_d)

        for p_idx, tem, dados, rodo, saia in [("P2", self.tem_p2, self.p2, self.p2_rodo, self.p2_saia), ("P3", self.tem_p3, self.p3, self.p3_rodo, self.p3_saia)]:
            if tem:
                lx, px = self.to_f(dados["l"].value), self.to_f(dados["p"].value)
                pos_x = (p1_x + w1*scale) if dados["lado"].value == "direita" else (p1_x - lx*scale)
                draw_peca(lx, px, pos_x, p1_y, rodo, saia, j_esq=(dados["lado"].value=="direita"), j_dir=(dados["lado"].value=="esquerda"))

        # Furos (Simples)
        for f in [self.f_bojo, self.f_cook]:
            if f["sw"].value:
                self.canvas.shapes.append(cv.Rect(p1_x + (w1*scale)/2 - 20, p1_y + 10, 40, 30, paint=ft.Paint(style="stroke", color="orange")))

        self.canvas.update()

    def salvar(self, e):
        # ... (mesma lógica de salvar anterior)
        pass