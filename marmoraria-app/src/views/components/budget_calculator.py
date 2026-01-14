# src/views/components/budget_calculator.py

import flet as ft
import flet.canvas as cv
from src.config import COLOR_PRIMARY, COLOR_WHITE
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

    # ===============================
    # UTIL
    # ===============================
    def to_f(self, v):
        try:
            return float(str(v).replace(",", ".")) if v else 0.0
        except:
            return 0.0

    # ===============================
    # BUILD
    # ===============================
    def build(self):
        chapas = firebase_service.get_collection("estoque")

        self.mapa_precos = {
            c["id"]: {
                "nome": c.get("nome", ""),
                "preco": float(c.get("preco_m2", 0))
            }
            for c in chapas
        }

        opcoes_pedras = [
            ft.dropdown.Option(
                key=c["id"],
                text=f"{c.get('nome')} - R$ {float(c.get('preco_m2', 0)):.2f}/m²"
            )
            for c in chapas
        ]

        def on_num_change(e):
            if "," in e.control.value:
                e.control.value = e.control.value.replace(",", ".")
            self.calcular()

        # -------- CAMPOS --------
        self.txt_ambiente = ft.TextField(label="Ambiente", value="Cozinha")
        self.dd_pedra = ft.Dropdown(label="Material", options=opcoes_pedras, on_change=self.calcular)
        self.txt_acab = ft.TextField(label="Mão de Obra (R$/ML)", value="130", on_change=on_num_change)

        def criar_peca(visivel=True):
            return {
                "l": ft.TextField(label="Comprimento (m)", value="1.00", on_change=on_num_change, visible=visivel),
                "p": ft.TextField(label="Profundidade (m)", value="0.60", on_change=on_num_change, visible=visivel),
                "lado": ft.Dropdown(
                    label="Posição",
                    value="direita",
                    options=[ft.dropdown.Option("esquerda"), ft.dropdown.Option("direita")],
                    on_change=self.calcular,
                    visible=visivel
                )
            }

        self.p1 = criar_peca(True)
        self.p2 = criar_peca(False)
        self.p3 = criar_peca(False)

        def lados():
            return {k: ft.Checkbox(label=k.capitalize(), on_change=self.calcular)
                    for k in ["fundo", "frente", "esquerda", "direita"]}

        self.p1_rodo = lados()
        self.p1_saia = lados()
        self.p1_rodo["fundo"].value = True
        self.p1_saia["frente"].value = True

        self.p2_rodo = lados()
        self.p2_saia = lados()
        self.p3_rodo = lados()
        self.p3_saia = lados()

        # -------- CANVAS --------
        self.canvas = cv.Canvas(width=350, height=350, shapes=[])

        self.lbl_total = ft.Text("R$ 0,00", size=24, weight="bold", color=COLOR_PRIMARY)

        # -------- TABS --------
        tabs = ft.Tabs(tabs=[
            ft.Tab(text="Base", content=ft.Column([
                self.txt_ambiente,
                self.dd_pedra,
                ft.Row([self.p1["l"], self.p1["p"]]),
                ft.ElevatedButton("+ Peça L", on_click=lambda e: self.toggle_p(2)),
                ft.Row([self.p2["l"], self.p2["p"]]),
                self.p2["lado"],
                ft.ElevatedButton("+ Peça U", on_click=lambda e: self.toggle_p(3)),
                ft.Row([self.p3["l"], self.p3["p"]]),
                self.p3["lado"],
                self.txt_acab
            ], scroll=ft.ScrollMode.AUTO)),
        ])

        return ft.Column([
            tabs,
            ft.Container(
                self.canvas,
                bgcolor=COLOR_WHITE,
                border=ft.border.all(1, "#DDD"),
                border_radius=10,
                alignment=ft.alignment.center
            ),
            ft.Row([
                self.lbl_total,
                ft.ElevatedButton("Salvar", on_click=self.salvar)
            ], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.AUTO)

    # ===============================
    # TOGGLES
    # ===============================
    def toggle_p(self, n):
        if n == 2:
            self.tem_p2 = not self.tem_p2
            vis = self.tem_p2
            p = self.p2
        else:
            self.tem_p3 = not self.tem_p3
            vis = self.tem_p3
            p = self.p3

        for c in p.values():
            c.visible = vis

        self.calcular()

    # ===============================
    # CÁLCULO
    # ===============================
    def calcular(self, e=None):
        if not self.dd_pedra.value:
            return

        preco_m2 = self.mapa_precos[self.dd_pedra.value]["preco"]
        ml = 0
        total = 0

        def calc(l, p):
            return self.to_f(l.value) * self.to_f(p.value)

        total += calc(self.p1["l"], self.p1["p"]) * preco_m2

        if self.tem_p2:
            total += calc(self.p2["l"], self.p2["p"]) * preco_m2
        if self.tem_p3:
            total += calc(self.p3["l"], self.p3["p"]) * preco_m2

        total += ml * self.to_f(self.txt_acab.value)

        self.lbl_total.value = f"R$ {total:,.2f}"
        self.desenhar()
        self.update()

    # ===============================
    # DESENHO (CORRIGIDO)
    # ===============================
    def desenhar(self):
        self.canvas.shapes.clear()

        w = self.to_f(self.p1["l"].value)
        h = self.to_f(self.p1["p"].value)

        if w <= 0 or h <= 0:
            self.canvas.update()
            return

        scale = min(300 / w, 200 / h)
        x = 175 - (w * scale) / 2
        y = 175 - (h * scale) / 2

        self.canvas.shapes.append(
            cv.Rect(
                x, y,
                w * scale, h * scale,
                paint=ft.Paint(style="stroke", color="black", stroke_width=2)
            )
        )

        self.canvas.shapes.append(
            cv.Text(x + (w * scale) / 2 - 15, y - 20, f"{w}m")
        )

        self.canvas.update()

    # ===============================
    # SALVAR
    # ===============================
    def salvar(self, e):
        total = float(
            self.lbl_total.value
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
        )

        self.on_save_item({
            "ambiente": self.txt_ambiente.value,
            "material": self.mapa_precos[self.dd_pedra.value]["nome"],
            "largura": self.p1["l"].value,
            "profundidade": self.p1["p"].value,
            "preco_total": total
        })
