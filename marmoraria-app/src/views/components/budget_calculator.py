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
        self.tem_encaixe = False

    def build(self):
        # --- CARREGAR DADOS DO ESTOQUE ---
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = []
        for chapa in chapas:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('preco_m2', 0) or 0)
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=f"{nome} - R$ {preco:.2f}/m²"))
            self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- FUNÇÃO PARA TRATAR NÚMEROS (ACEITA PONTO OU VÍRGULA) ---
        def on_num_change(e):
            if e.control.value:
                e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # --- INPUTS BASE (TECLADO TEXT PARA LIBERAR VÍRGULA) ---
        kb_text = ft.KeyboardType.TEXT 
        self.txt_ambiente = ft.TextField(label="Ambiente", border_radius=8, height=45, value="Cozinha")
        self.dd_pedra = ft.Dropdown(label="Selecionar Pedra", options=opcoes_pedras, border_radius=8, height=45, on_change=self.calcular)
        self.txt_larg = ft.TextField(label="Compr. P1 (m)", value="1.00", expand=True, keyboard_type=kb_text, on_change=on_num_change)
        self.txt_prof = ft.TextField(label="Prof. P1 (m)", value="0.60", expand=True, keyboard_type=kb_text, on_change=on_num_change)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", expand=True, keyboard_type=kb_text, on_change=on_num_change)

        # --- CONFIGURAÇÃO DA PEÇA LATERAL (L) ---
        self.txt_larg_enc = ft.TextField(label="Compr. L (m)", value="0.80", expand=True, keyboard_type=kb_text, on_change=on_num_change, visible=False)
        self.txt_prof_enc = ft.TextField(label="Prof. L (m)", value="0.60", expand=True, keyboard_type=kb_text, on_change=on_num_change, visible=False)
        self.dd_lado_enc = ft.Dropdown(label="Colar na...", value="direita", visible=False, options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")], on_change=self.calcular)

        def campo_alt(val): 
            return ft.TextField(label="Alt (m)", value=val, width=75, height=40, text_size=12, keyboard_type=kb_text, on_change=on_num_change)

        # --- SELETORES DE ACABAMENTO (4 LADOS CADA) ---
        def criar_seletor_lados(prefixo):
            return {l: ft.Checkbox(label=l.capitalize()[:3], on_change=self.calcular) for l in ["fundo", "frente", "esquerda", "direita"]}

        self.p1_rodo = criar_seletor_lados("p1r"); self.p1_rodo["fundo"].value = True
        self.p1_saia = criar_seletor_lados("p1s"); self.p1_saia["frente"].value = True
        self.p2_rodo = criar_seletor_lados("p2r")
        self.p2_saia = criar_seletor_lados("p2s")
        
        self.txt_alt_rodo = campo_alt("0.10")
        self.txt_alt_saia = campo_alt("0.04")

        # --- FUROS (BOJO E COOKTOP) ---
        def ctrl_furo(label):
            return {
                "sw": ft.Switch(label=label, on_change=self.calcular),
                "peca": ft.Dropdown(value="P1", options=[ft.dropdown.Option("P1"), ft.dropdown.Option("P2")], width=70, height=40, text_size=11, on_change=self.calcular),
                "w": ft.TextField(label="Larg", value="0.50", width=70, height=40, text_size=11, on_change=on_num_change),
                "x": ft.TextField(label="Eixo", value="0.50", width=70, height=40, text_size=11, on_change=on_num_change)
            }
        self.f_bojo = ctrl_furo("Bojo")
        self.f_cook = ctrl_furo("Cooktop")

        self.canvas = cv.Canvas(width=350, height=350, shapes=[])
        self.lbl_total = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        # --- BOTÃO ALTERNAR ENCAIXE ---
        def toggle_l(e):
            self.tem_encaixe = not self.tem_encaixe
            self.txt_larg_enc.visible = self.txt_prof_enc.visible = self.dd_lado_enc.visible = self.tem_encaixe
            btn_l.text = "Remover Peça L" if self.tem_encaixe else "Adicionar Peça L"
            self.calcular()

        btn_l = ft.ElevatedButton("Adicionar Peça L", icon=ft.icons.ADD_BOX, on_click=toggle_l)

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([self.txt_ambiente, self.dd_pedra, ft.Row([self.txt_larg, self.txt_prof]), btn_l, ft.Row([self.txt_larg_enc, self.txt_prof_enc]), self.dd_lado_enc, self.txt_acab], spacing=10, scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Row([ft.Text("Rodo (Verm):"), self.txt_alt_rodo]), ft.Row(list(self.p1_rodo.values()), wrap=True),
                ft.Divider(),
                ft.Row([ft.Text("Saia (Azul):"), self.txt_alt_saia]), ft.Row(list(self.p1_saia.values()), wrap=True),
                ft.Divider(),
                ft.Text("Acabamentos Peça L (Se ativa):", size=11, weight="bold"),
                ft.Row(list(self.p2_rodo.values()), wrap=True), ft.Row(list(self.p2_saia.values()), wrap=True)
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.f_bojo["sw"], self.f_bojo["peca"], self.f_bojo["w"], self.f_bojo["x"]], spacing=5),
                ft.Row([self.f_cook["sw"], self.f_cook["peca"], self.f_cook["w"], self.f_cook["x"]], spacing=5)
            ]))
        ], height=350)

        return ft.Container(padding=10, content=ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()), ft.Text("Projeto de Bancada", weight="bold")]),
            ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
            ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), height=350, alignment=ft.alignment.center),
            ft.Container(padding=15, bgcolor=COLOR_WHITE, border_radius=10, content=ft.Row([self.lbl_total, ft.ElevatedButton("Salvar", on_click=self.salvar, height=45)], alignment="spaceBetween"))
        ], scroll=ft.ScrollMode.ALWAYS))

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            def f(v): return float(str(v).replace(",", ".")) if v else 0.0
            p_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            v_ml = f(self.txt_acab.value)
            
            l1, p1 = f(self.txt_larg.value), f(self.txt_prof.value)
            area = l1 * p1
            ml = sum(l1 if k in ["fundo", "frente"] else p1 for k, v in self.p1_rodo.items() if v.value)
            ml += sum(l1 if k in ["fundo", "frente"] else p1 for k, v in self.p1_saia.items() if v.value)

            if self.tem_encaixe:
                l2, p2 = f(self.txt_larg_enc.value), f(self.txt_prof_enc.value)
                area += l2 * p2
                ml += sum(l2 if k in ["fundo", "frente"] else p2 for k, v in self.p2_rodo.items() if v.value)
                ml += sum(l2 if k in ["fundo", "frente"] else p2 for k, v in self.p2_saia.items() if v.value)

            total = (area * p_m2) + (ml * v_ml)
            if self.f_bojo["sw"].value: total += 150
            if self.f_cook["sw"].value: total += 100

            self.lbl_total.value = f"R$ {total:,.2f}"
            self.desenhar(l1, p1, f(self.txt_larg_enc.value) if self.tem_encaixe else 0, f(self.txt_prof_enc.value) if self.tem_encaixe else 0)
            self.update()
        except: pass

    def desenhar(self, w1, h1, w2, h2):
        self.canvas.shapes.clear()
        scale = min(300/(w1+w2+0.5), 200/(max(h1, h2)+0.5)) * 0.7
        w1_px, h1_px = w1*scale, h1*scale
        w2_px, h2_px = w2*scale, h2*scale
        sx, sy = (350 - (w1_px + w2_px))/2, (350 - h1_px)/2

        # Peça 1
        self.canvas.shapes.append(cv.Rect(sx, sy, w1_px, h1_px, paint=ft.Paint(style="fill", color="#F5F5F5")))
        self.canvas.shapes.append(cv.Rect(sx, sy, w1_px, h1_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))
        
        # Acabamentos Técnicos P1
        for k, v in self.p1_rodo.items():
            if v.value:
                pts = {"fundo": (sx, sy, sx+w1_px, sy), "frente": (sx, sy+h1_px, sx+w1_px, sy+h1_px), "esquerda": (sx, sy, sx, sy+h1_px), "direita": (sx+w1_px, sy, sx+w1_px, sy+h1_px)}
                self.canvas.shapes.append(cv.Line(*pts[k], paint=ft.Paint(color="red", stroke_width=4)))
        for k, v in self.p1_saia.items():
            if v.value:
                pts = {"fundo": (sx, sy, sx+w1_px, sy), "frente": (sx, sy+h1_px, sx+w1_px, sy+h1_px), "esquerda": (sx, sy, sx, sy+h1_px), "direita": (sx+w1_px, sy, sx+w1_px, sy+h1_px)}
                self.canvas.shapes.append(cv.Line(*pts[k], paint=ft.Paint(color="blue", stroke_width=6)))

        # Peça Lateral (L)
        if self.tem_encaixe:
            ex = sx + w1_px if self.dd_lado_enc.value == "direita" else sx - w2_px
            self.canvas.shapes.append(cv.Rect(ex, sy, w2_px, h2_px, paint=ft.Paint(style="fill", color="#E8E8E8")))
            self.canvas.shapes.append(cv.Rect(ex, sy, w2_px, h2_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))
            # Acabamentos P2
            for k, v in self.p2_rodo.items():
                if v.value:
                    pts = {"fundo": (ex, sy, ex+w2_px, sy), "frente": (ex, sy+h2_px, ex+w2_px, sy+h2_px), "esquerda": (ex, sy, ex, sy+h2_px), "direita": (ex+w2_px, sy, ex+w2_px, sy+h2_px)}
                    self.canvas.shapes.append(cv.Line(*pts[k], paint=ft.Paint(color="red", stroke_width=4)))
            for k, v in self.p2_saia.items():
                if v.value:
                    pts = {"fundo": (ex, sy, ex+w2_px, sy), "frente": (ex, sy+h2_px, ex+w2_px, sy+h2_px), "esquerda": (ex, sy, ex, sy+h2_px), "direita": (ex+w2_px, sy, ex+w2_px, sy+h2_px)}
                    self.canvas.shapes.append(cv.Line(*pts[k], paint=ft.Paint(color="blue", stroke_width=6)))

        # Furos 
        for f in [self.f_bojo, self.f_cook]:
            if f["sw"].value:
                try:
                    bx = sx if f["peca"].value == "P1" else (sx + w1_px if self.dd_lado_enc.value == "direita" else sx - w2_px)
                    px = bx + (float(str(f["x"].value).replace(",",".")) * scale)
                    fw, fh = float(str(f["w"].value).replace(",",".")) * scale, 30
                    self.canvas.shapes.append(cv.Rect(px-fw/2, sy+15, fw, fh, border_radius=3, paint=ft.Paint(style="stroke", color="blue")))
                except: pass
        self.canvas.update()

    def salvar(self, e):
        if not self.dd_pedra.value: return
        total_puro = float(self.lbl_total.value.replace("R$ ","").replace(".","").replace(",","."))
        self.on_save_item({
            "ambiente": self.txt_ambiente.value, "material": self.mapa_precos[self.dd_pedra.value]['nome'],
            "largura": self.txt_larg.value, "profundidade": self.txt_prof.value, "preco_total": total_puro
        })