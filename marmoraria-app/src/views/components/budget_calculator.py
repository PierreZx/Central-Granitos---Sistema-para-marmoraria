import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND
from src.services import firebase_service

class BudgetCalculator(ft.Container):
    def __init__(self, page, on_save_item, on_cancel, item_para_editar=None):
        super().__init__()
        self.page_ref = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        self.item_para_editar = item_para_editar 
        self.mapa_precos = {}
        
        # Detecção Mobile
        self.eh_mobile = page.width < 768 if hasattr(page, 'width') else False
        
        self.padding = 10 if self.eh_mobile else 20
        self.bgcolor = COLOR_BACKGROUND
        self.expand = True

        # --- 1. CARREGAMENTO DE DADOS ---
        chapas = firebase_service.get_estoque_lista()
        opcoes_pedras = []
        for chapa in chapas:
            # Tratamento seguro de preço
            raw_price = str(chapa.get('valor_m2', 0))
            try: p = float(raw_price.replace(',', '.'))
            except: p = 0.0
            
            txt_op = f"{chapa.get('nome')} - R$ {p:.2f}/m²"
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=txt_op))
            self.mapa_precos[chapa['id']] = {'nome': chapa.get('nome'), 'preco': p}

        # --- 2. INPUTS (LAYOUT SEGURO) ---
        # Filtro para teclado (aceita números e ponto/vírgula)
        filtro_num = ft.InputFilter(allow=True, regex_string=r"[0-9.,]", replacement_string="")

        self.txt_ambiente = ft.TextField(label="Ambiente (Ex: Cozinha)", border_radius=10, filled=True)
        # Dropdown com on_change para recalcular valor da pedra
        self.dd_pedra = ft.Dropdown(label="Selecione a Pedra", options=opcoes_pedras, border_radius=10, filled=True, on_change=self.calcular)
        
        # Inputs de Medidas - EMPILHADOS NO MOBILE (col=12) para não cortar
        self.txt_larg = ft.TextField(label="Largura", suffix_text="m", input_filter=filtro_num, border_radius=10, filled=True, on_change=self.calcular)
        self.txt_prof = ft.TextField(label="Profundidade", suffix_text="m", input_filter=filtro_num, border_radius=10, filled=True, on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Acabamento (R$/m)", value="130.00", input_filter=filtro_num, border_radius=10, filled=True, on_change=self.calcular)

        # Container Responsivo para os inputs
        self.container_medidas = ft.ResponsiveRow([
            ft.Container(self.txt_larg, col={"xs": 12, "md": 4}),
            ft.Container(self.txt_prof, col={"xs": 12, "md": 4}),
            ft.Container(self.txt_acab, col={"xs": 12, "md": 4}),
        ], spacing=10)

        # --- 3. COMPONENTES TÉCNICOS (RODAS/SAIAS/CORTES) ---
        def criar_linha(label, val_padrao):
            chk = ft.Checkbox(label=label, active_color=COLOR_PRIMARY, on_change=self.toggle_campos)
            # Input menor para caber na tela
            txt_c = ft.TextField(label="Comp", value="0.00", width=65, height=35, text_size=12, disabled=True, content_padding=5, filled=True, input_filter=filtro_num, on_change=self.calcular)
            txt_a = ft.TextField(label="Alt", value=val_padrao, width=55, height=35, text_size=12, disabled=True, content_padding=5, filled=True, input_filter=filtro_num, on_change=self.calcular)
            return chk, txt_c, txt_a

        # Rodabancas
        self.chk_rfundo, self.txt_rf_c, self.txt_rf_a = criar_linha("Fundo", "0.10")
        self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a = criar_linha("Frente", "0.10")
        self.chk_resq, self.txt_re_c, self.txt_re_a = criar_linha("Esq.", "0.10")
        self.chk_rdir, self.txt_rd_c, self.txt_rd_a = criar_linha("Dir.", "0.10")

        # Saias
        self.chk_sfundo, self.txt_sf_c, self.txt_sf_a = criar_linha("Fundo", "0.04")
        self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a = criar_linha("Frente", "0.04")
        self.chk_sesq, self.txt_se_c, self.txt_se_a = criar_linha("Esq.", "0.04")
        self.chk_sdir, self.txt_sd_c, self.txt_sd_a = criar_linha("Dir.", "0.04")

        # Cortes (Cuba/Cook)
        self.chk_cuba = ft.Checkbox(label="Cuba", active_color=COLOR_PRIMARY, on_change=self.toggle_campos)
        self.txt_cuba_pos = ft.TextField(label="Pos", width=60, height=35, content_padding=5, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cuba_larg = ft.TextField(label="Lar", width=60, height=35, content_padding=5, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cuba_prof = ft.TextField(label="Pro", width=60, height=35, content_padding=5, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)

        self.chk_cook = ft.Checkbox(label="Cook", active_color=COLOR_PRIMARY, on_change=self.toggle_campos)
        self.txt_cook_pos = ft.TextField(label="Pos", width=60, height=35, content_padding=5, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cook_larg = ft.TextField(label="Lar", width=60, height=35, content_padding=5, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cook_prof = ft.TextField(label="Pro", width=60, height=35, content_padding=5, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)

        self.txt_instrucoes = ft.TextField(label="Obs. Produção", multiline=True, filled=True)

        # --- 4. CANVAS E VISUALIZAÇÃO ---
        # Canvas com tamanho fixo seguro
        self.canvas = cv.Canvas(
            width=320 if self.eh_mobile else 500, 
            height=300, 
            shapes=[]
        )
        
        self.lbl_valor = ft.Text("R$ 0.00", size=30, weight="bold", color=COLOR_PRIMARY)
        self.lbl_detalhes_pedra = ft.Text("Pedra: 0.00m²", size=12, color="grey")
        self.lbl_detalhes_servico = ft.Text("Serviço: 0.00m", size=12, color="grey")
        
        self.valor_final = 0.0
        self.area_final = 0.0

        # --- 5. LÓGICA DE CARREGAMENTO (EDIÇÃO) ---
        if self.item_para_editar:
            cfg = self.item_para_editar.get('config', {})
            self.txt_ambiente.value = self.item_para_editar.get('ambiente', '')
            self.dd_pedra.value = cfg.get('pedra_id', '')
            self.txt_larg.value = str(cfg.get('largura', 0))
            self.txt_prof.value = str(cfg.get('profundidade', 0))
            self.txt_acab.value = str(cfg.get('preco_acab', 130))
            self.txt_instrucoes.value = cfg.get('instrucoes_producao', '')
            
            def load_chk(chk, txt_c, txt_a, k):
                v = cfg.get(k, {})
                chk.value = v.get('chk', False)
                txt_c.value = str(v.get('c', '0.00'))
                txt_a.value = str(v.get('a', '0.00'))
            
            load_chk(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a, 'rfundo')
            load_chk(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a, 'rfrente')
            load_chk(self.chk_resq, self.txt_re_c, self.txt_re_a, 'resq')
            load_chk(self.chk_rdir, self.txt_rd_c, self.txt_rd_a, 'rdir')
            load_chk(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a, 'sfundo')
            load_chk(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a, 'sfrente')
            load_chk(self.chk_sesq, self.txt_se_c, self.txt_se_a, 'sesq')
            load_chk(self.chk_sdir, self.txt_sd_c, self.txt_sd_a, 'sdir')

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
            
            self.toggle_campos(None, update_ui=False)

        # --- 6. MONTAGEM DA TELA (LAYOUT) ---
        def row_full(chk, txt_c, txt_a): return ft.Row([chk, txt_c, txt_a], spacing=5)
        
        tabs = ft.Tabs(selected_index=0, label_color=COLOR_PRIMARY, indicator_color=COLOR_PRIMARY, tabs=[
            ft.Tab(text="1. Base", content=ft.Container(padding=15, content=ft.Column([
                self.txt_ambiente, self.dd_pedra, self.container_medidas
            ], scroll=ft.ScrollMode.AUTO))),
            
            ft.Tab(text="2. Rodas", content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Rodabancas:", size=12, color="grey"),
                row_full(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a), row_full(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a),
                row_full(self.chk_resq, self.txt_re_c, self.txt_re_a), row_full(self.chk_rdir, self.txt_rd_c, self.txt_rd_a)
            ], scroll=ft.ScrollMode.AUTO))),
            
            ft.Tab(text="3. Saias", content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Saias:", size=12, color="grey"),
                row_full(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a), row_full(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a),
                row_full(self.chk_sesq, self.txt_se_c, self.txt_se_a), row_full(self.chk_sdir, self.txt_sd_c, self.txt_sd_a)
            ], scroll=ft.ScrollMode.AUTO))),
            
            ft.Tab(text="4. Cortes", content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Cubas e Cooktops:", size=12, color="grey"),
                ft.Row([self.chk_cuba, self.txt_cuba_pos]), ft.Row([self.txt_cuba_larg, self.txt_cuba_prof]),
                ft.Divider(),
                ft.Row([self.chk_cook, self.txt_cook_pos]), ft.Row([self.txt_cook_larg, self.txt_cook_prof])
            ], scroll=ft.ScrollMode.AUTO))),
            
            ft.Tab(text="5. Obs", content=ft.Container(padding=15, content=self.txt_instrucoes))
        ])

        self.content = ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()), ft.Text("Calculadora", size=20, weight="bold", color=COLOR_PRIMARY)]),
            ft.Divider(),
            ft.Container(height=350, content=tabs),
            ft.Divider(),
            ft.Text("Visualização & Preço", weight="bold"),
            # Container do Canvas
            ft.Container(
                content=self.canvas, 
                bgcolor=ft.colors.GREY_50, 
                border_radius=10, 
                padding=10,
                alignment=ft.alignment.center,
                height=320 
            ),
            ft.Container(height=10),
            ft.Column([
                self.lbl_valor,
                self.lbl_detalhes_pedra,
                self.lbl_detalhes_servico
            ], spacing=2),
            ft.Divider(),
            ft.ElevatedButton("Salvar Peça", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, height=50, width=float("inf"), on_click=self.salvar)
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        if self.item_para_editar: self.calcular(None, update_ui=False)

    # --- 7. LÓGICA MATEMÁTICA E VISUAL ---
    def _to_float(self, val):
        if not val: return 0.0
        try: return float(str(val).replace(',', '.'))
        except: return 0.0

    def toggle_campos(self, e, update_ui=True):
        l_peca = self.txt_larg.value
        p_peca = self.txt_prof.value

        def update_linha(chk, txt_c, txt_a, val_padrao_c):
            if update_ui:
                txt_c.disabled = not chk.value
                txt_a.disabled = not chk.value
                if chk.value and self._to_float(txt_c.value) == 0: txt_c.value = val_padrao_c
                txt_c.update(); txt_a.update()

        # Atualiza todos os campos dependentes
        for chk, txt_c, txt_a, val in [
            (self.chk_rfundo, self.txt_rf_c, self.txt_rf_a, l_peca), (self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a, l_peca),
            (self.chk_resq, self.txt_re_c, self.txt_re_a, p_peca), (self.chk_rdir, self.txt_rd_c, self.txt_rd_a, p_peca),
            (self.chk_sfundo, self.txt_sf_c, self.txt_sf_a, l_peca), (self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a, l_peca),
            (self.chk_sesq, self.txt_se_c, self.txt_se_a, p_peca), (self.chk_sdir, self.txt_sd_c, self.txt_sd_a, p_peca)
        ]:
            update_linha(chk, txt_c, txt_a, val)

        for chk, inps in [(self.chk_cuba, [self.txt_cuba_pos, self.txt_cuba_larg, self.txt_cuba_prof]), 
                          (self.chk_cook, [self.txt_cook_pos, self.txt_cook_larg, self.txt_cook_prof])]:
            if update_ui:
                for i in inps: i.disabled = not chk.value; i.update()

        self.calcular(None, update_ui=update_ui)

    def calcular(self, e, update_ui=True):
        # 1. Pega valores base
        l = self._to_float(self.txt_larg.value)
        p = self._to_float(self.txt_prof.value)
        
        # 2. Pega preço da pedra selecionada
        preco_m2_pedra = 0.0
        nome_pedra = "Nenhuma"
        if self.dd_pedra.value:
            d = self.mapa_precos.get(self.dd_pedra.value, {})
            preco_m2_pedra = d.get('preco', 0.0)
            nome_pedra = d.get('nome', '')

        preco_lin_servico = self._to_float(self.txt_acab.value)
        
        # 3. Calcula extras
        area_extra, metros_lineares = 0.0, 0.0
        
        def somar(chk, txt_c, txt_a):
            nonlocal area_extra, metros_lineares
            if chk.value:
                c = self._to_float(txt_c.value); a = self._to_float(txt_a.value)
                area_extra += (c * a); metros_lineares += c
        
        # Soma tudo
        somar(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a); somar(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a)
        somar(self.chk_resq, self.txt_re_c, self.txt_re_a); somar(self.chk_rdir, self.txt_rd_c, self.txt_rd_a)
        somar(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a); somar(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a)
        somar(self.chk_sesq, self.txt_se_c, self.txt_se_a); somar(self.chk_sdir, self.txt_sd_c, self.txt_sd_a)

        # 4. Totalização
        area_total = (l * p) + area_extra
        custo_pedra = area_total * preco_m2_pedra
        custo_servico = metros_lineares * preco_lin_servico
        
        taxa_corte = 0
        if self.chk_cuba.value: taxa_corte += 80
        if self.chk_cook.value: taxa_corte += 80

        custo_total = custo_pedra + custo_servico + taxa_corte

        # 5. Atualiza UI
        self.valor_final = custo_total
        self.area_final = area_total
        
        if update_ui:
            self.lbl_valor.value = f"R$ {custo_total:.2f}"
            self.lbl_detalhes_pedra.value = f"PEDRA ({nome_pedra}): {area_total:.2f}m² x R$ {preco_m2_pedra:.2f} = R$ {custo_pedra:.2f}"
            self.lbl_detalhes_servico.value = f"SERVIÇO: {metros_lineares:.2f}m x R$ {preco_lin_servico:.2f} + Cortes = R$ {custo_servico+taxa_corte:.2f}"
            self.lbl_valor.update()
            self.lbl_detalhes_pedra.update()
            self.lbl_detalhes_servico.update()
        
        self.desenhar(l, p, update_ui)

    def desenhar(self, w, h, update_ui=True):
        self.canvas.shapes.clear()
        
        W_C = 320 if self.eh_mobile else 450
        H_C = 280 if self.eh_mobile else 350
        MARGEM = 40
        
        if w == 0 or h == 0: scale = 1
        else: scale = min((W_C - (MARGEM*2)) / w, (H_C - (MARGEM*2)) / h) * 0.8
        
        w_px, h_px = w * scale, h * scale
        sx, sy = (W_C - w_px) / 2, (H_C - h_px) / 2
        
        C_PEDRA, C_LINHA, C_COTA, C_RODA, C_SAIA = ft.colors.BLUE_GREY_50, ft.colors.BLACK, ft.colors.RED_700, ft.colors.BROWN_400, ft.colors.ORANGE_400
        
        # Base
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_PEDRA)))
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))

        # Cotas
        self.canvas.shapes.append(cv.Line(sx, sy-MARGEM, sx+w_px, sy-MARGEM, paint=ft.Paint(color=C_COTA)))
        self.canvas.shapes.append(cv.Text(sx + w_px/2 - 10, sy - MARGEM - 15, f"{w:.2f}m", style=ft.TextStyle(size=10, color=C_COTA)))
        self.canvas.shapes.append(cv.Line(sx-MARGEM, sy, sx-MARGEM, sy+h_px, paint=ft.Paint(color=C_COTA)))
        self.canvas.shapes.append(cv.Text(sx - MARGEM - 35, sy + h_px/2, f"{h:.2f}m", style=ft.TextStyle(size=10, color=C_COTA)))

        # Extras (Rodas/Saias)
        def draw_extra(chk, txt_c, txt_a, pos, cor, label):
            if chk.value:
                comp = self._to_float(txt_c.value) * scale
                alt = self._to_float(txt_a.value)
                esp = 10
                
                # Coordenadas
                off_x, off_y = (w_px - comp) / 2, (h_px - comp) / 2
                rx, ry, rw, rh = 0,0,0,0
                tx, ty = 0,0
                
                if pos == 'top': 
                    rx, ry, rw, rh = sx + off_x, sy - esp, comp, esp
                    tx, ty = sx + w_px/2, sy - esp - 10
                elif pos == 'bottom': 
                    rx, ry, rw, rh = sx + off_x, sy + h_px, comp, esp
                    tx, ty = sx + w_px/2, sy + h_px + 5
                elif pos == 'left': 
                    rx, ry, rw, rh = sx - esp, sy + off_y, esp, comp
                    tx, ty = sx - esp - 30, sy + h_px/2
                elif pos == 'right': 
                    rx, ry, rw, rh = sx + w_px, sy + off_y, esp, comp
                    tx, ty = sx + w_px + 5, sy + h_px/2

                self.canvas.shapes.append(cv.Rect(rx, ry, rw, rh, paint=ft.Paint(color=cor)))
                self.canvas.shapes.append(cv.Text(tx, ty, f"{label}: {alt:.2f}", style=ft.TextStyle(size=9, color="black")))

        # Desenha tudo
        draw_extra(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a, 'top', C_RODA, "Roda")
        draw_extra(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a, 'bottom', C_RODA, "Roda")
        draw_extra(self.chk_resq, self.txt_re_c, self.txt_re_a, 'left', C_RODA, "Roda")
        draw_extra(self.chk_rdir, self.txt_rd_c, self.txt_rd_a, 'right', C_RODA, "Roda")
        
        draw_extra(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a, 'top', C_SAIA, "Saia")
        draw_extra(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a, 'bottom', C_SAIA, "Saia")
        draw_extra(self.chk_sesq, self.txt_se_c, self.txt_se_a, 'left', C_SAIA, "Saia")
        draw_extra(self.chk_sdir, self.txt_sd_c, self.txt_sd_a, 'right', C_SAIA, "Saia")

        # Cortes
        def draw_hole(chk, t_pos, t_l, t_p, cor, lbl):
            if chk.value:
                cx = sx + (self._to_float(t_pos.value) * scale)
                cw = self._to_float(t_l.value) * scale
                ch = self._to_float(t_p.value) * scale
                cy = sy + (h_px - ch) / 2
                self.canvas.shapes.append(cv.Rect(cx, cy, cw, ch, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=cor, stroke_width=2)))
                self.canvas.shapes.append(cv.Text(cx+5, cy+5, lbl, style=ft.TextStyle(size=9, color=cor, weight="bold")))

        draw_hole(self.chk_cuba, self.txt_cuba_pos, self.txt_cuba_larg, self.txt_cuba_prof, "blue", "CUBA")
        draw_hole(self.chk_cook, self.txt_cook_pos, self.txt_cook_larg, self.txt_cook_prof, "black", "COOK")

        if update_ui: self.canvas.update()

    def salvar(self, e):
        if not self.txt_ambiente.value or self.valor_final == 0: return
        
        def get_vals(chk, txt_c, txt_a): 
            return {'chk': chk.value, 'c': self._to_float(txt_c.value), 'a': self._to_float(txt_a.value)}
        
        config = {
            'pedra_id': self.dd_pedra.value,
            'largura': self._to_float(self.txt_larg.value),
            'profundidade': self._to_float(self.txt_prof.value),
            'preco_acab': self._to_float(self.txt_acab.value),
            'instrucoes_producao': self.txt_instrucoes.value,
            'rfundo': get_vals(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a),
            'rfrente': get_vals(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a),
            'resq': get_vals(self.chk_resq, self.txt_re_c, self.txt_re_a),
            'rdir': get_vals(self.chk_rdir, self.txt_rd_c, self.txt_rd_a),
            'sfundo': get_vals(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a),
            'sfrente': get_vals(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a),
            'sesq': get_vals(self.chk_sesq, self.txt_se_c, self.txt_se_a),
            'sdir': get_vals(self.chk_sdir, self.txt_sd_c, self.txt_sd_a),
            'cuba': {'chk': self.chk_cuba.value, 'pos': self._to_float(self.txt_cuba_pos.value), 'larg': self._to_float(self.txt_cuba_larg.value), 'prof': self._to_float(self.txt_cuba_prof.value)},
            'cook': {'chk': self.chk_cook.value, 'pos': self._to_float(self.txt_cook_pos.value), 'larg': self._to_float(self.txt_cook_larg.value), 'prof': self._to_float(self.txt_cook_prof.value)}
        }

        item_dict = {
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos.get(self.dd_pedra.value, {}).get('nome', 'Pedra'),
            "largura": self.txt_larg.value,
            "profundidade": self.txt_prof.value,
            "area": self.area_final,
            "preco_total": self.valor_final,
            "config": config
        }
        self.on_save_item(item_dict)