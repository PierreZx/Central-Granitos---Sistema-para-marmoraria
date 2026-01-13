# src/views/components/budget_canvas.py
import flet as ft
import io
import base64
from PIL import Image, ImageDraw
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager, width=500, height=350, scale=200):
        super().__init__()
        self.composition = composition
        self.canvas_w = width
        self.canvas_h = height
        self.scale = scale

    def build(self):
        img = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        draw = ImageDraw.Draw(img)
        m_left, m_top = 20, 20

        for peca in self.composition.pecas:
            w_px = int(peca.largura * self.scale)
            h_px = int(peca.profundidade * self.scale)
            x0, y0 = m_left, m_top
            x1, y1 = x0 + w_px, y0 + h_px

            draw.rectangle([x0, y0, x1, y1], fill="#f5f5f5", outline="black", width=2)
            # Cotas
            draw.line([x0, y0-20, x1, y0-20], fill="black", width=1)
            draw.text((x0 + w_px/2 - 20, y0-35), f"{peca.largura:.2f}m", fill="black")
            draw.line([x0-20, y0, x0-20, y1], fill="black", width=1)
            draw.text((x0-50, y0 + h_px/2 - 5), f"{peca.profundidade:.2f}m", fill="black")

            # Aberturas
            for ab in peca.aberturas:
                ab_w = int(ab.largura * self.scale)
                ab_h = int(ab.profundidade * self.scale)
                ab_x = x0 + int(w_px * ab.x_relativo) - ab_w//2
                ab_y = y0 + int(h_px * ab.y_relativo) - ab_h//2
                draw.rectangle([ab_x, ab_y, ab_x+ab_w, ab_y+ab_h], outline="red", width=1)
                draw.line([ab_x + ab_w//2, y0-40, ab_x + ab_w//2, y1+20], fill="blue", width=1)
                draw.text((ab_x + ab_w//2 - 20, y0-55), "EIXO", fill="blue")

            # Acabamentos
            if peca.saia: draw.line([x0, y1, x1, y1], fill="blue", width=4)
            if peca.rodobanca: draw.line([x0, y0, x1, y0], fill="red", width=3)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return ft.Image(src_base64=img_str, width=self.canvas_w, height=self.canvas_h, fit=ft.ImageFit.CONTAIN)
