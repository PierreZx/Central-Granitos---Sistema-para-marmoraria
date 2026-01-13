# src/views/components/budget_interactive_canvas.py

import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager

class BudgetInteractiveCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager, on_change=None):
        super().__init__()
        self.composition = composition
        self.on_change = on_change
        self.scale = 100 

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
            expand=True
        )

    def update_canvas(self, e=None):
        self.canvas.shapes.clear()
        
        for peca in self.composition.pecas:
            w = peca.largura * self.scale
            h = peca.profundidade * self.scale
            
            # Pedra
            self.canvas.shapes.append(
                cv.Rect(
                    x=peca.x, y=peca.y, width=w, height=h,
                    paint=ft.Paint(color="#CCCCCC", style=ft.PaintingStyle.FILL)
                )
            )
            self.canvas.shapes.append(
                cv.Rect(
                    x=peca.x, y=peca.y, width=w, height=h,
                    paint=ft.Paint(color="black", stroke_width=2, style=ft.PaintingStyle.STROKE)
                )
            )

            # Texto Medida
            self.canvas.shapes.append(
                cv.Text(peca.x + 5, peca.y + 5, f"{peca.largura}x{peca.profundidade}m", size=10, weight="bold")
            )

        self.update()

    def on_pan_update(self, e: ft.DragUpdateEvent):
        if self.composition.pecas:
            # Move a última peça adicionada para teste de encaixe
            peca = self.composition.pecas[-1]
            peca.x += e.delta_x
            peca.y += e.delta_y
            self.update_canvas()
            if self.on_change:
                self.on_change()