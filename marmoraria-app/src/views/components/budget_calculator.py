# src/views/components/budget_calculator.py

import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND
from src.services import firebase_service

class BudgetCalculator(ft.UserControl):
    def __init__(self, page, on_save_item, on_cancel, item=None): # Ajustado para bater com budget_view
        super().__init__()
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        self.item_para_editar = item 
        self.mapa_precos = {}

    def build(self):
        # --- CARREGAR DADOS ---
        chapas = firebase_service.get_collection("estoque") # Ajustado para o seu serviço atual
        opcoes_pedras = []
        for chapa in chapas:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('preco_m2', 0) or 0) # Ajustado para preco_m2
            txt_op = f"{nome} - R$ {preco:.2f}/m²"
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=txt_op))
            self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- COMPONENTES DA INTERFACE ---
        self.txt_ambiente = ft.TextField(label="Ambiente (Ex: Cozinha)", border_radius=8, expand=True, height=45, text_size=14)
        self.dd_pedra = ft.Dropdown(label="Pedra", options=opcoes_pedras, border_radius=8, expand=True, height=45, text_size=14)
        self.txt_larg = ft.TextField(label="Largura (m)", suffix_text="m", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        self.txt_prof = ft.TextField(label="Profund. (m)", suffix_text="m", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        self.txt_acab = ft.TextField(label="R$/m Linear", value="130.00", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)

        def criar_linha_config(label_chk, valor_padrao_alt):
            chk = ft.Checkbox(label=label_chk, value=False)
            txt_comp = ft.TextField(label="Comp (m)", width=90, height=40, text_size=12, disabled=True, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.colors.GREY_50)
            txt_alt = ft.TextField(label="Alt (m)", value=valor_padrao_alt, width=80, height=40, text_size=12, disabled=True, keyboard_type=ft.KeyboardType.NUMBER)
            return chk, txt_comp, txt_alt

        # Rodabancas
        self.chk_rfundo, self.txt_rf_c, self.txt_rf_a = criar_linha_config("Fundo", "0.10")
        self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a = criar_linha_config("Frente", "0.10")
        self.chk_resq, self.txt_re_c, self.txt_re_a = criar_linha_config("Lat. Esq", "0.10")
        self.chk_rdir, self.txt_rd_c, self.txt_rd_a = criar_linha_config("Lat. Dir", "0.10")

        # Saias
        self.chk_sfundo, self.txt_sf_c, self.txt_sf_a = criar_linha_config("Fundo", "0.04")
        self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a = criar_linha_config("Frente", "0.04")
        self.chk_sesq, self.txt_se_c, self.txt_se_a = criar_linha_config("Lat. Esq", "0.04")
        self.chk_sdir, self.txt_sd_c, self.txt_sd_a = criar_linha_config("Lat. Dir", "0.04")

        # Recortes
        self.chk_cuba = ft.Checkbox(label="Cuba", value=False)
        self.txt_pos_cuba = ft.TextField(label="Eixo (m)", value="0.50", width=80, height=40, text_size=12, disabled=True)
        self.chk_cook = ft.Checkbox(label="Cooktop", value=False)
        self.txt_pos_cook = ft.TextField(label="Eixo (m)", value="1.50", width=80, height=40, text_size=12, disabled=True)

        self.canvas = cv.Canvas(width=400, height=350, shapes=[])
        self.lbl_valor = ft.Text("R$ 0.00", size=28, weight="bold", color=COLOR_PRIMARY)
        self.valor_final = 0.0
        self.area_final = 0.0

        # --- EVENTOS ---
        inputs_calc = [
            self.txt_larg, self.txt_prof, self.txt_acab, self.dd_pedra, 
            self.txt_rf_a, self.txt_rf_c, self.txt_rfr_a, self.txt_rfr_c, self.txt_re_a, self.txt_re_c, self.txt_rd_a, self.txt_rd_c,
            self.txt_sf_a, self.txt_sf_c, self.txt_sfr_a, self.txt_sfr_c, self.txt_se_a, self.txt_se_c, self.txt_sd_a, self.txt_sd_c,
            self.txt_pos_cuba, self.txt_pos_cook
        ]
        for i in inputs_calc: i.on_change = self.calcular

        inputs_toggle = [
            self.chk_rfundo, self.chk_rfrente, self.chk_resq, self.chk_rdir, 
            self.chk_sfundo, self.chk_sfrente, self.chk_sesq, self.chk_sdir, 
            self.chk_cuba, self.chk_cook
        ]
        for i in inputs_toggle: i.on_change = self.toggle_campos

        # Preencher edição se houver
        if self.item_para_editar: 
            self.txt_ambiente.value = self.item_para_editar.get('ambiente', '')
            # ... lógica de carregar o resto ...
            self.calcular(None, update_ui=False)

        def row_compacta(chk, txt_c, txt_a):
            return ft.Row([chk, txt_c, txt_a], spacing=5)

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([self.txt_ambiente, self.dd_pedra, ft.Row([self.txt_larg, self.txt_prof]), self.txt_acab])),
            ft.Tab(text="Rodobanca", content=ft.Column([row_compacta(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a), row_compacta(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a), row_compacta(self.chk_resq, self.txt_re_c, self.txt_re_a), row_compacta(self.chk_rdir, self.txt_rd_c, self.txt_rd_a)])),
            ft.Tab(text="Saia", content=ft.Column([row_compacta(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a), row_compacta(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a), row_compacta(self.chk_sesq, self.txt_se_c, self.txt_se_a), row_compacta(self.chk_sdir, self.txt_sd_c, self.txt_sd_a)])),
            ft.Tab(text="Furos", content=ft.Column([ft.Row([self.chk_cuba, self.txt_pos_cuba]), ft.Row([self.chk_cook, self.txt_pos_cook])]))
        ], expand=True)

        return ft.Container(
            padding=10, bgcolor=COLOR_BACKGROUND, expand=True,
            content=ft.Column([
                ft.Text("Calculadora Marmoraria", size=20, weight="bold"),
                ft.Row([
                    ft.Container(width=350, content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
                    ft.Container(expand=True, content=ft.Column([
                        ft.Container(content=self.canvas, bgcolor=ft.colors.GREY_50, border_radius=10, border=ft.border.all(1, ft.colors.GREY_300), alignment=ft.alignment.center, expand=True),
                        ft.Row([self.lbl_valor, ft.ElevatedButton("Salvar", bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, on_click=self.salvar)], alignment="spaceBetween")
                    ]))
                ], expand=True)
            ])
        )

    def toggle_campos(self, e):
        l = self.txt_larg.value or "0"
        p = self.txt_prof.value or "0"
        def set_st(chk, tc, ta, val):
            tc.disabled = not chk.value
            ta.disabled = not chk.value
            if chk.value and (not tc.value or float(tc.value or 0)==0): tc.value = val
        
        set_st(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a, l)
        set_st(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a, l)
        set_st(self.chk_resq, self.txt_re_c, self.txt_re_a, p)
        set_st(self.chk_rdir, self.txt_rd_c, self.txt_rd_a, p)
        set_st(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a, l)
        set_st(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a, l)
        set_st(self.chk_sesq, self.txt_se_c, self.txt_se_a, p)
        set_st(self.chk_sdir, self.txt_sd_c, self.txt_sd_a, p)
        self.txt_pos_cuba.disabled = not self.chk_cuba.value
        self.txt_pos_cook.disabled = not self.chk_cook.value
        self.calcular(None)

    def calcular(self, e, update_ui=True):
        try:
            if not self.dd_pedra.value: return
            l = float(self.txt_larg.value or 0)
            p = float(self.txt_prof.value or 0)
            if l==0 or p==0: return

            preco_base = self.mapa_precos[self.dd_pedra.value]['preco']
            preco_lin = float(self.txt_acab.value or 0)
            
            area = l * p
            serv = 0

            def add_extra(chk, tc, ta):
                nonlocal area, serv
                if chk.value:
                    c = float(tc.value or 0)
                    a = float(ta.value or 0)
                    area += (c * a)
                    serv += c
            
            for chk, tc, ta in [(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a), (self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a), (self.chk_resq, self.txt_re_c, self.txt_re_a), (self.chk_rdir, self.txt_rd_c, self.txt_rd_a), (self.chk_sfundo, self.txt_sf_c, self.txt_sf_a), (self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a), (self.chk_sesq, self.txt_se_c, self.txt_se_a), (self.chk_sdir, self.txt_sd_c, self.txt_sd_a)]:
                add_extra(chk, tc, ta)

            custo = (area * preco_base) + (serv * preco_lin)
            if self.chk_cuba.value: custo += 150
            if self.chk_cook.value: custo += 100

            self.valor_final = custo
            self.area_final = area
            self.lbl_valor.value = f"R$ {custo:.2f}"
            self.desenhar(l, p, update_ui)
            if update_ui: self.update()
        except: pass

    def desenhar(self, w, h, update_ui=True):
        self.canvas.shapes.clear()
        scale = min(300/w, 250/h) * 0.8
        w_px, h_px = w*scale, h*scale
        sx, sy = (400-w_px)/2, (350-h_px)/2
        
        # Pedra Principal
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style="fill", color="#EEEEEE")))
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))

        # Visualização básica de furos
        if self.chk_cuba.value:
            pos_x = sx + (float(self.txt_pos_cuba.value or 0) * scale)
            self.canvas.shapes.append(cv.Rect(pos_x - 20, sy + h_px/2 - 15, 40, 30, border_radius=5, paint=ft.Paint(style="stroke", color="blue")))
            self.canvas.shapes.append(cv.Text(pos_x - 15, sy + h_px/2 - 5, "EIXO", style=ft.TextStyle(size=8, color="blue")))

        if update_ui: self.canvas.update()

    def salvar(self, e):
        if self.valor_final <= 0: return
        item_dict = {
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos[self.dd_pedra.value]['nome'],
            "largura": self.txt_larg.value,
            "profundidade": self.txt_prof.value,
            "area": self.area_final,
            "preco_total": self.valor_final,
            "config": {"pedra_id": self.dd_pedra.value, "largura": float(self.txt_larg.value), "profundidade": float(self.txt_prof.value)}
        }
        self.on_save_item(item_dict)