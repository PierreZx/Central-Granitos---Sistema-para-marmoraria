# src/views/components/budget_calculator.py

import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND
from src.services import firebase_service
from src.views.components.budget_composition import BancadaPiece, Abertura

class BudgetCalculator(ft.UserControl):
    def __init__(self, page, on_save_item, on_cancel, item=None):
        super().__init__()
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel
        self.item_para_editar = item 
        self.mapa_precos = {}
        
        # Estado para a Peça de Encaixe (Bancada em L)
        self.tem_encaixe = False
        self.lado_encaixe = "direita" # Onde a segunda peça encosta

    def build(self):
        # --- CARREGAR DADOS DO ESTOQUE ---
        chapas = firebase_service.get_collection("estoque")
        opcoes_pedras = []
        for chapa in chapas:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('preco_m2', 0) or 0)
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=f"{nome} - R$ {preco:.2f}/m²"))
            self.mapa_precos[chapa['id']] = {'nome': nome, 'preco': preco}

        # --- FUNÇÃO PARA TRATAR VÍRGULA E PONTO ---
        def on_num_change(e):
            if e.control.value:
                # Substitui vírgula por ponto para o cálculo matemático
                e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # --- INPUTS DA PEÇA PRINCIPAL ---
        # Alterado para KeyboardType.TEXT para garantir que a vírgula apareça no teclado
        kb_text = ft.KeyboardType.TEXT 
        
        self.txt_ambiente = ft.TextField(label="Ambiente", border_radius=8, height=45, value="Cozinha")
        self.dd_pedra = ft.Dropdown(label="Selecionar Pedra", options=opcoes_pedras, border_radius=8, height=45, on_change=self.calcular)
        self.txt_larg = ft.TextField(label="Comprimento (m)", value="1.00", expand=True, keyboard_type=kb_text, on_change=on_num_change)
        self.txt_prof = ft.TextField(label="Profundidade (m)", value="0.60", expand=True, keyboard_type=kb_text, on_change=on_num_change)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130.00", expand=True, keyboard_type=kb_text, on_change=on_num_change)

        # --- INPUTS DA PEÇA DE ENCAIXE (L) ---
        self.txt_larg_enc = ft.TextField(label="Comprimento L (m)", value="0.80", expand=True, keyboard_type=kb_text, on_change=on_num_change, visible=False)
        self.txt_prof_enc = ft.TextField(label="Profundidade L (m)", value="0.60", expand=True, keyboard_type=kb_text, on_change=on_num_change, visible=False)
        self.dd_lado_enc = ft.Dropdown(
            label="Encaixar na...", value="direita", visible=False,
            options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")],
            on_change=self.calcular
        )

        def campo_alt(val): 
            return ft.TextField(label="Alt (m)", value=val, width=75, height=40, text_size=12, keyboard_type=kb_text, on_change=on_num_change)

        # --- ACABAMENTOS ---
        self.chk_rfundo = ft.Checkbox(label="Rodo Fundo", value=True, on_change=self.calcular)
        self.txt_rf_a = campo_alt("0.10")
        self.chk_sfrente = ft.Checkbox(label="Saia Frente", value=True, on_change=self.calcular)
        self.txt_sfr_a = campo_alt("0.04")

        # --- FUROS ---
        self.sw_bojo = ft.Switch(label="Bojo", value=False, on_change=self.calcular)
        self.bojo_w = ft.TextField(label="Larg (m)", value="0.50", width=75, height=40, text_size=11, keyboard_type=kb_text, on_change=on_num_change)
        self.bojo_h = ft.TextField(label="Prof (m)", value="0.40", width=75, height=40, text_size=11, keyboard_type=kb_text, on_change=on_num_change)
        self.bojo_x = ft.TextField(label="Eixo (m)", value="0.50", width=75, height=40, text_size=11, keyboard_type=kb_text, on_change=on_num_change)

        self.sw_cook = ft.Switch(label="Cooktop", value=False, on_change=self.calcular)
        self.cook_w = ft.TextField(label="Larg (m)", value="0.55", width=75, height=40, text_size=11, keyboard_type=kb_text, on_change=on_num_change)
        self.cook_h = ft.TextField(label="Prof (m)", value="0.45", width=75, height=40, text_size=11, keyboard_type=kb_text, on_change=on_num_change)
        self.cook_x = ft.TextField(label="Eixo (m)", value="1.50", width=75, height=40, text_size=11, keyboard_type=kb_text, on_change=on_num_change)

        self.canvas = cv.Canvas(width=350, height=350, shapes=[])
        self.lbl_valor = ft.Text("R$ 0.00", size=24, weight="bold", color=COLOR_PRIMARY)

        # --- BOTÃO ADICIONAR ENCAIXE ---
        def toggle_encaixe(e):
            self.tem_encaixe = not self.tem_encaixe
            self.txt_larg_enc.visible = self.tem_encaixe
            self.txt_prof_enc.visible = self.tem_encaixe
            self.dd_lado_enc.visible = self.tem_encaixe
            btn_encaixe.text = "Remover Encaixe" if self.tem_encaixe else "Adicionar Peça Encaixe (L)"
            btn_encaixe.icon = ft.icons.REMOVE_CIRCLE if self.tem_encaixe else ft.icons.ADD_CIRCLE
            self.calcular()

        btn_encaixe = ft.ElevatedButton("Adicionar Peça Encaixe (L)", icon=ft.icons.ADD_CIRCLE, on_click=toggle_encaixe)

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Base", content=ft.Column([
                self.txt_ambiente, self.dd_pedra, 
                ft.Row([self.txt_larg, self.txt_prof]), 
                ft.Divider(),
                btn_encaixe,
                ft.Row([self.txt_larg_enc, self.txt_prof_enc]),
                self.dd_lado_enc,
                self.txt_acab
            ], spacing=10, scroll=ft.ScrollMode.ALWAYS)),
            ft.Tab(text="Acabam.", content=ft.Column([
                ft.Row([self.chk_rfundo, self.txt_rf_a], alignment="spaceBetween"),
                ft.Row([self.chk_sfrente, self.txt_sfr_a], alignment="spaceBetween"),
            ])),
            ft.Tab(text="Furos", content=ft.Column([
                ft.Row([self.sw_bojo, self.bojo_w, self.bojo_h, self.bojo_x], wrap=True),
                ft.Divider(),
                ft.Row([self.sw_cook, self.cook_w, self.cook_h, self.cook_x], wrap=True),
            ]))
        ], height=350)

        return ft.Container(
            padding=10, bgcolor=COLOR_BACKGROUND,
            content=ft.Column([
                ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel()), ft.Text("Configurar Bancada", weight="bold")]),
                ft.Container(content=tabs, padding=10, bgcolor=COLOR_WHITE, border_radius=10),
                ft.Container(content=self.canvas, bgcolor=ft.colors.WHITE, border_radius=10, border=ft.border.all(1, "#ddd"), alignment=ft.alignment.center, height=350),
                ft.Container(padding=15, bgcolor=COLOR_WHITE, border_radius=10, content=ft.Row([
                    ft.Column([ft.Text("Total:", size=12), self.lbl_valor]),
                    ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=self.salvar, height=45)
                ], alignment="spaceBetween"))
            ], scroll=ft.ScrollMode.ALWAYS)
        )

    def calcular(self, e=None):
        try:
            if not self.dd_pedra.value: return
            def to_f(v): return float(str(v).replace(",", ".")) if v else 0.0
            
            p_m2 = self.mapa_precos[self.dd_pedra.value]['preco']
            v_ml = to_f(self.txt_acab.value)
            
            # Peça 1
            l1, p1 = to_f(self.txt_larg.value), to_f(self.txt_prof.value)
            total = (l1 * p1 * p_m2)
            ml = 0
            if self.chk_rfundo.value: ml += l1
            if self.chk_sfrente.value: ml += l1
            
            # Peça 2 (Encaixe)
            l2, p2 = 0, 0
            if self.tem_encaixe:
                l2, p2 = to_f(self.txt_larg_enc.value), to_f(self.txt_prof_enc.value)
                total += (l2 * p2 * p_m2)
                ml += l2 # Assume saia/rodo também no encaixe
            
            total += (ml * v_ml)
            if self.sw_bojo.value: total += 150
            if self.sw_cook.value: total += 100

            self.lbl_valor.value = f"R$ {total:,.2f}"
            self.desenhar(l1, p1, l2, p2)
            self.update()
        except: pass

    def desenhar(self, w1, h1, w2, h2):
        self.canvas.shapes.clear()
        # Escala ajustada para caber as duas peças
        scale = min(300/(w1+w2+0.5), 200/(max(h1, h2)+0.5)) * 0.7
        w1_px, h1_px = w1*scale, h1*scale
        w2_px, h2_px = w2*scale, h2*scale
        
        # Centralização baseada no L
        total_w_px = w1_px + (w2_px if self.tem_encaixe else 0)
        sx, sy = (350 - total_w_px)/2, (350 - h1_px)/2

        # --- DESENHO PEÇA 1 ---
        self.canvas.shapes.append(cv.Rect(sx, sy, w1_px, h1_px, paint=ft.Paint(style="fill", color="#F0F0F0")))
        self.canvas.shapes.append(cv.Rect(sx, sy, w1_px, h1_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))
        
        # --- DESENHO PEÇA 2 (ENCAIXE) ---
        if self.tem_encaixe:
            # Lógica de colagem: esquerda ou direita
            ex = sx + w1_px if self.dd_lado_enc.value == "direita" else sx - w2_px
            self.canvas.shapes.append(cv.Rect(ex, sy, w2_px, h2_px, paint=ft.Paint(style="fill", color="#E0E0E0")))
            self.canvas.shapes.append(cv.Rect(ex, sy, w2_px, h2_px, paint=ft.Paint(style="stroke", color="black", stroke_width=2)))
            self.canvas.shapes.append(cv.Text(ex + w2_px/2 - 10, sy + h2_px + 20, f"{w2}m", style=ft.TextStyle(size=10)))

        # --- ACABAMENTOS E FUROS (Na Peça Principal) ---
        if self.chk_rfundo.value:
            self.canvas.shapes.append(cv.Line(sx, sy, sx+w1_px, sy, paint=ft.Paint(color="red", stroke_width=5)))
            self.canvas.shapes.append(cv.Text(sx+w1_px/2-20, sy-15, f"R:{self.txt_rf_a.value}m", style=ft.TextStyle(size=9, color="red")))

        if self.sw_bojo.value:
            px = sx + (float(str(self.bojo_x.value or 0).replace(",",".")) * scale)
            bw, bh = float(str(self.bojo_w.value or 0).replace(",",".")) * scale, float(str(self.bojo_h.value or 0).replace(",",".")) * scale
            self.canvas.shapes.append(cv.Rect(px - bw/2, sy + (h1_px-bh)/2, bw, bh, border_radius=3, paint=ft.Paint(style="stroke", color="blue")))
            self.canvas.shapes.append(cv.Text(px - 12, sy + h1_px/2 - 5, "EIXO", style=ft.TextStyle(size=7, color="blue")))

        # --- COTAS PEÇA 1 ---
        self.canvas.shapes.append(cv.Text(sx+w1_px/2-10, sy-35, f"{w1}m", style=ft.TextStyle(size=11, weight="bold")))
        self.canvas.shapes.append(cv.Text(sx-50, sy+h1_px/2-10, f"{h1}m", style=ft.TextStyle(size=11, weight="bold")))
        self.canvas.update()

    def salvar(self, e):
        if not self.dd_pedra.value or self.lbl_valor.value == "R$ 0.00": return
        total_puro = float(self.lbl_valor.value.replace("R$ ", "").replace(".", "").replace(",", "."))
        item_dict = {
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos[self.dd_pedra.value]['nome'],
            "largura": self.txt_larg.value,
            "profundidade": self.txt_prof.value,
            "preco_total": total_puro,
            "tem_encaixe": self.tem_encaixe # Informação importante para o PDF
        }
        self.on_save_item(item_dict)