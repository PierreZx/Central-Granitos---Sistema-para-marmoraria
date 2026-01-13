# src/views/components/budget_canvas.py

import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.scale = 120 
        self.padding = 50

    def build(self):
        shapes = []
        for peca in self.composition.pecas:
            x_off = self.padding
            y_off = self.padding
            w_px = peca.largura * self.scale
            h_px = peca.profundidade * self.scale

            # DESENHO DA PEDRA (COR ESCURA PARA CONTRASTE)
            shapes.append(
                cv.Rect(
                    x=x_off, y=y_off, width=w_px, height=h_px,
                    paint=ft.Paint(color=ft.colors.GREY_400, style=ft.PaintingStyle.FILL)
                )
            )
            shapes.append(
                cv.Rect(
                    x=x_off, y=y_off, width=w_px, height=h_px,
                    paint=ft.Paint(color=ft.colors.BLACK, stroke_width=2, style=ft.PaintingStyle.STROKE)
                )
            )

            # ACABAMENTOS
            if peca.saia and peca.saia.lados:
                p_saia = ft.Paint(color=ft.colors.BLUE_700, stroke_width=5)
                if "frente" in peca.saia.lados: shapes.append(cv.Line(x_off, y_off + h_px, x_off + w_px, y_off + h_px, p_saia))
                if "esquerda" in peca.saia.lados: shapes.append(cv.Line(x_off, y_off, x_off, y_off + h_px, p_saia))
                if "direita" in peca.saia.lados: shapes.append(cv.Line(x_off + w_px, y_off, x_off + w_px, y_off + h_px, p_saia))

            # MEDIDAS (TEXTO)
            shapes.append(
                cv.Text(
                    x=x_off + w_px/2 - 20, y=y_off - 35,
                    text=f"{peca.largura}m",
                    style=ft.TextStyle(size=14, weight="bold", color=ft.colors.BLACK)
                )
            )
            shapes.append(
                cv.Text(
                    x=x_off - 45, y=y_off + h_px/2 - 10,
                    text=f"{peca.profundidade}m",
                    style=ft.TextStyle(size=14, weight="bold", color=ft.colors.BLACK)
                )
            )

        return ft.Container(
            content=cv.Canvas(shapes=shapes, width=400, height=300),
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            alignment=ft.alignment.center,
            width=400,
            height=300
        )