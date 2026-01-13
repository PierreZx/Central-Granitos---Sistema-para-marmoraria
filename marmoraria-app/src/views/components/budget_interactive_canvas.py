# src/views/components/budget_interactive_canvas.py
import flet as ft
import io
import base64
from PIL import Image, ImageDraw
from src.views.components.budget_composition import CompositionManager

class BudgetInteractiveCanvas(ft.UserControl):
    """Canvas interativo usando Pillow"""
    def __init__(self, composition: CompositionManager, width=500, height=350, scale=200, on_change=None):
        super().__init__()
        self.composition = composition
        self.width = width
        self.height = height
        self.scale = scale
        self.on_change = on_change
        self._drag_peca = None
        self._offset_x = 0
        self._offset_y = 0

    def build(self):
        # GestureDetector para arrastar a última peça adicionada
        return ft.GestureDetector(
            content=ft.Image(width=self.width, height=self.height, src_base64=self._render_image()),
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
        )

    def _render_image(self):
        img = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(img)

        for peca in self.composition.pecas:
            w_px = int(peca.largura * self.scale)
            h_px = int(peca.profundidade * self.scale)
            x0 = int(peca.x)
            y0 = int(peca.y)
            x1 = x0 + w_px
            y1 = y0 + h_px

            # Pedra
            draw.rectangle([x0, y0, x1, y1], fill="#f5f5f5", outline="black", width=2)

            # Texto medidas
            draw.text((x0 + 5, y0 + 5), f"{peca.largura:.2f}x{peca.profundidade:.2f}m", fill="black")

            # Aberturas
            for ab in peca.aberturas:
                ab_w = int(ab.largura * self.scale)
                ab_h = int(ab.profundidade * self.scale)
                ab_x = x0 + int(w_px * ab.x_relativo) - ab_w // 2
                ab_y = y0 + int(h_px * ab.y_relativo) - ab_h // 2
                draw.rectangle([ab_x, ab_y, ab_x + ab_w, ab_y + ab_h], outline="red", width=1)
                draw.text((ab_x, ab_y - 15), "EIXO", fill="blue")

            # Acabamentos
            if peca.saia: draw.line([x0, y1, x1, y1], fill="blue", width=4)
            if peca.rodobanca: draw.line([x0, y0, x1, y0], fill="red", width=3)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def _on_pan_start(self, e):
        if self.composition.pecas:
            self._drag_peca = self.composition.pecas[-1]
            self._offset_x = e.local_x - self._drag_peca.x
            self._offset_y = e.local_y - self._drag_peca.y

    def _on_pan_update(self, e):
        if self._drag_peca:
            self._drag_peca.x = e.local_x - self._offset_x
            self._drag_peca.y = e.local_y - self._offset_y
            self.content.src_base64 = self._render_image()
            self.update()
            if self.on_change:
                self.on_change()
