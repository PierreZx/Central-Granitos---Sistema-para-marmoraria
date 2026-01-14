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
        """Converte string para float tratando ponto e vírgula com segurança."""
        try:
            return float(str(v).replace(",", ".")) if v else 0.0
        except:
            return 0.0

    def build(self):
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = [ft.dropdown.Option(key=c['id'], text=f"{c.get('nome')} - R$ {float(c.get('preco_m2',0)):.2f}/m²") for c in chapas]
        for c in chapas: self.mapa_precos[c['id']] = {'nome': c.get('nome'), 'preco': float(c.get('preco_m2',0))}

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
                "lado": ft.Dropdown(label="Posição", value="direita", visible=visivel, options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")], on_change=self.calcular)
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

        self.canvas = cv.Canvas(width=350, height=350, shapes=[])
        self.lbl_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        def toggle_p(e, n):
            if n == 2: self.tem_p2 = not self.tem_p2; p = self.p2
            else: self.tem_p3 = not self.tem_p3; p = self.p3
            p["l"].visible = p["p"].visible = p["lado"].visible = (self.tem_p2 if n==2 else self.tem_p3)
            self.calcular()

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([
                self.txt_ambiente, self.dd_pedra, ft.Row([self.p1["l"], self.p1["p"]]),
                ft.ElevatedButton("+ Peça Lateral (L)", on_click=lambda e: toggle_p(e, 2)),
                ft.Row([self.p2["l"], self.p2["p"]]), self.p2["lado"],
                ft.ElevatedButton("+ Peça Lateral (U)", on_click=lambda e: toggle_p(e, 3)),
                ft.Row([self.p3["l"], self.p3["p"]]), self.p3["lado"],
                self.txt_acab
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Text("P1", weight="bold"), ft.Row([*self.p1_rodo.values()], wrap=True), ft.Row([*self.p1_saia.values()], wrap=True),
                ft.Divider(), ft.Text("P2", weight="bold"), ft.Row([*self.p2_rodo.values()], wrap=True), ft.Row([*self.p2_saia.values()], wrap=True),
                ft.Divider(), ft.Text("P3", weight="bold"), ft.Row([*self.p3_rodo.values()], wrap=True), ft.Row([*self.p3_saia.values()], wrap=True),
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
            v_ml = self.to_f(self.txt_acab.value)
            
            total = 0; ml = 0
            def calc_u(l_ctrl, p_ctrl, rodo, saia):
                l, p = self.to_f(l_ctrl.value), self.to_f(p_ctrl.value)
                m = sum(l if k in ["fundo", "frente"] else p for k, v in rodo.items() if v.value)
                m += sum(l if k in ["fundo", "frente"] else p for k, v in saia.items() if v.value)
                return (l * p * p_m2), m

            v1, m1 = calc_u(self.p1["l"], self.p1["p"], self.p1_rodo, self.p1_saia)
            total += v1; ml += m1
            if self.tem_p2:
                v2, m2 = calc_u(self.p2["l"], self.p2["p"], self.p2_rodo, self.p2_saia)
                total += v2; ml += m2
            if self.tem_p3:
                v3, m3 = calc_u(self.p3["l"], self.p3["p"], self.p3_rodo, self.p3_saia)
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
        w1, h1 = self.to_f(self.p1["l"].value), self.to_f(self.p1["p"].value)
        w2, h2 = (self.to_f(self.p2["l"].value), self.to_f(self.p2["p"].value)) if self.tem_p2 else (0,0)
        w3, h3 = (self.to_f(self.p3["l"].value), self.to_f(self.p3["p"].value)) if self.tem_p3 else (0,0)

        # Fator de escala inteligente
        scale = min(320 / (w1 + w2 + w3 + 0.5), 250 / (max(h1, h2, h3, 0.1) + 1.0))
        base_x = 175 - (w1 * scale) / 2
        base_y = 175 - (h1 * scale) / 2

        def draw_tech_peca(w, h, x, y, rodo, saia, juncao=None):
            wp, hp = w*scale, h*scale
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="fill", color="#F8F8F8")))
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="stroke", color="black", stroke_width=1.5)))
            
            # Cotas de medida
            self.canvas.shapes.append(cv.Text(x + wp/2 - 10, y - 22, f"{w}m", style=ft.TextStyle(size=10, weight="bold")))
            self.canvas.shapes.append(cv.Text(x - 40, y + hp/2 - 5, f"{h}m", style=ft.TextStyle(size=10, weight="bold")))

            # Acabamentos sem bagunça
            lados = {
                "fundo": (x, y, x+wp, y, -12, "red", "R:0.10"),
                "frente": (x, y+hp, x+wp, y+hp, 4, "blue", "S:0.04"),
                "esquerda": (x, y, x, y+hp, -30, "red", "R"),
                "direita": (x+wp, y, x+wp, y+hp, 5, "blue", "S")
            }
            for lado, x1, y1, x2, y2, off, cor, txt in lados.items():
                if lado == juncao: continue 
                if rodo[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="red", stroke_width=4)))
                    if lado in ["fundo","frente"]: self.canvas.shapes.append(cv.Text(x+wp/2-15, y1+off, txt, style=ft.TextStyle(size=8, color="red")))
                if saia[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="blue", stroke_width=6)))
                    if lado in ["fundo","frente"]: self.canvas.shapes.append(cv.Text(x+wp/2-15, y1+off, txt, style=ft.TextStyle(size=8, color="blue")))

        # P1 centralizada
        draw_tech_peca(w1, h1, base_x, base_y, self.p1_rodo, self.p1_saia)
        
        # P2 Lateral
        if self.tem_p2:
            lado_p2 = self.p2["lado"].value
            x2 = base_x + (w1 * scale) if lado_p2 == "direita" else base_x - (w2 * scale)
            draw_tech_peca(w2, h2, x2, base_y, self.p2_rodo, self.p2_saia, juncao=("esquerda" if lado_p2=="direita" else "direita"))

        # P3 Lateral
        if self.tem_p3:
            lado_p3 = self.p3["lado"].value
            x3 = base_x + (w1 * scale) if lado_p3 == "direita" else base_x - (w3 * scale)
            draw_tech_peca(w3, h3, x3, base_y, self.p3_rodo, self.p3_saia, juncao=("esquerda" if lado_p3=="direita" else "direita"))

        # Furos (Cooktop e Bojo aparecendo sempre)
        for f in [self.f_bojo, self.f_cook]:
            if f["sw"].value:
                cur_x = base_x
                if f["peca"].value == "P2" and self.tem_p2: cur_x = base_x + (w1*scale) if self.p2["lado"].value=="direita" else base_x - (w2*scale)
                if f["peca"].value == "P3" and self.tem_p3: cur_x = base_x + (w1*scale) if self.p3["lado"].value=="direita" else base_x - (w3*scale)
                
                fx, fw, fh = self.to_f(f["x"].value)*scale, self.to_f(f["w"].value)*scale, self.to_f(f["h"].value)*scale
                self.canvas.shapes.append(cv.Rect(cur_x+fx-fw/2, base_y + 10, fw, fh, border_radius=2, paint=ft.Paint(style="stroke", color="blue", stroke_width=1)))
                self.canvas.shapes.append(cv.Text(cur_x+fx-10, base_y + fh/2 + 5, "EIXO", style=ft.TextStyle(size=7, color="blue")))

        self.canvas.update()

    def salvar(self, e):
        t = float(self.lbl_total.value.replace("R$ ","").replace(".","").replace(",","."))
        self.on_save_item({"ambiente": self.txt_ambiente.value, "material": self.mapa_precos[self.dd_pedra.value]['nome'] if self.dd_pedra.value else "N/A", "largura": self.p1["l"].value, "profundidade": self.p1["p"].value, "preco_total": t})