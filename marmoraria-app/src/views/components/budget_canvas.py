# src/views/components/budget_canvas.py
import flet as ft
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.canvas_w = 1200
        self.canvas_h = 800
        self.scale = 400

    def build(self):
        img = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        draw = ImageDraw.Draw(img)
        m_left, m_top = 150, 200

        for peca in self.composition.pecas:
            w_px = int(peca.largura * self.scale)
            h_px = int(peca.profundidade * self.scale)
            x0, y0 = m_left, m_top
            x1, y1 = x0 + w_px, y0 + h_px

            # Desenho da Pedra
            draw.rectangle([x0, y0, x1, y1], fill="#f5f5f5", outline="black", width=3)

            # Cotas e Medidas
            draw.line([x0, y0-60, x1, y0-60], fill="black", width=2)
            draw.text((x0 + w_px/2 - 30, y0-95), f"{peca.largura}m", fill="black")
            draw.line([x0-60, y0, x0-60, y1], fill="black", width=2)
            draw.text((x0-120, y0 + h_px/2 - 10), f"{peca.profundidade}m", fill="black")

            # Aberturas e Eixos (Igual à imagem enviada)
            for ab in peca.aberturas:
                ab_w = int(ab.largura * self.scale)
                ab_h = int(ab.profundidade * self.scale)
                ab_x = x0 + int(w_px * ab.x_relativo) - (ab_w // 2)
                ab_y = y0 + int(h_px * ab.y_relativo) - (ab_h // 2)
                draw.rectangle([ab_x, ab_y, ab_x + ab_w, ab_y + ab_h], outline="red", width=2)
                draw.line([ab_x + ab_w/2, y0-120, ab_x + ab_w/2, y1+40], fill="blue", width=2)
                draw.text((ab_x + ab_w/2 - 25, y0-150), "EIXO", fill="blue")

            # Acabamentos
            if peca.saia: draw.line([x0, y1, x1, y1], fill="blue", width=8)
            if peca.rodobanca: draw.line([x0, y0, x1, y0], fill="red", width=6)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return ft.Image(src_base64=img_str, width=500, height=350, fit=ft.ImageFit.CONTAIN)