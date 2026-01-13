# src/views/components/budget_canvas.py

import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.scale = 150  # Escala: 1 metro = 150 pixels
        self.padding = 40

    def build(self):
        # Criamos o canvas onde o desenho será feito
        shapes = []
        
        # Cursor inicial para o desenho
        x_offset = self.padding
        y_offset = self.padding

        for peca in self.composition.pecas:
            w_px = peca.largura * self.scale
            h_px = peca.profundidade * self.scale

            # 1. DESENHO DA PEDRA (O retângulo principal)
            shapes.append(
                cv.Rect(
                    x=x_offset,
                    y=y_offset,
                    width=w_px,
                    height=h_px,
                    border_radius=2,
                    paint=ft.Paint(
                        color=ft.colors.GREY_300,
                        style=ft.PaintingStyle.FILL,
                    ),
                )
            )
            # Bordas da pedra
            shapes.append(
                cv.Rect(
                    x=x_offset,
                    y=y_offset,
                    width=w_px,
                    height=h_px,
                    paint=ft.Paint(
                        color=ft.colors.BLACK,
                        stroke_width=2,
                        style=ft.PaintingStyle.STROKE,
                    ),
                )
            )

            # 2. INDICAÇÃO DE SAIA (Linha mais grossa na frente)
            if peca.saia:
                shapes.append(
                    cv.Line(
                        x_offset, y_offset + h_px, 
                        x_offset + w_px, y_offset + h_px,
                        paint=ft.Paint(color=ft.colors.BLUE_700, stroke_width=5)
                    )
                )
                shapes.append(cv.Text(x_offset + 5, y_offset + h_px + 5, f"Saia {peca.saia.altura}m", size=10))

            # 3. INDICAÇÃO DE RODOBANCA (Linha dupla no fundo/atrás)
            if peca.rodobanca:
                shapes.append(
                    cv.Line(
                        x_offset, y_offset, 
                        x_offset + w_px, y_offset,
                        paint=ft.Paint(color=ft.colors.RED_700, stroke_width=4)
                    )
                )
                shapes.append(cv.Text(x_offset + 5, y_offset - 20, f"Rodo. {peca.rodobanca.altura}m", size=10))

            # 4. MEDIDAS (Cotas)
            # Largura
            shapes.append(cv.Text(x_offset + w_px/2 - 20, y_offset + h_px/2, f"{peca.largura}m", weight="bold"))
            # Profundidade
            shapes.append(cv.Text(x_offset - 35, y_offset + h_px/2 - 10, f"{peca.profundidade}m", weight="bold"))

        return ft.Container(
            content=cv.Canvas(
                shapes=shapes,
                width=500,
                height=300,
            ),
            alignment=ft.alignment.center,
            expand=True
        )