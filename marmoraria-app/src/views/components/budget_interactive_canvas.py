# src/views/components/budget_interactive_canvas.py

import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager, BancadaPiece

class BudgetInteractiveCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager, on_change=None):
        super().__init__()
        self.composition = composition
        self.on_change = on_change
        self.scale = 100  # Escala para o modo interativo (1m = 100px)

    def build(self):
        self.canvas = cv.Canvas(
            allow_request_fixed_size=True,
            on_resize=self.update_canvas,
            shapes=[],
            content=ft.GestureDetector(
                on_pan_update=self.on_pan_update,
                drag_interval=10,
            )
        )
        
        return ft.Container(
            content=self.canvas,
            bgcolor="#f0f0f0",
            border_radius=10,
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

    def update_canvas(self, e=None):
        """Redesenha todas as peças na tela com base em suas posições X, Y."""
        self.canvas.shapes.clear()
        
        for peca in self.composition.pecas:
            w = peca.largura * self.scale
            h = peca.profundidade * self.scale
            
            # Desenho da Sombra/Corpo da Pedra
            self.canvas.shapes.append(
                cv.Rect(
                    x=peca.x, y=peca.y, width=w, height=h,
                    border_radius=3,
                    paint=ft.Paint(color=ft.colors.with_opacity(0.8, ft.colors.GREY_400), style=ft.PaintingStyle.FILL)
                )
            )

            # Contorno Principal
            self.canvas.shapes.append(
                cv.Rect(
                    x=peca.x, y=peca.y, width=w, height=h,
                    paint=ft.Paint(color=ft.colors.BLACK, stroke_width=2, style=ft.PaintingStyle.STROKE)
                )
            )

            # Indicação de Saia (Linha Azul na Frente)
            if peca.saia:
                self.canvas.shapes.append(
                    cv.Line(
                        peca.x, peca.y + h, peca.x + w, peca.y + h,
                        paint=ft.Paint(color=ft.colors.BLUE_800, stroke_width=4)
                    )
                )

            # Indicação de Rodobanca (Linha Vermelha no Fundo)
            if peca.rodobanca:
                self.canvas.shapes.append(
                    cv.Line(
                        peca.x, peca.y, peca.x + w, peca.y,
                        paint=ft.Paint(color=ft.colors.RED_800, stroke_width=3)
                    )
                )

            # Texto informativo sobre a peça
            self.canvas.shapes.append(
                cv.Text(
                    peca.x + 5, peca.y + 5,
                    f"{peca.largura}x{peca.profundidade}m",
                    style=ft.TextStyle(size=12, weight="bold", color=ft.colors.BLACK)
                )
            )

        self.update()

    def on_pan_update(self, e: ft.DragUpdateEvent):
        """Lógica para arrastar as peças no canvas."""
        # Se houver apenas uma peça (como no seu caso atual), movemos a primeira
        if self.composition.pecas:
            peca = self.composition.pecas[0]
            peca.x += e.delta_x
            peca.y += e.delta_y
            self.update_canvas()
            if self.on_change:
                self.on_change()