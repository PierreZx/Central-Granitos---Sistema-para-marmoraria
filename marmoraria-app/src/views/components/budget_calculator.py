import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND
from src.services import firebase_service

class BudgetCalculator(ft.UserControl):
    def __init__(self, on_save_item, on_cancel, item_para_editar=None):
        super().__init__()
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        self.item_para_editar = item_para_editar 
        self.mapa_precos = {}

    def build(self):
        # --- DADOS ---
        chapas = firebase_service.get_estoque_lista()
        opcoes_pedras = []
        for chapa in chapas:
            qtd = int(chapa.get('quantidade', 0) or 0)
            if qtd > 0:
                nome = chapa.get('nome', 'Sem Nome')
                preco = float(chapa.get('valor_m2', 0) or 0)
                txt_op = f"{nome} - R$ {preco:.2f}/m²"
                opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=txt_op))
                self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- INPUTS GERAIS ---
        self.txt_ambiente = ft.TextField(label="Ambiente (Ex: Cozinha)", border_radius=8, expand=True, height=45, text_size=14)
        self.dd_pedra = ft.Dropdown(label="Pedra", options=opcoes_pedras, border_radius=8, expand=True, height=45, text_size=14)
        
        # Medidas Principais
        self.txt_larg = ft.TextField(label="Largura Total (m)", suffix_text="m", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        self.txt_prof = ft.TextField(label="Profundidade (m)", suffix_text="m", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        
        # Acabamentos
        self.txt_acab = ft.TextField(label="R$/m Linear", value="50.00", width=120, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        self.dd_borda = ft.Dropdown(
            label="Tipo de Borda",
            options=[
                ft.dropdown.Option("Reto"),
                ft.dropdown.Option("Meia-Esquadria (45º)"),
                ft.dropdown.Option("Boleado"),
                ft.dropdown.Option("Bisotê")
            ],
            value="Meia-Esquadria (45º)",
            expand=True, height=45, text_size=14
        )

        # Helper UI
        def criar_linha_config(label_chk, valor_padrao_alt):
            chk = ft.Checkbox(label=label_chk, value=False)
            txt_comp = ft.TextField(label="Comp (m)", width=80, height=40, text_size=12, disabled=True, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.colors.GREY_50)
            txt_alt = ft.TextField(label="Alt (m)", value=valor_padrao_alt, width=70, height=40, text_size=12, disabled=True, keyboard_type=ft.KeyboardType.NUMBER)
            return chk, txt_comp, txt_alt

        # Rodabancas & Saias
        self.chk_rfundo, self.txt_rf_c, self.txt_rf_a = criar_linha_config("Fundo", "0.10")
        self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a = criar_linha_config("Frente", "0.10")
        self.chk_resq, self.txt_re_c, self.txt_re_a = criar_linha_config("Esq", "0.10")
        self.chk_rdir, self.txt_rd_c, self.txt_rd_a = criar_linha_config("Dir", "0.10")

        self.chk_sfundo, self.txt_sf_c, self.txt_sf_a = criar_linha_config("Fundo", "0.04")
        self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a = criar_linha_config("Frente", "0.04")
        self.chk_sesq, self.txt_se_c, self.txt_se_a = criar_linha_config("Esq", "0.04")
        self.chk_sdir, self.txt_sd_c, self.txt_sd_a = criar_linha_config("Dir", "0.04")

        # --- RECORTES TÉCNICOS (Medidas Exatas) ---
        self.chk_cuba = ft.Checkbox(label="Cuba/Pia", value=False)
        self.txt_cuba_pos = ft.TextField(label="Dist. Esq (m)", value="0.50", width=90, height=40, text_size=12, disabled=True)
        self.txt_cuba_larg = ft.TextField(label="Largura (m)", value="0.50", width=90, height=40, text_size=12, disabled=True)
        self.txt_cuba_prof = ft.TextField(label="Profund. (m)", value="0.40", width=90, height=40, text_size=12, disabled=True)

        self.chk_cook = ft.Checkbox(label="Cooktop", value=False)
        self.txt_cook_pos = ft.TextField(label="Dist. Esq (m)", value="1.50", width=90, height=40, text_size=12, disabled=True)
        self.txt_cook_larg = ft.TextField(label="Largura (m)", value="0.60", width=90, height=40, text_size=12, disabled=True)
        self.txt_cook_prof = ft.TextField(label="Profund. (m)", value="0.45", width=90, height=40, text_size=12, disabled=True)

        # Observações Técnicas
        self.txt_obs = ft.TextField(label="Observações de Produção / Tolerâncias", multiline=True, min_lines=2, max_lines=4, expand=True, text_size=12)

        # Visualização
        self.canvas = cv.Canvas(width=400, height=350, shapes=[])
        self.lbl_valor = ft.Text("R$ 0.00", size=28, weight="bold", color=COLOR_PRIMARY)
        self.valor_final = 0.0
        self.area_final = 0.0

        # --- CARREGAR EDIÇÃO ---
        if self.item_para_editar:
            cfg = self.item_para_editar.get('config', {})
            self.txt_ambiente.value = self.item_para_editar.get('ambiente', '')
            self.dd_pedra.value = cfg.get('pedra_id', '')
            self.txt_larg.value = str(cfg.get('largura', 0))
            self.txt_prof.value = str(cfg.get('profundidade', 0))
            self.txt_acab.value = str(cfg.get('preco_acab', 50))
            self.dd_borda.value = cfg.get('tipo_borda', 'Reto')
            self.txt_obs.value = cfg.get('obs', '')

            def load_f(chk, tc, ta, k):
                vals = cfg.get(k, {})
                chk.value = vals.get('chk', False)
                tc.value = str(vals.get('c', ''))
                ta.value = str(vals.get('a', ''))
                tc.disabled = not chk.value
                ta.disabled = not chk.value

            for k, (chk, tc, ta) in {
                'rfundo': (self.chk_rfundo, self.txt_rf_c, self.txt_rf_a),
                'rfrente': (self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a),
                'resq': (self.chk_resq, self.txt_re_c, self.txt_re_a),
                'rdir': (self.chk_rdir, self.txt_rd_c, self.txt_rd_a),
                'sfundo': (self.chk_sfundo, self.txt_sf_c, self.txt_sf_a),
                'sfrente': (self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a),
                'sesq': (self.chk_sesq, self.txt_se_c, self.txt_se_a),
                'sdir': (self.chk_sdir, self.txt_sd_c, self.txt_sd_a)
            }.items():
                load_f(chk, tc, ta, k)

            c_cuba = cfg.get('cuba', {})
            self.chk_cuba.value = c_cuba.get('chk', False)
            self.txt_cuba_pos.value = str(c_cuba.get('pos', 0.5))
            self.txt_cuba_larg.value = str(c_cuba.get('larg', 0.5))
            self.txt_cuba_prof.value = str(c_cuba.get('prof', 0.4))
            
            c_cook = cfg.get('cook', {})
            self.chk_cook.value = c_cook.get('chk', False)
            self.txt_cook_pos.value = str(c_cook.get('pos', 1.5))
            self.txt_cook_larg.value = str(c_cook.get('larg', 0.6))
            self.txt_cook_prof.value = str(c_cook.get('prof', 0.45))
            
            # Atualiza estado dos campos
            for c in [self.txt_cuba_pos, self.txt_cuba_larg, self.txt_cuba_prof]: c.disabled = not self.chk_cuba.value
            for c in [self.txt_cook_pos, self.txt_cook_larg, self.txt_cook_prof]: c.disabled = not self.chk_cook.value

        # --- LAYOUT EM ABAS ---
        def row_compacta(chk, txt_c, txt_a):
            return ft.Row([chk, txt_c, txt_a], spacing=10)

        tabs = ft.Tabs(selected_index=0, animation_duration=300, tabs=[
            ft.Tab(text="1. Base", content=ft.Container(padding=15, content=ft.Column([
                self.txt_ambiente, self.dd_pedra, 
                ft.Row([self.txt_larg, self.txt_prof]), 
                ft.Row([self.dd_borda, self.txt_acab]),
                self.txt_obs
            ], spacing=15))),
            ft.Tab(text="2. Rodabancas", content=ft.Container(padding=15, content=ft.Column([
                row_compacta(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a),
                row_compacta(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a),
                row_compacta(self.chk_resq, self.txt_re_c, self.txt_re_a),
                row_compacta(self.chk_rdir, self.txt_rd_c, self.txt_rd_a)
            ], spacing=10))),
            ft.Tab(text="3. Saias", content=ft.Container(padding=15, content=ft.Column([
                row_compacta(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a),
                row_compacta(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a),
                row_compacta(self.chk_sesq, self.txt_se_c, self.txt_se_a),
                row_compacta(self.chk_sdir, self.txt_sd_c, self.txt_sd_a)
            ], spacing=10))),
            ft.Tab(text="4. Recortes", content=ft.Container(padding=15, content=ft.Column([
                ft.Row([self.chk_cuba, self.txt_cuba_pos], alignment="spaceBetween"),
                ft.Row([self.txt_cuba_larg, self.txt_cuba_prof]),
                ft.Divider(),
                ft.Row([self.chk_cook, self.txt_cook_pos], alignment="spaceBetween"),
                ft.Row([self.txt_cook_larg, self.txt_cook_prof]),
            ], spacing=10)))
        ], expand=True)

        # --- EVENTOS ---
        inputs_calc = [
            self.txt_larg, self.txt_prof, self.txt_acab, self.dd_pedra, 
            self.txt_rf_a, self.txt_rf_c, self.txt_rfr_a, self.txt_rfr_c, self.txt_re_a, self.txt_re_c, self.txt_rd_a, self.txt_rd_c,
            self.txt_sf_a, self.txt_sf_c, self.txt_sfr_a, self.txt_sfr_c, self.txt_se_a, self.txt_se_c, self.txt_sd_a, self.txt_sd_c,
            self.txt_cuba_pos, self.txt_cuba_larg, self.txt_cuba_prof,
            self.txt_cook_pos, self.txt_cook_larg, self.txt_cook_prof
        ]
        for i in inputs_calc: i.on_change = self.calcular

        inputs_toggle = [
            self.chk_rfundo, self.chk_rfrente, self.chk_resq, self.chk_rdir, 
            self.chk_sfundo, self.chk_sfrente, self.chk_sesq, self.chk_sdir, 
            self.chk_cuba, self.chk_cook
        ]
        for i in inputs_toggle: i.on_change = self.toggle_campos

        if self.item_para_editar: self.calcular(None, update_ui=False)

        return ft.Container(
            padding=20, bgcolor=COLOR_BACKGROUND, expand=True,
            content=ft.Column([
                ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()),
                    ft.Text("Ficha Técnica da Peça", size=20, weight="bold")
                ]),
                ft.Divider(),
                ft.Row([
                    ft.Container(width=420, bgcolor=COLOR_WHITE, border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="#00000010"), content=tabs),
                    ft.Container(expand=True, padding=ft.padding.only(left=20), content=ft.Column([
                        ft.Text("Visualização Técnica", weight="bold"),
                        ft.Container(content=self.canvas, bgcolor=ft.colors.GREY_50, border_radius=10, border=ft.border.all(1, ft.colors.GREY_300), alignment=ft.alignment.center, expand=True),
                        ft.Divider(),
                        ft.Row([
                            ft.Column([ft.Text("Custo Estimado:", size=14), self.lbl_valor]),
                            ft.ElevatedButton("Salvar Peça", icon=ft.icons.CHECK, bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, height=50, on_click=self.salvar)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]))
                ], expand=True)
            ])
        )

    def toggle_campos(self, e):
        l = self.txt_larg.value or "0"
        p = self.txt_prof.value or "0"
        
        def set_st(chk, txt_c, txt_a, val_padrao):
            txt_c.disabled = not chk.value
            txt_a.disabled = not chk.value
            if chk.value:
                if not txt_c.value or float(txt_c.value or 0) == 0: txt_c.value = val_padrao
                txt_c.bgcolor = ft.colors.WHITE
                txt_a.bgcolor = ft.colors.WHITE
            else:
                txt_c.bgcolor = ft.colors.GREY_50
                txt_a.bgcolor = ft.colors.GREY_50
        
        # Ativa/Desativa Campos
        set_st(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a, l)
        set_st(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a, l)
        set_st(self.chk_resq, self.txt_re_c, self.txt_re_a, p)
        set_st(self.chk_rdir, self.txt_rd_c, self.txt_rd_a, p)
        
        set_st(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a, l)
        set_st(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a, l)
        set_st(self.chk_sesq, self.txt_se_c, self.txt_se_a, p)
        set_st(self.chk_sdir, self.txt_sd_c, self.txt_sd_a, p)

        # Recortes
        for c in [self.txt_cuba_pos, self.txt_cuba_larg, self.txt_cuba_prof]:
            c.disabled = not self.chk_cuba.value
            c.bgcolor = ft.colors.WHITE if self.chk_cuba.value else ft.colors.GREY_50
            
        for c in [self.txt_cook_pos, self.txt_cook_larg, self.txt_cook_prof]:
            c.disabled = not self.chk_cook.value
            c.bgcolor = ft.colors.WHITE if self.chk_cook.value else ft.colors.GREY_50
        
        self.calcular(None)

    def calcular(self, e, update_ui=True):
        try:
            if not self.dd_pedra.value: return
            l = float(self.txt_larg.value or 0)
            p = float(self.txt_prof.value or 0)
            if l==0 or p==0: return

            preco_base = self.mapa_precos.get(self.dd_pedra.value, {}).get('preco', 0)
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
            
            add_extra(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a)
            add_extra(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a)
            add_extra(self.chk_resq, self.txt_re_c, self.txt_re_a)
            add_extra(self.chk_rdir, self.txt_rd_c, self.txt_rd_a)
            
            add_extra(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a)
            add_extra(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a)
            add_extra(self.chk_sesq, self.txt_se_c, self.txt_se_a)
            add_extra(self.chk_sdir, self.txt_sd_c, self.txt_sd_a)

            custo = (area * preco_base) + (serv * preco_lin)
            if self.chk_cuba.value: custo += 150
            if self.chk_cook.value: custo += 100

            self.valor_final = custo
            self.area_final = area
            self.lbl_valor.value = f"R$ {custo:.2f}"
            
            self.desenhar(l, p, update_ui)
            if update_ui: self.update()
        except ValueError: pass

    def desenhar(self, w, h, update_ui=True):
        self.canvas.shapes.clear()
        
        W_C, H_C = 400, 350
        scale = min((W_C-100)/w, (H_C-100)/h) * 0.8
        w_px, h_px = w*scale, h*scale
        sx, sy = (W_C-w_px)/2, (H_C-h_px)/2
        
        C_PEDRA, C_RODA, C_SAIA, C_LINHA = ft.colors.BLUE_GREY_100, ft.colors.BLUE_GREY_300, ft.colors.BLUE_GREY_500, ft.colors.BLACK
        TXT_STYLE = ft.TextStyle(size=12, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)
        TXT_STYLE_SM = ft.TextStyle(size=10, color=ft.colors.GREY_800)

        # Rodabancas
        def draw_roda(chk, th, pos):
            if chk.value:
                hr = float(th.value or 0.1) * scale
                if pos=='t': 
                    self.canvas.shapes.append(cv.Rect(sx, sy-hr, w_px, hr, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_RODA)))
                    self.canvas.shapes.append(cv.Rect(sx, sy-hr, w_px, hr, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))
                elif pos=='b': 
                    self.canvas.shapes.append(cv.Rect(sx, sy+h_px, w_px, hr, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_RODA)))
                    self.canvas.shapes.append(cv.Rect(sx, sy+h_px, w_px, hr, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))
                elif pos=='l': 
                    self.canvas.shapes.append(cv.Rect(sx-hr, sy, hr, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_RODA)))
                    self.canvas.shapes.append(cv.Rect(sx-hr, sy, hr, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))
                elif pos=='r': 
                    self.canvas.shapes.append(cv.Rect(sx+w_px, sy, hr, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_RODA)))
                    self.canvas.shapes.append(cv.Rect(sx+w_px, sy, hr, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))

        draw_roda(self.chk_rfundo, self.txt_rf_a, 't')
        draw_roda(self.chk_rfrente, self.txt_rfr_a, 'b')
        draw_roda(self.chk_resq, self.txt_re_a, 'l')
        draw_roda(self.chk_rdir, self.txt_rd_a, 'r')

        # Pedra
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_PEDRA)))
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=2, color=C_LINHA)))

        # Saias
        esp = 10
        def draw_saia(chk, th, pos):
            if chk.value:
                if pos=='t': self.canvas.shapes.append(cv.Rect(sx, sy, w_px, esp, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_SAIA)))
                elif pos=='b': self.canvas.shapes.append(cv.Rect(sx, sy+h_px-esp, w_px, esp, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_SAIA)))
                elif pos=='l': self.canvas.shapes.append(cv.Rect(sx, sy, esp, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_SAIA)))
                elif pos=='r': self.canvas.shapes.append(cv.Rect(sx+w_px-esp, sy, esp, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_SAIA)))

        draw_saia(self.chk_sfundo, self.txt_sf_a, 't')
        draw_saia(self.chk_sfrente, self.txt_sfr_a, 'b')
        draw_saia(self.chk_sesq, self.txt_se_a, 'l')
        draw_saia(self.chk_sdir, self.txt_sd_a, 'r')

        # Recortes (Agora com Tamanho Real)
        if self.chk_cuba.value:
            try:
                dist = float(self.txt_cuba_pos.value or 0) * scale
                cw = float(self.txt_cuba_larg.value or 0.5) * scale
                ch = float(self.txt_cuba_prof.value or 0.4) * scale
                
                c_x = sx + dist
                # Centraliza Y se não tiver posição Y definida (padrão)
                c_y = sy + (h_px - ch)/2
                
                self.canvas.shapes.append(cv.Rect(c_x, c_y, cw, ch, border_radius=5, paint=ft.Paint(style=ft.PaintingStyle.STROKE)))
                self.canvas.shapes.append(cv.Circle(c_x+cw/2, c_y+5, 3, paint=ft.Paint(style=ft.PaintingStyle.STROKE)))
                self.canvas.shapes.append(cv.Text(c_x, c_y + ch/2, "Cuba", style=TXT_STYLE_SM))
            except: pass

        if self.chk_cook.value:
            try:
                dist = float(self.txt_cook_pos.value or 0) * scale
                cw = float(self.txt_cook_larg.value or 0.6) * scale
                ch = float(self.txt_cook_prof.value or 0.45) * scale
                
                c_x = sx + dist
                c_y = sy + (h_px - ch)/2
                
                self.canvas.shapes.append(cv.Rect(c_x, c_y, cw, ch, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.colors.BLACK)))
                self.canvas.shapes.append(cv.Circle(c_x+cw*0.25, c_y+ch*0.25, 5, paint=ft.Paint(style=ft.PaintingStyle.STROKE)))
                self.canvas.shapes.append(cv.Circle(c_x+cw*0.75, c_y+ch*0.75, 5, paint=ft.Paint(style=ft.PaintingStyle.STROKE)))
                self.canvas.shapes.append(cv.Text(c_x, c_y + ch + 5, "Cook", style=TXT_STYLE_SM))
            except: pass

        # Cotas
        self.canvas.shapes.append(cv.Text(sx+w_px/2-15, sy+h_px+20, f"{w:.2f}m", style=TXT_STYLE))
        self.canvas.shapes.append(cv.Text(sx-40, sy+h_px/2, f"{h:.2f}m", style=TXT_STYLE))
        
        if update_ui: self.canvas.update()

    def salvar(self, e):
        if not self.txt_ambiente.value or self.valor_final == 0:
            return 
        
        def get_vals(chk, tc, ta): return {'chk': chk.value, 'c': float(tc.value or 0), 'a': float(ta.value or 0)}
        
        # Salva TUDO, inclusive as novas medidas de recorte e obs
        config = {
            'pedra_id': self.dd_pedra.value,
            'largura': float(self.txt_larg.value or 0),
            'profundidade': float(self.txt_prof.value or 0),
            'preco_acab': float(self.txt_acab.value or 0),
            'tipo_borda': self.dd_borda.value,
            'obs': self.txt_obs.value,
            
            'rfundo': get_vals(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a),
            'rfrente': get_vals(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a),
            'resq': get_vals(self.chk_resq, self.txt_re_c, self.txt_re_a),
            'rdir': get_vals(self.chk_rdir, self.txt_rd_c, self.txt_rd_a),
            'sfundo': get_vals(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a),
            'sfrente': get_vals(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a),
            'sesq': get_vals(self.chk_sesq, self.txt_se_c, self.txt_se_a),
            'sdir': get_vals(self.chk_sdir, self.txt_sd_c, self.txt_sd_a),
            
            'cuba': {
                'chk': self.chk_cuba.value, 
                'pos': float(self.txt_cuba_pos.value or 0),
                'larg': float(self.txt_cuba_larg.value or 0.5),
                'prof': float(self.txt_cuba_prof.value or 0.4)
            },
            'cook': {
                'chk': self.chk_cook.value, 
                'pos': float(self.txt_cook_pos.value or 0),
                'larg': float(self.txt_cook_larg.value or 0.6),
                'prof': float(self.txt_cook_prof.value or 0.45)
            }
        }

        item_dict = {
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos.get(self.dd_pedra.value, {}).get('nome', ''),
            "largura": self.txt_larg.value,
            "profundidade": self.txt_prof.value,
            "area": self.area_final,
            "preco_total": self.valor_final,
            "config": config
        }
        self.on_save_item(item_dict)