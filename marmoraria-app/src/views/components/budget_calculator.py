import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND, BORDER_RADIUS_MD
from src.services import firebase_service

class BudgetCalculator(ft.Container):
    def __init__(self, page, on_save_item, on_cancel, item_para_editar=None):
        super().__init__()
        self.page_ref = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        self.item_para_editar = item_para_editar 
        self.mapa_precos = {}
        
        self.eh_mobile = page.width < 768 if hasattr(page, 'width') else False
        self.padding = 15 if self.eh_mobile else 25
        self.bgcolor = COLOR_BACKGROUND
        self.expand = True

        # --- 1. CARREGAMENTO DE DADOS (Inalterado) ---
        chapas = firebase_service.get_estoque_lista()
        opcoes_pedras = []
        for chapa in chapas:
            raw_price = str(chapa.get('valor_m2', 0))
            try: p = float(raw_price.replace(',', '.'))
            except: p = 0.0
            
            txt_op = f"{chapa.get('nome')} - R$ {p:.2f}/m²"
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=txt_op))
            self.mapa_precos[chapa['id']] = {'nome': chapa.get('nome'), 'preco': p}

        filtro_num = ft.InputFilter(allow=True, regex_string=r"[0-9.,]", replacement_string="")

        # --- 2. INPUTS ESTILIZADOS ---
        self.txt_ambiente = ft.TextField(label="Ambiente", hint_text="Ex: Cozinha Gourmet", border_radius=BORDER_RADIUS_MD, filled=True, bgcolor=COLOR_WHITE)
        self.dd_pedra = ft.Dropdown(label="Selecione o Material", options=opcoes_pedras, border_radius=BORDER_RADIUS_MD, filled=True, bgcolor=COLOR_WHITE, on_change=self.calcular)
        
        self.txt_larg = ft.TextField(label="Largura", suffix_text="m", input_filter=filtro_num, border_radius=BORDER_RADIUS_MD, filled=True, bgcolor=COLOR_WHITE, on_change=self.calcular)
        self.txt_prof = ft.TextField(label="Profundidade", suffix_text="m", input_filter=filtro_num, border_radius=BORDER_RADIUS_MD, filled=True, bgcolor=COLOR_WHITE, on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/m)", value="130.00", input_filter=filtro_num, border_radius=BORDER_RADIUS_MD, filled=True, bgcolor=COLOR_WHITE, on_change=self.calcular)

        self.container_medidas = ft.ResponsiveRow([
            ft.Container(self.txt_larg, col={"xs": 12, "md": 4}),
            ft.Container(self.txt_prof, col={"xs": 12, "md": 4}),
            ft.Container(self.txt_acab, col={"xs": 12, "md": 4}),
        ], spacing=10)

        # --- 3. COMPONENTES TÉCNICOS ---
        def criar_linha(label, val_padrao):
            chk = ft.Checkbox(label=label, active_color=COLOR_PRIMARY, on_change=self.toggle_campos)
            txt_c = ft.TextField(label="Comp", value="0.00", width=75, height=40, text_size=12, disabled=True, filled=True, bgcolor=COLOR_WHITE, input_filter=filtro_num, on_change=self.calcular)
            txt_a = ft.TextField(label="Alt", value=val_padrao, width=65, height=40, text_size=12, disabled=True, filled=True, bgcolor=COLOR_WHITE, input_filter=filtro_num, on_change=self.calcular)
            return chk, txt_c, txt_a

        self.chk_rfundo, self.txt_rf_c, self.txt_rf_a = criar_linha("Fundo", "0.10")
        self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a = criar_linha("Frente", "0.10")
        self.chk_resq, self.txt_re_c, self.txt_re_a = criar_linha("Esq.", "0.10")
        self.chk_rdir, self.txt_rd_c, self.txt_rd_a = criar_linha("Dir.", "0.10")

        self.chk_sfundo, self.txt_sf_c, self.txt_sf_a = criar_linha("Fundo", "0.04")
        self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a = criar_linha("Frente", "0.04")
        self.chk_sesq, self.txt_se_c, self.txt_se_a = criar_linha("Esq.", "0.04")
        self.chk_sdir, self.txt_sd_c, self.txt_sd_a = criar_linha("Dir.", "0.04")

        self.chk_cuba = ft.Checkbox(label="Cuba", active_color=COLOR_PRIMARY, on_change=self.toggle_campos)
        self.txt_cuba_pos = ft.TextField(label="Pos", width=65, height=40, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cuba_larg = ft.TextField(label="Lar", width=65, height=40, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cuba_prof = ft.TextField(label="Pro", width=65, height=40, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)

        self.chk_cook = ft.Checkbox(label="Cooktop", active_color=COLOR_PRIMARY, on_change=self.toggle_campos)
        self.txt_cook_pos = ft.TextField(label="Pos", width=65, height=40, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cook_larg = ft.TextField(label="Lar", width=65, height=40, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)
        self.txt_cook_prof = ft.TextField(label="Pro", width=65, height=40, disabled=True, filled=True, input_filter=filtro_num, on_change=self.calcular)

        self.txt_instrucoes = ft.TextField(label="Observações para Produção", multiline=True, filled=True, border_radius=10, min_lines=3)

        # --- 4. CANVAS (Visualização Técnica) ---
        self.canvas = cv.Canvas(
            width=320 if self.eh_mobile else 500, 
            height=300, 
            shapes=[]
        )
        
        self.lbl_valor = ft.Text("R$ 0.00", size=32, weight="bold", color=COLOR_PRIMARY)
        self.lbl_detalhes_pedra = ft.Text("Pedra: 0.00m²", size=13, color=ft.colors.BLUE_GREY_400)
        self.lbl_detalhes_servico = ft.Text("Mão de Obra: R$ 0.00", size=13, color=ft.colors.BLUE_GREY_400)
        
        self.valor_final = 0.0
        self.area_final = 0.0

        # --- 5. MONTAGEM DAS ABAS ---
        def row_full(chk, txt_c, txt_a): return ft.Row([chk, txt_c, txt_a], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        tabs = ft.Tabs(
            selected_index=0, 
            label_color=COLOR_PRIMARY, 
            indicator_color=COLOR_PRIMARY,
            unselected_label_color=ft.colors.BLUE_GREY_400,
            tabs=[
                ft.Tab(text="Base", icon=ft.icons.SQUARE_FOOT, content=ft.Container(padding=ft.padding.only(top=20), content=ft.Column([
                    self.txt_ambiente, self.dd_pedra, self.container_medidas
                ], scroll=ft.ScrollMode.AUTO, spacing=15))),
                
                ft.Tab(text="Rodas", icon=ft.icons.BORDER_TOP, content=ft.Container(padding=ft.padding.only(top=20), content=ft.Column([
                    ft.Text("Definição de Rodabancas", weight="bold", size=14),
                    row_full(self.chk_rfundo, self.txt_rf_c, self.txt_rf_a),
                    row_full(self.chk_rfrente, self.txt_rfr_c, self.txt_rfr_a),
                    row_full(self.chk_resq, self.txt_re_c, self.txt_re_a),
                    row_full(self.chk_rdir, self.txt_rd_c, self.txt_rd_a)
                ], scroll=ft.ScrollMode.AUTO, spacing=10))),
                
                ft.Tab(text="Saias", icon=ft.icons.BORDER_BOTTOM, content=ft.Container(padding=ft.padding.only(top=20), content=ft.Column([
                    ft.Text("Definição de Saias/Acabamento", weight="bold", size=14),
                    row_full(self.chk_sfundo, self.txt_sf_c, self.txt_sf_a),
                    row_full(self.chk_sfrente, self.txt_sfr_c, self.txt_sfr_a),
                    row_full(self.chk_sesq, self.txt_se_c, self.txt_se_a),
                    row_full(self.chk_sdir, self.txt_sd_c, self.txt_sd_a)
                ], scroll=ft.ScrollMode.AUTO, spacing=10))),
                
                ft.Tab(text="Cortes", icon=ft.icons.CONTENT_CUT, content=ft.Container(padding=ft.padding.only(top=20), content=ft.Column([
                    ft.Text("Vãos para Cubas e Cooktops", weight="bold", size=14),
                    ft.Row([self.chk_cuba, self.txt_cuba_pos, self.txt_cuba_larg, self.txt_cuba_prof], spacing=5),
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([self.chk_cook, self.txt_cook_pos, self.txt_cook_larg, self.txt_cook_prof], spacing=5)
                ], scroll=ft.ScrollMode.AUTO))),
                
                ft.Tab(text="Notas", icon=ft.icons.EDIT_NOTE, content=ft.Container(padding=ft.padding.only(top=20), content=self.txt_instrucoes))
            ]
        )

        # --- 6. LAYOUT FINAL ---
        self.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda e: self.on_cancel(), icon_size=20),
                ft.Text("Editor de Peça", size=22, weight="bold", color=COLOR_PRIMARY)
            ]),
            ft.Divider(height=1, color="#EEEEEE"),
            ft.Container(height=380, content=tabs),
            ft.Divider(height=20, color="transparent"),
            
            # Área de Visualização com Card
            ft.Container(
                content=ft.Column([
                    ft.Text("Croqui Técnico", weight="bold", size=12, color=ft.colors.BLUE_GREY_400),
                    ft.Container(
                        content=self.canvas, 
                        bgcolor="#F9F9F9", 
                        border_radius=15, 
                        padding=10,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, "#EEEEEE")
                    ),
                    ft.Column([
                        self.lbl_valor,
                        self.lbl_detalhes_pedra,
                        self.lbl_detalhes_servico
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10
            ),
            
            ft.Container(height=10),
            ft.ElevatedButton(
                "ADICIONAR PEÇA AO ORÇAMENTO", 
                bgcolor=COLOR_PRIMARY, 
                color=COLOR_WHITE, 
                height=55, 
                width=float("inf"), 
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                on_click=self.salvar
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        # Logica de inicialização (Inalterada)
        if self.item_para_editar: 
            # ... (seu bloco de carregamento de dados aqui é igual)
            self.calcular(None, update_ui=False)

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