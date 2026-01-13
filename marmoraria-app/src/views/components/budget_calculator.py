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
        # --- CARREGAR DADOS ---
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = []
        for chapa in chapas:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('preco_m2', 0) or 0)
            txt_op = f"{nome} - R$ {preco:.2f}/m²"
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=txt_op))
            self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- COMPONENTES DA INTERFACE ---
        self.txt_ambiente = ft.TextField(label="Ambiente", border_radius=8, height=45, text_size=14)
        self.dd_pedra = ft.Dropdown(label="Selecionar Pedra", options=opcoes_pedras, border_radius=8, height=45, text_size=14)
        self.txt_larg = ft.TextField(label="Comprimento (m)", suffix_text="m", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        self.txt_prof = ft.TextField(label="Profundidade (m)", suffix_text="m", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", expand=True, keyboard_type=ft.KeyboardType.NUMBER, height=45, text_size=14)

        def criar_linha_config(label_chk, valor_padrao_alt):
            chk = ft.Checkbox(label=label_chk, value=False)
            txt_alt = ft.TextField(label="Alt (m)", value=valor_padrao_alt, width=80, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
            return chk, txt_alt

        # Configurações de Acabamento (Simplicado para Mobile)
        self.chk_rfundo, self.txt_rf_a = criar_linha_config("Rodo Fundo", "0.10")
        self.chk_resq, self.txt_re_a = criar_linha_config("Rodo Esq", "0.10")
        self.chk_rdir, self.txt_rd_a = criar_linha_config("Rodo Dir", "0.10")
        
        self.chk_sfrente, self.txt_sfr_a = criar_linha_config("Saia Frente", "0.04")
        self.chk_sesq, self.txt_se_a = criar_linha_config("Saia Esq", "0.04")
        self.chk_sdir, self.txt_sd_a = criar_linha_config("Saia Dir", "0.04")

        self.chk_cuba = ft.Checkbox(label="Bojo/Cuba", value=False)
        self.txt_pos_cuba = ft.TextField(label="Eixo (m)", value="0.50", width=80, height=40, text_size=12)

        self.canvas = cv.Canvas(width=350, height=300, shapes=[])
        self.lbl_valor = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)
        self.valor_final = 0.0

        # Ativar cálculos automáticos
        inputs = [self.txt_larg, self.txt_prof, self.txt_acab, self.dd_pedra, 
                  self.txt_rf_a, self.txt_re_a, self.txt_rd_a, 
                  self.txt_sfr_a, self.txt_se_a, self.txt_sd_a, self.txt_pos_cuba,
                  self.chk_rfundo, self.chk_resq, self.chk_rdir, 
                  self.chk_sfrente, self.chk_sesq, self.chk_sdir, self.chk_cuba]
        
        for i in inputs: i.on_change = self.calcular

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([self.txt_ambiente, self.dd_pedra, ft.Row([self.txt_larg, self.txt_prof]), self.txt_acab], spacing=10)),
            ft.Tab(text="Acabamentos", content=ft.Column([
                ft.Text("Rodobancas (Fundo/Laterais)", size=12, weight="bold"),
                ft.Row([self.chk_rfundo, self.txt_rf_a]),
                ft.Row([self.chk_resq, self.txt_re_a, self.chk_rdir, self.txt_rd_a]),
                ft.Divider(),
                ft.Text("Saias (Frente/Laterais)", size=12, weight="bold"),
                self.chk_sfrente,
                ft.Row([self.chk_sesq, self.txt_se_a, self.chk_sdir, self.txt_sd_a]),
            ], spacing=5)),
            ft.Tab(text="Furos", content=ft.Column([ft.Row([self.chk_cuba, self.txt_pos_cuba])]))
        ], height=280)

        return ft.Container(
            padding=10, bgcolor=COLOR_BACKGROUND,
            content=ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()), ft.Text("Nova Peça", weight="bold")], alignment="spaceBetween"),
                ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
                ft.Text("Visualização Técnica", weight="bold", size=14),
                ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), alignment=ft.alignment.center, height=300),
                ft.Container(
                    padding=15, bgcolor=COLOR_WHITE, border_radius=10,
                    content=ft.Row([
                        ft.Column([ft.Text("Investimento:", size=12), self.lbl_valor], spacing=0),
                        ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self.salvar, height=45)
                    ], alignment="spaceBetween")
                )
            ], scroll=ft.ScrollMode.ALWAYS) # Ativa scroll para telemóveis pequenos
        )

    def calcular(self, e):
        try:
            if not self.dd_pedra.value: return
            l = float(self.txt_larg.value or 0)
            p = float(self.txt_prof.value or 0)
            v_ml = float(self.txt_acab.value or 0)
            if l==0 or p==0: return

            preco_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            
            area = l * p
            ml_total = 0

            # Soma perímetros ativos
            if self.chk_rfundo.value: ml_total += l
            if self.chk_resq.value: ml_total += p
            if self.chk_rdir.value: ml_total += p
            if self.chk_sfrente.value: ml_total += l
            if self.chk_sesq.value: ml_total += p
            if self.chk_sdir.value: ml_total += p

            total = (area * preco_m2) + (ml_total * v_ml)
            if self.chk_cuba.value: total += 150 # Taxa de furo

            self.valor_final = total
            self.lbl_valor.value = f"R$ {total:,.2f}"
            self.desenhar(l, p)
            self.update()
        except: pass

    def desenhar(self, w, h):
        self.canvas.shapes.clear()
        scale = min(300/w, 200/h) * 0.8
        w_px, h_px = w*scale, h*scale
        sx, sy = (350-w_px)/2, (300-h_px)/2
        
        # Pedra
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style="fill", color="#F0F0F0")))
        self.canvas.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))

        # Rodobancas (Vermelho com legenda)
        def draw_rodo(chk, val, x1, y1, x2, y2, tx, ty):
            if chk.value:
                self.canvas.shapes.append(cv.Line(x1, y1, x2, y2, paint=ft.Paint(color="red", stroke_width=4)))
                self.canvas.shapes.append(cv.Text(tx, ty, f"R:{val}m", style=ft.TextStyle(size=10, color="red")))

        draw_rodo(self.chk_rfundo, self.txt_rf_a.value, sx, sy, sx+w_px, sy, sx+w_px/2-20, sy-15)
        draw_rodo(self.chk_resq, self.txt_re_a.value, sx, sy, sx, sy+h_px, sx-45, sy+h_px/2)

        # Saias (Azul com legenda)
        if self.chk_sfrente.value:
            self.canvas.shapes.append(cv.Line(sx, sy+h_px, sx+w_px, sy+h_px, paint=ft.Paint(color="blue", stroke_width=6)))
            self.canvas.shapes.append(cv.Text(sx+w_px/2-20, sy+h_px+5, f"S:{self.txt_sfr_a.value}m", style=ft.TextStyle(size=10, color="blue")))

        # Cuba/Bojo
        if self.chk_cuba.value:
            px = sx + (float(self.txt_pos_cuba.value or 0) * scale)
            self.canvas.shapes.append(cv.Rect(px-25, sy+h_px/2-15, 50, 30, border_radius=5, paint=ft.Paint(style="stroke", color="blue")))
            self.canvas.shapes.append(cv.Text(px-15, sy+h_px/2-5, "EIXO", style=ft.TextStyle(size=8, color="blue")))

        # Medidas Gerais
        self.canvas.shapes.append(cv.Text(sx+w_px/2-10, sy-35, f"{w}m", style=ft.TextStyle(size=12, weight="bold")))
        self.canvas.shapes.append(cv.Text(sx-55, sy+h_px/2-25, f"{h}m", style=ft.TextStyle(size=12, weight="bold")))
        
        self.canvas.update()

    def salvar(self, e):
        if self.valor_final <= 0: return
        item_dict = {
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos[self.dd_pedra.value]['nome'],
            "largura": self.txt_larg.value,
            "profundidade": self.txt_prof.value,
            "preco_total": self.valor_final
        }
        self.on_save_item(item_dict)