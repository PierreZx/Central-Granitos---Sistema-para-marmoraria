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

    def build(self):
        # --- CARREGAR DADOS DO ESTOQUE ---
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = []
        for chapa in chapas:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('preco_m2', 0) or 0)
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=f"{nome} - R$ {preco:.2f}/m²"))
            self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- INPUTS BASE ---
        self.txt_ambiente = ft.TextField(label="Ambiente", border_radius=8, height=45, value="Cozinha")
        self.dd_pedra = ft.Dropdown(label="Selecionar Pedra", options=opcoes_pedras, border_radius=8, height=45)
        self.txt_larg = ft.TextField(label="Comprimento (m)", value="1.00", expand=True, keyboard_type="number", on_change=self.calcular)
        self.txt_prof = ft.TextField(label="Profundidade (m)", value="0.60", expand=True, keyboard_type="number", on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", expand=True, keyboard_type="number", on_change=self.calcular)

        def campo_alt(val): 
            return ft.TextField(label="Alt (m)", value=val, width=75, height=40, text_size=12, on_change=self.calcular)

        # --- ACABAMENTOS ---
        self.chk_rfundo = ft.Checkbox(label="Rodo Fundo", value=True, on_change=self.calcular)
        self.txt_rf_a = campo_alt("0.10")
        self.chk_resq = ft.Checkbox(label="Rodo Esq", on_change=self.calcular)
        self.txt_re_a = campo_alt("0.10")
        self.chk_rdir = ft.Checkbox(label="Rodo Dir", on_change=self.calcular)
        self.txt_rd_a = campo_alt("0.10")

        self.chk_sfrente = ft.Checkbox(label="Saia Frente", value=True, on_change=self.calcular)
        self.txt_sfr_a = campo_alt("0.04")
        self.chk_sesq = ft.Checkbox(label="Saia Esq", on_change=self.calcular)
        self.txt_se_a = campo_alt("0.04")
        self.chk_sdir = ft.Checkbox(label="Saia Dir", on_change=self.calcular)
        self.txt_sd_a = campo_alt("0.04")

        # --- FUROS ---
        self.sw_bojo = ft.Switch(label="Bojo", value=False, on_change=self.calcular)
        self.bojo_w = ft.TextField(label="Larg (m)", value="0.50", width=70, height=40, text_size=11, on_change=self.calcular)
        self.bojo_h = ft.TextField(label="Prof (m)", value="0.40", width=70, height=40, text_size=11, on_change=self.calcular)
        self.bojo_x = ft.TextField(label="Eixo (m)", value="0.50", width=70, height=40, text_size=11, on_change=self.calcular)

        self.sw_cook = ft.Switch(label="Cooktop", value=False, on_change=self.calcular)
        self.cook_w = ft.TextField(label="Larg (m)", value="0.55", width=70, height=40, text_size=11, on_change=self.calcular)
        self.cook_h = ft.TextField(label="Prof (m)", value="0.45", width=70, height=40, text_size=11, on_change=self.calcular)
        self.cook_x = ft.TextField(label="Eixo (m)", value="1.50", width=70, height=40, text_size=11, on_change=self.calcular)

        self.canvas = cv.Canvas(width=350, height=300, shapes=[])
        self.lbl_valor = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        # --- TABS ORGANIZADAS ---
        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([self.txt_ambiente, self.dd_pedra, ft.Row([self.txt_larg, self.txt_prof]), self.txt_acab], spacing=10)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Text("Rodobancas (Parede)", size=11, weight="bold"),
                ft.Row([self.chk_rfundo, self.txt_rf_a], alignment="spaceBetween"),
                ft.Row([self.chk_resq, self.txt_re_a], alignment="spaceBetween"),
                ft.Row([self.chk_rdir, self.txt_rd_a], alignment="spaceBetween"),
                ft.Divider(),
                ft.Text("Saias (Acabamento)", size=11, weight="bold"),
                ft.Row([self.chk_sfrente, self.txt_sfr_a], alignment="spaceBetween"),
                ft.Row([self.chk_sesq, self.txt_se_a], alignment="spaceBetween"),
                ft.Row([self.chk_sdir, self.txt_sd_a], alignment="spaceBetween"),
            ], scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.sw_bojo, ft.Text("Furo Bojo")]),
                ft.Row([self.bojo_w, self.bojo_h, self.bojo_x], spacing=5),
                ft.Divider(),
                ft.Row([self.sw_cook, ft.Text("Furo Cooktop")]),
                ft.Row([self.cook_w, self.cook_h, self.cook_x], spacing=5),
            ]))
        ], height=320)

        self.dd_pedra.on_change = self.calcular

        return ft.Container(
            padding=10, bgcolor=COLOR_BACKGROUND,
            content=ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()), ft.Text("Nova Peça", weight="bold")]),
                ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
                ft.Text("Visualização Técnica", weight="bold", size=14),
                ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), alignment=ft.alignment.center, height=300),
                ft.Container(padding=15, bgcolor=COLOR_WHITE, border_radius=10, content=ft.Row([
                    ft.Column([ft.Text("Total:", size=12), self.lbl_valor]),
                    ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self.salvar, height=45)
                ], alignment="spaceBetween"))
            ], scroll=ft.ScrollMode.ALWAYS)
        )

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            l, p, v_ml = float(self.txt_larg.value or 0), float(self.txt_prof.value or 0), float(self.txt_acab.value or 0)
            if l == 0 or p == 0: return

            total = (l * p * self.mapa_precos[self.dd_pedra.value]['preco'])
            ml = 0
            for chk, val in [(self.chk_rfundo, l), (self.chk_resq, p), (self.chk_rdir, p), (self.chk_sfrente, l), (self.chk_sesq, p), (self.chk_sdir, p)]:
                if chk.value: ml += val
            
            total += (ml * v_ml)
            if self.sw_bojo.value: total += 150
            if self.sw_cook.value: total += 100

            self.lbl_valor.value = f"R$ {total:,.2f}"
            self.desenhar(l, p)
            self.update()
        except: pass

    def desenhar(self, w, h):
        self.canvas.shapes.clear()
        scale = min(300/w, 200/h) * 0.7
        w_px, h_px = w*scale, h*scale
        sx, sy = (350-w_px)/2, (300-h_px)/2
        
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style="fill", color="#F0F0F0")))
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))

        def draw_tech(chk, val, x1, y1, x2, y2, tx, ty, color, pref):
            if chk.value:
                self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color=color, stroke_width=5)))
                self.canvas.shapes.append(cv.Text(tx, ty, f"{pref}:{val}m", style=ft.TextStyle(size=9, color=color)))

        draw_tech(self.chk_rfundo, self.txt_rf_a.value, sx, sy, sx+w_px, sy, sx+w_px/2-20, sy-15, "red", "R")
        draw_tech(self.chk_sfrente, self.txt_sfr_a.value, sx, sy+h_px, sx+w_px, sy+h_px, sx+w_px/2-20, sy+h_px+5, "blue", "S")

        def draw_furo(sw, fx, fw, fh):
            if sw.value:
                pos_x = sx + (float(fx.value or 0) * scale)
                fw_px, fh_px = float(fw.value or 0) * scale, float(fh.value or 0) * scale
                self.canvas.shapes.append(cv.Rect(pos_x - fw_px/2, sy + (h_px-fh_px)/2, fw_px, fh_px, border_radius=3, paint=ft.Paint(style="stroke", color="blue", stroke_width=1)))
                self.canvas.shapes.append(cv.Text(pos_x - 15, sy + h_px/2 - 5, "EIXO", style=ft.TextStyle(size=7, color="blue")))

        draw_furo(self.sw_bojo, self.bojo_x, self.bojo_w, self.bojo_h)
        draw_furo(self.sw_cook, self.cook_x, self.cook_w, self.cook_h)

        self.canvas.shapes.append(cv.Text(sx+w_px/2-10, sy-35, f"{w}m", style=ft.TextStyle(size=11, weight="bold")))
        self.canvas.shapes.append(cv.Text(sx-50, sy+h_px/2-10, f"{h}m", style=ft.TextStyle(size=11, weight="bold")))
        self.canvas.update()

    def salvar(self, e):
        if not self.dd_pedra.value or self.lbl_valor.value == "R$ 0.00": return
        
        # Limpa formatação para salvar número puro
        total_puro = float(self.lbl_valor.value.replace("R$ ", "").replace(".", "").replace(",", "."))
        
        item_dict = {
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos[self.dd_pedra.value]['nome'],
            "largura": self.txt_larg.value,
            "profundidade": self.txt_prof.value,
            "preco_total": total_puro
        }
        self.on_save_item(item_dict)