# src/views/components/budget_canvas.py

import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.scale = 140 
        self.padding = 60

    def build(self):
        shapes = []
        for peca in self.composition.pecas:
            x_off = self.padding
            y_off = self.padding
            w_px = peca.largura * self.scale
            h_px = peca.profundidade * self.scale

            shapes.append(cv.Rect(x=x_off, y=y_off, width=w_px, height=h_px, paint=ft.Paint(color="#EEEEEE", style=ft.PaintingStyle.FILL)))
            shapes.append(cv.Rect(x=x_off, y=y_off, width=w_px, height=h_px, paint=ft.Paint(color="black", stroke_width=2, style=ft.PaintingStyle.STROKE)))

            if peca.saia and peca.saia.lados:
                p_saia = ft.Paint(color="blue", stroke_width=4)
                if "frente" in peca.saia.lados: shapes.append(cv.Line(x_off, y_off + h_px, x_off + w_px, y_off + h_px, p_saia))
                if "fundo" in peca.saia.lados: shapes.append(cv.Line(x_off, y_off, x_off + w_px, y_off, p_saia))
                if "esquerda" in peca.saia.lados: shapes.append(cv.Line(x_off, y_off, x_off, y_off + h_px, p_saia))
                if "direita" in peca.saia.lados: shapes.append(cv.Line(x_off + w_px, y_off, x_off + w_px, y_off + h_px, p_saia))

            if peca.rodobanca and peca.rodobanca.lados:
                p_rodo = ft.Paint(color="red", stroke_width=3)
                if "fundo" in peca.rodobanca.lados: shapes.append(cv.Line(x_off, y_off - 4, x_off + w_px, y_off - 4, p_rodo))
                if "esquerda" in peca.rodobanca.lados: shapes.append(cv.Line(x_off - 4, y_off, x_off - 4, y_off + h_px, p_rodo))
                if "direita" in peca.rodobanca.lados: shapes.append(cv.Line(x_off + w_px + 4, y_off, x_off + w_px + 4, y_off + h_px, p_rodo))

            for ab in peca.aberturas:
                ab_w = ab.largura * self.scale
                ab_h = ab.profundidade * self.scale
                ab_x = x_off + (w_px * ab.x_relativo) - (ab_w / 2)
                ab_y = y_off + (h_px * ab.y_relativo) - (ab_h / 2)
                shapes.append(cv.Rect(x=ab_x, y=ab_y, width=ab_w, height=ab_h, paint=ft.Paint(color="red", stroke_width=1, style=ft.PaintingStyle.STROKE, stroke_dash_pattern=[5, 5])))
                shapes.append(cv.Line(ab_x + ab_w/2, y_off - 10, ab_x + ab_w/2, y_off + h_px + 10, paint=ft.Paint(color="blue", stroke_width=1, stroke_dash_pattern=[10, 5])))
                # CORREÇÃO AQUI: font_size em vez de size
                shapes.append(cv.Text(ab_x + ab_w/2 - 12, y_off - 25, "EIXO", font_size=8, color="blue"))

            # CORREÇÃO AQUI: font_size em vez de size
            shapes.append(cv.Text(x_off + w_px/2 - 15, y_off - 40, f"{peca.largura}m", font_size=11, weight="bold"))
            shapes.append(cv.Text(x_off - 45, y_off + h_px/2 - 10, f"{peca.profundidade}m", font_size=11, weight="bold"))

        return ft.Container(content=cv.Canvas(shapes=shapes, width=500, height=300), alignment=ft.alignment.center, width=500, height=300)