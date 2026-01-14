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

        def seletor_lados(cor):
            return {l: ft.Checkbox(label=l.capitalize()[:3], on_change=self.calcular, fill_color=cor) for l in ["fundo", "frente", "esquerda", "direita"]}

        # Separando explicitamente instâncias de Checkbox para Rodo e Saia
        self.p1_rodo = seletor_lados("red"); self.p1_rodo["fundo"].value = True
        self.p1_saia = seletor_lados("blue"); self.p1_saia["frente"].value = True
        self.p2_rodo = seletor_lados("red"); self.p2_saia = seletor_lados("blue")
        self.p3_rodo = seletor_lados("red"); self.p3_saia = seletor_lados("blue")

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
            if n == 2: self.tem_p2 = not self.tem_p2; p, v = self.p2, self.tem_p2
            else: self.tem_p3 = not self.tem_p3; p, v = self.p3, self.tem_p3
            p["l"].visible = p["p"].visible = p["lado"].visible = v
            self.calcular()

        def layout_acabamentos(titulo_peca, dict_rodo, dict_saia):
            return ft.Column([
                ft.Text(f"--- {titulo_peca} ---", weight="bold", size=14),
                ft.Text("Rodobanca (Vermelho)", size=12, color="red"),
                ft.Row([*dict_rodo.values()], wrap=True, spacing=0),
                ft.Text("Saia (Azul)", size=12, color="blue"),
                ft.Row([*dict_saia.values()], wrap=True, spacing=0),
                ft.Divider()
            ], spacing=5)

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
                layout_acabamentos("PEÇA 1", self.p1_rodo, self.p1_saia),
                layout_acabamentos("PEÇA 2", self.p2_rodo, self.p2_saia),
                layout_acabamentos("PEÇA 3", self.p3_rodo, self.p3_saia),
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.f_bojo["sw"], self.f_bojo["peca"]]),
                ft.Row([self.f_bojo["w"], self.f_bojo["h"], self.f_bojo["x"]], spacing=5),
                ft.Divider(),
                ft.Row([self.f_cook["sw"], self.f_cook["peca"]]),
                ft.Row([self.f_cook["w"], self.f_cook["h"], self.f_cook["x"]], spacing=5),
            ]))
        ], height=300)

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

        total_w = w1 + (w2 if self.tem_p2 else 0) + (w3 if self.tem_p3 else 0)
        max_h = max(h1, h2, h3)
        scale = min(280 / max(0.1, total_w), 280 / max(0.1, max_h))

        offset_x = 175 - (total_w * scale) / 2
        p1_x = offset_x + (w2 * scale if (self.tem_p2 and self.p2["lado"].value == "esquerda") else 0)
        if self.tem_p3 and self.p3["lado"].value == "esquerda": p1_x += (w3 * scale)
        p1_y = 175 - (max_h * scale) / 2

        def draw_peca(w, h, x, y, rodo, saia, j_esq, j_dir):
            wp, hp = w*scale, h*scale
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="fill", color="#F5F5F5")))
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="stroke", color="black", stroke_width=1)))
            self.canvas.shapes.append(cv.Text(x + wp/2 - 15, y + hp/2 - 5, f"{w}x{h}", style=ft.TextStyle(size=10, weight="bold")))

            lados = {"fundo": (x,y,x+wp,y), "frente": (x,y+hp,x+wp,y+hp), "esquerda": (x,y,x,y+hp), "direita": (x+wp,y,x+wp,y+hp)}
            for lado, (x1, y1, x2, y2) in lados.items():
                if (lado == "esquerda" and j_esq) or (lado == "direita" and j_dir): continue
                if rodo[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="red", stroke_width=3)))
                    self.canvas.shapes.append(cv.Text((x1+x2)/2 - 10, y1-12 if lado=="fundo" else y1+5, f"R:{w if lado in ['fundo','frente'] else h}", style=ft.TextStyle(size=8, color="red")))
                if saia[lado].value:
                    off = 4 if rodo[lado].value else 0
                    self.canvas.shapes.append(cv.Line(x1+off, y1+off, x2+off, y2+off, paint=ft.Paint(color="blue", stroke_width=4)))
                    self.canvas.shapes.append(cv.Text((x1+x2)/2 - 10, y1+12 if lado=="fundo" else y1-15, f"S:{w if lado in ['fundo','frente'] else h}", style=ft.TextStyle(size=8, color="blue")))

        # P1, P2 e P3
        j1_e = (self.tem_p2 and self.p2["lado"].value == "esquerda") or (self.tem_p3 and self.p3["lado"].value == "esquerda")
        j1_d = (self.tem_p2 and self.p2["lado"].value == "direita") or (self.tem_p3 and self.p3["lado"].value == "direita")
        draw_peca(w1, h1, p1_x, p1_y, self.p1_rodo, self.p1_saia, j1_e, j1_d)

        for p_idx, tem, dados, rodo, saia in [("P2", self.tem_p2, self.p2, self.p2_rodo, self.p2_saia), ("P3", self.tem_p3, self.p3, self.p3_rodo, self.p3_saia)]:
            if tem:
                lx, px = self.to_f(dados["l"].value), self.to_f(dados["p"].value)
                pos_x = (p1_x + w1*scale) if dados["lado"].value == "direita" else (p1_x - lx*scale)
                draw_peca(lx, px, pos_x, p1_y, rodo, saia, j_esq=(dados["lado"].value=="direita"), j_dir=(dados["lado"].value=="esquerda"))

        # Furos corrigidos
        for f, cor in [(self.f_bojo, "orange"), (self.f_cook, "green")]:
            if f["sw"].value:
                p_ref = f["peca"].value
                bx = p1_x
                if p_ref == "P2" and self.tem_p2: bx = (p1_x + w1*scale) if self.p2["lado"].value=="direita" else (p1_x - self.to_f(self.p2["l"].value)*scale)
                if p_ref == "P3" and self.tem_p3: bx = (p1_x + w1*scale) if self.p3["lado"].value=="direita" else (p1_x - self.to_f(self.p3["l"].value)*scale)
                
                fx, fw, fh = self.to_f(f["x"].value)*scale, self.to_f(f["w"].value)*scale, self.to_f(f["h"].value)*scale
                self.canvas.shapes.append(cv.Rect(bx+fx-fw/2, p1_y+10, fw, fh, paint=ft.Paint(style="stroke", color=cor, stroke_width=2)))
                self.canvas.shapes.append(cv.Text(bx+fx-10, p1_y+15, f.get("label", "F"), style=ft.TextStyle(size=8, color=cor)))

        self.canvas.update()

    def salvar(self, e):
        try:
            # 1. Extração e limpeza do preço total
            # Remove "R$ ", pontos de milhar e troca vírgula por ponto
            preco_str = self.lbl_total.value.replace("R$ ", "").replace(".", "").replace(",", ".")
            preco_total = float(preco_str)

            # 2. Montagem do dicionário com os detalhes técnicos
            # Aqui salvamos o ambiente, material e as medidas das peças ativas
            dados_orcamento = {
                "ambiente": self.txt_ambiente.value,
                "material": self.mapa_precos[self.dd_pedra.value]['nome'] if self.dd_pedra.value else "Não selecionado",
                "preco_total": preco_total,
                "mao_de_obra_ml": self.to_f(self.txt_acab.value),
                "peças": {
                    "p1": {
                        "l": self.to_f(self.p1["l"].value),
                        "p": self.to_f(self.p1["p"].value)
                    }
                }
            }

            # 3. Adiciona P2 e P3 apenas se estiverem ativas (visíveis)
            if self.tem_p2:
                dados_orcamento["peças"]["p2"] = {
                    "l": self.to_f(self.p2["l"].value),
                    "p": self.to_f(self.p2["p"].value),
                    "lado": self.p2["lado"].value
                }
            
            if self.tem_p3:
                dados_orcamento["peças"]["p3"] = {
                    "l": self.to_f(self.p3["l"].value),
                    "p": self.to_f(self.p3["p"].value),
                    "lado": self.p3["lado"].value
                }

            # 4. Inclui informações de furos se estiverem marcados
            dados_orcamento["furos"] = {
                "bojo": self.f_bojo["sw"].value,
                "cooktop": self.f_cook["sw"].value
            }

            # 5. Chama o callback passado pelo componente pai (geralmente para salvar no Firebase)
            self.on_save_item(dados_orcamento)
            
            # Feedback visual simples (opcional)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Orçamento calculado e enviado!")))

        except Exception as ex:
            print(f"Erro ao salvar: {ex}")
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Erro ao processar valores. Verifique os campos.")))