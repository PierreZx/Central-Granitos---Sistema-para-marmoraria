# src/views/components/budget_calculator.py

import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE
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
        except: return 0.0

    def build(self):
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = [ft.dropdown.Option(key=c['id'], text=f"{c.get('nome')} - R$ {float(c.get('preco_m2',0)):.2f}/m²") for c in chapas]
        for c in chapas: self.mapa_precos[c['id']] = {'nome': c.get('nome'), 'preco': float(c.get('preco_m2',0))}

        def on_num_change(e):
            if e.control.value and "," in e.control.value: e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # --- CAMPOS ---
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha", height=45)
        self.dd_pedra = ft.Dropdown(label="Material", options=opcoes_pedras, height=45, on_change=self.calcular)
        self.txt_acab_preco = ft.TextField(label="Preço Mão de Obra (R$/ML)", value="130.00", on_change=on_num_change)
        self.h_rodo = ft.TextField(label="Alt. Rodo (m)", value="0.10", width=100, on_change=on_num_change)
        self.h_saia = ft.TextField(label="Alt. Saia (m)", value="0.04", width=100, on_change=on_num_change)

        def criar_peca(nome, visivel=True):
            return {
                "l": ft.TextField(label=f"Comp. {nome}", value="1.00", expand=True, on_change=on_num_change, visible=visivel),
                "p": ft.TextField(label=f"Prof. {nome}", value="0.60", expand=True, on_change=on_num_change, visible=visivel),
                "lado": ft.Dropdown(label="Lado", value="direita", visible=visivel, options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")], on_change=self.calcular)
            }

        self.p1 = criar_peca("P1")
        self.p2 = criar_peca("P2", False)
        self.p3 = criar_peca("P3", False)

        def seletor(cor):
            return {l: ft.Checkbox(label=l[:3].upper(), on_change=self.calcular, fill_color=cor, scale=0.8) for l in ["fundo", "frente", "esquerda", "direita"]}

        self.p1_rodo = seletor("red"); self.p1_rodo["fundo"].value = True
        self.p1_saia = seletor("blue"); self.p1_saia["frente"].value = True
        self.p2_rodo = seletor("red"); self.p2_saia = seletor("blue")
        self.p3_rodo = seletor("red"); self.p3_saia = seletor("blue")

        def ctrl_furo(label):
            return {
                "sw": ft.Switch(label=label, on_change=self.calcular),
                "peca": ft.Dropdown(value="P1", options=[ft.dropdown.Option("P1"), ft.dropdown.Option("P2"), ft.dropdown.Option("P3")], width=80, on_change=self.calcular),
                "w": ft.TextField(label="L", value="0.50", width=65, on_change=on_num_change),
                "h": ft.TextField(label="P", value="0.40", width=65, on_change=on_num_change),
                "x": ft.TextField(label="X", value="0.50", width=65, on_change=on_num_change),
                "y": ft.TextField(label="Y", value="0.30", width=65, on_change=on_num_change) # Novo campo Y
            }
        self.f_bojo = ctrl_furo("Bojo")
        self.f_cook = ctrl_furo("Cooktop")

        self.canvas = cv.Canvas(width=350, height=350)
        self.lbl_total = ft.Text("R$ 0.00", size=22, weight="bold", color=COLOR_PRIMARY)

        def toggle_p(n):
            if n==2: self.tem_p2 = not self.tem_p2; p, v = self.p2, self.tem_p2
            else: self.tem_p3 = not self.tem_p3; p, v = self.p3, self.tem_p3
            p["l"].visible = p["p"].visible = p["lado"].visible = v
            self.calcular()

        tabs = ft.Tabs(tabs=[
            ft.Tab(text="Medidas", content=ft.Column([
                self.txt_ambiente, self.dd_pedra, ft.Row([self.p1["l"], self.p1["p"]]),
                ft.Row([ft.ElevatedButton("+ P2", on_click=lambda _: toggle_p(2)), ft.ElevatedButton("+ P3", on_click=lambda _: toggle_p(3))]),
                ft.Column([ft.Row([self.p2["l"], self.p2["p"]]), self.p2["lado"]]),
                ft.Column([ft.Row([self.p3["l"], self.p3["p"]]), self.p3["lado"]]),
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabamento", content=ft.Column([
                ft.Row([self.h_rodo, self.h_saia]),
                ft.Text("P1 - Rodo / Saia", weight="bold"),
                ft.Row([*self.p1_rodo.values()], wrap=True), ft.Row([*self.p1_saia.values()], wrap=True),
                ft.Divider(),
                ft.Text("P2 - Rodo / Saia", weight="bold"),
                ft.Row([*self.p2_rodo.values()], wrap=True), ft.Row([*self.p2_saia.values()], wrap=True),
                ft.Divider(),
                ft.Text("P3 - Rodo / Saia", weight="bold"),
                ft.Row([*self.p3_rodo.values()], wrap=True), ft.Row([*self.p3_saia.values()], wrap=True),
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.f_bojo["sw"], self.f_bojo["peca"]]),
                ft.Row([self.f_bojo["w"], self.f_bojo["h"], self.f_bojo["x"], self.f_bojo["y"]], spacing=5),
                ft.Divider(),
                ft.Row([self.f_cook["sw"], self.f_cook["peca"]]),
                ft.Row([self.f_cook["w"], self.f_cook["h"], self.f_cook["x"], self.f_cook["y"]], spacing=5),
            ], scroll=ft.ScrollMode.ALWAYS))
        ], expand=1)

        return ft.Container(padding=10, content=ft.Column([
            ft.Container(tabs, height=300, bgcolor=COLOR_WHITE, border_radius=10, padding=10),
            ft.Container(self.canvas, bgcolor="white", border_radius=10, border=ft.border.all(1, "#ddd"), height=350, alignment=ft.alignment.center),
            ft.Row([self.lbl_total, ft.ElevatedButton("Salvar", on_click=self.salvar)], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.ALWAYS))

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            p_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            v_ml = self.to_f(self.txt_acab_preco.value)
            
            lados_ocupados = []
            if self.tem_p2: lados_ocupados.append(self.p2["lado"].value)
            if self.tem_p3: lados_ocupados.append(self.p3["lado"].value)

            for lado in ["esquerda", "direita"]:
                is_ocupado = lado in lados_ocupados
                self.p1_rodo[lado].disabled = is_ocupado
                self.p1_saia[lado].disabled = is_ocupado
                if is_ocupado: self.p1_rodo[lado].value = self.p1_saia[lado].value = False

            total_m2 = 0; total_ml = 0

            def calc_peca(l_ctrl, p_ctrl, rodo, saia, is_p1=False):
                l, p = self.to_f(l_ctrl.value), self.to_f(p_ctrl.value)
                ml = 0
                for lado, cb in rodo.items():
                    if cb.value:
                        if not is_p1 and (lado == "esquerda" or lado == "direita"): ml += max(0, p - self.to_f(self.p1["p"].value))
                        else: ml += (l if lado in ["fundo", "frente"] else p)
                for lado, cb in saia.items():
                    if cb.value:
                        if not is_p1 and (lado == "esquerda" or lado == "direita"): ml += max(0, p - self.to_f(self.p1["p"].value))
                        else: ml += (l if lado in ["fundo", "frente"] else p)
                return (l * p), ml

            m1, ml1 = calc_peca(self.p1["l"], self.p1["p"], self.p1_rodo, self.p1_saia, True)
            total_m2 += m1; total_ml += ml1
            if self.tem_p2:
                m2, ml2 = calc_peca(self.p2["l"], self.p2["p"], self.p2_rodo, self.p2_saia)
                total_m2 += m2; total_ml += ml2
            if self.tem_p3:
                m3, ml3 = calc_peca(self.p3["l"], self.p3["p"], self.p3_rodo, self.p3_saia)
                total_m2 += m3; total_ml += ml3

            if self.f_bojo["sw"].value: total_ml += (self.to_f(self.f_bojo["w"].value) + self.to_f(self.f_bojo["h"].value)) * 2
            if self.f_cook["sw"].value: total_ml += (self.to_f(self.f_cook["w"].value) + self.to_f(self.f_cook["h"].value)) * 2

            v_final = (total_m2 * p_m2) + (total_ml * v_ml)
            self.lbl_total.value = f"R$ {v_final:,.2f}"
            self.desenhar()
            self.update()
        except: pass

    def desenhar(self):
        self.canvas.shapes.clear()
        w1, h1 = max(0.01, self.to_f(self.p1["l"].value)), max(0.01, self.to_f(self.p1["p"].value))
        w2, h2 = (self.to_f(self.p2["l"].value), self.to_f(self.p2["p"].value)) if self.tem_p2 else (0,0)
        w3, h3 = (self.to_f(self.p3["l"].value), self.to_f(self.p3["p"].value)) if self.tem_p3 else (0,0)

        total_w = w1 + w2 + w3
        max_h = max(h1, h2, h3)
        
        # Escala segura para caber no Canvas (considerando margens)
        scale = min(320 / max(0.1, total_w), 320 / max(0.1, max_h))

        # Posição central dinâmica
        canvas_mid_x = 175
        canvas_mid_y = 175
        
        p1_x = canvas_mid_x - (w1 * scale) / 2
        if self.tem_p2 and self.p2["lado"].value == "esquerda": p1_x += (w2 * scale) / 2
        if self.tem_p3 and self.p3["lado"].value == "esquerda": p1_x += (w3 * scale) / 2
        
        p1_y = canvas_mid_y - (max_h * scale) / 2

        def draw_box(w, h, x, y, rodo, saia, j_esq, j_dir):
            wp, hp = w*scale, h*scale
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="fill", color="#F5F5F5")))
            self.canvas.shapes.append(cv.Rect(x, y, wp, hp, paint=ft.Paint(style="stroke", color="black")))
            self.canvas.shapes.append(cv.Text(x + 5, y + 5, f"{w}x{h}", style=ft.TextStyle(size=9, weight="bold")))

            lados = {"fundo": (x,y,x+wp,y), "frente": (x,y+hp,x+wp,y+hp), "esquerda": (x,y,x,y+hp), "direita": (x+wp,y,x+wp,y+hp)}
            for lado, (x1, y1, x2, y2) in lados.items():
                if (lado == "esquerda" and j_esq) or (lado == "direita" and j_dir):
                    if h <= h1: continue
                    else: y1 = y + h1*scale
                if rodo[lado].value:
                    self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="red", stroke_width=3)))
                    self.canvas.shapes.append(cv.Text((x1+x2)/2 - 10, y1-15 if lado=="fundo" else y1+5, f"R:{w if lado in ['fundo','frente'] else h}", style=ft.TextStyle(size=8, color="red")))
                if saia[lado].value:
                    off = 4 if rodo[lado].value else 0
                    self.canvas.shapes.append(cv.Line(x1+off, y1+off, x2+off, y2+off, paint=ft.Paint(color="blue", stroke_width=4)))
                    self.canvas.shapes.append(cv.Text((x1+x2)/2 - 10, y1+12 if lado=="fundo" else y1-15, f"S:{w if lado in ['fundo','frente'] else h}", style=ft.TextStyle(size=8, color="blue")))

        # P1
        j1_e = (self.tem_p2 and self.p2["lado"].value=="esquerda") or (self.tem_p3 and self.p3["lado"].value=="esquerda")
        j1_d = (self.tem_p2 and self.p2["lado"].value=="direita") or (self.tem_p3 and self.p3["lado"].value=="direita")
        draw_box(w1, h1, p1_x, p1_y, self.p1_rodo, self.p1_saia, j1_e, j1_d)
        
        # P2 e P3 e Furos
        pecas_coords = {"P1": (p1_x, p1_y, w1, h1)}
        for p_idx, tem, dados, rodo, saia in [("P2", self.tem_p2, self.p2, self.p2_rodo, self.p2_saia), ("P3", self.tem_p3, self.p3, self.p3_rodo, self.p3_saia)]:
            if tem:
                lx, px = self.to_f(dados["l"].value), self.to_f(dados["p"].value)
                pos_x = (p1_x + w1*scale) if dados["lado"].value == "direita" else (p1_x - lx*scale)
                draw_box(lx, px, pos_x, p1_y, rodo, saia, j_esq=(dados["lado"].value=="direita"), j_dir=(dados["lado"].value=="esquerda"))
                pecas_coords[p_idx] = (pos_x, p1_y, lx, px)

        # Desenho dos Furos
        for f, cor, tipo in [(self.f_bojo, "orange", "cuba"), (self.f_cook, "green", "bocas")]:
            if f["sw"].value:
                p_ref = f["peca"].value
                if p_ref in pecas_coords:
                    bx, by, bw, bh = pecas_coords[p_ref]
                    fw, fh, fx, fy = self.to_f(f["w"].value)*scale, self.to_f(f["h"].value)*scale, self.to_f(f["x"].value)*scale, self.to_f(f["y"].value)*scale
                    f_x_pos, f_y_pos = bx + fx - fw/2, by + fy
                    
                    self.canvas.shapes.append(cv.Rect(f_x_pos, f_y_pos, fw, fh, border_radius=5 if tipo=="cuba" else 2, paint=ft.Paint(style="stroke", color=cor, stroke_width=2)))
                    if tipo == "cuba":
                        self.canvas.shapes.append(cv.Circle(f_x_pos + fw/2, f_y_pos + fh/2, 3, paint=ft.Paint(color=cor)))
                    else:
                        for ox, oy in [(-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2), (0,0)]:
                            self.canvas.shapes.append(cv.Circle(f_x_pos + fw/2 + (ox*fw), f_y_pos + fh/2 + (oy*fh), 3.5, paint=ft.Paint(style="stroke", color=cor)))

        self.canvas.update()

    def salvar(self, e):
        try:
            # 1. Extração e limpeza do preço total
            # Transformamos "R$ 2.462,00" em um número real 2462.00
            preco_limpo = self.lbl_total.value.replace("R$ ", "").replace(".", "").replace(",", ".")
            preco_total = float(preco_limpo)

            # 2. Montagem do dicionário estruturado
            # Guardamos todas as configurações que definimos na tela
            dados_orcamento = {
                "ambiente": self.txt_ambiente.value,
                "material": self.mapa_precos[self.dd_pedra.value]['nome'] if self.dd_pedra.value else "Não selecionado",
                "preco_total": preco_total,
                "configuracoes_tecnicas": {
                    "valor_mao_de_obra_ml": self.to_f(self.txt_acab_preco.value),
                    "altura_rodobanca": self.to_f(self.h_rodo.value),
                    "altura_saia": self.to_f(self.h_saia.value),
                },
                "pecas": {
                    "p1": {
                        "l": self.to_f(self.p1["l"].value),
                        "p": self.to_f(self.p1["p"].value),
                        "acabamentos": {
                            "rodo": {k: v.value for k, v in self.p1_rodo.items()},
                            "saia": {k: v.value for k, v in self.p1_saia.items()}
                        }
                    }
                },
                "furos_incluidos_no_ml": {
                    "bojo": self.f_bojo["sw"].value,
                    "cooktop": self.f_cook["sw"].value
                }
            }

            # 3. Adiciona P2 e P3 apenas se você as ativou no botão "+"
            if self.tem_p2:
                dados_orcamento["pecas"]["p2"] = {
                    "l": self.to_f(self.p2["l"].value),
                    "p": self.to_f(self.p2["p"].value),
                    "lado": self.p2["lado"].value,
                    "acabamentos": {
                        "rodo": {k: v.value for k, v in self.p2_rodo.items()},
                        "saia": {k: v.value for k, v in self.p2_saia.items()}
                    }
                }
            
            if self.tem_p3:
                dados_orcamento["pecas"]["p3"] = {
                    "l": self.to_f(self.p3["l"].value),
                    "p": self.to_f(self.p3["p"].value),
                    "lado": self.p3["lado"].value,
                    "acabamentos": {
                        "rodo": {k: v.value for k, v in self.p3_rodo.items()},
                        "saia": {k: v.value for k, v in self.p3_saia.items()}
                    }
                }

            # 4. Envia os dados para o Firebase através do callback que definimos no início
            self.on_save_item(dados_orcamento)
            
            # Mostra o aviso de sucesso na parte de baixo da tela
            self.page.snack_bar = ft.SnackBar(ft.Text("Orçamento salvo com sucesso!"), bgcolor="green")
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            print(f"Erro ao salvar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text("Erro ao salvar. Verifique se os campos estão preenchidos."), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()