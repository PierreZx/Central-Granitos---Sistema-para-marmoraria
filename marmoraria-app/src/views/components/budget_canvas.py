# src/views/components/budget_canvas.py

import flet as ft
import io
from PIL import Image, ImageDraw, ImageFont
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.width = 800
        self.height = 600
        self.scale = 200 # 1 metro = 200 pixels

    def build(self):
        # Criamos uma imagem em branco (RGB) com fundo branco
        img = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(img)
        
        # Tenta carregar uma fonte, se não houver, usa a padrão
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

        margin_x, margin_y = 100, 150

        for peca in self.composition.pecas:
            w = peca.largura * self.scale
            h = peca.profundidade * self.scale
            
            x0, y0 = margin_x, margin_y
            x1, y1 = x0 + w, y0 + h

            # 1. DESENHO DA PEDRA (CORPO)
            draw.rectangle([x0, y0, x1, y1], fill="#E0E0E0", outline="black", width=2)

            # 2. ACABAMENTOS (SAIA EM AZUL)
            if peca.saia and peca.saia.lados:
                if "frente" in peca.saia.lados:
                    draw.line([x0, y1, x1, y1], fill="blue", width=5)

            # 3. RODOBANCAS (PAREDE EM VERMELHO)
            if peca.rodobanca and peca.rodobanca.lados:
                if "fundo" in peca.rodobanca.lados:
                    draw.line([x0, y0-2, x1, y0-2], fill="red", width=3)

            # 4. ABERTURAS (BOJO / COOKTOP)
            for ab in peca.aberturas:
                ab_w = ab.largura * self.scale
                ab_h = ab.profundidade * self.scale
                ab_x = x0 + (w * ab.x_relativo) - (ab_w / 2)
                ab_y = y0 + (h * ab.y_relativo) - (ab_h / 2)
                
                # Desenha o furo (tracejado simulado)
                draw.rectangle([ab_x, ab_y, ab_x + ab_w, ab_y + ab_h], outline="red", width=2)
                
                # LINHA DE EIXO (Igual à imagem base)
                draw.line([ab_x + ab_w/2, y0 - 40, ab_x + ab_w/2, y1 + 20], fill="blue", width=1)
                draw.text((ab_x + ab_w/2 - 15, y0 - 60), "EIXO", fill="blue", font=font_small)

            # 5. COTAS (MEDIDAS)
            # Largura
            draw.line([x0, y0 - 20, x1, y0 - 20], fill="black", width=1)
            draw.text((x0 + w/2 - 20, y0 - 45), f"{peca.largura}m", fill="black", font=font)
            
            # Profundidade
            draw.line([x0 - 20, y0, x0 - 20, y1], fill="black", width=1)
            draw.text((x0 - 70, y0 + h/2 - 10), f"{peca.profundidade}m", fill="black", font=font)

        # Converter imagem PIL para Bytes para o Flet exibir
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = buffered.getvalue()

        return ft.Image(
            src_base64=buffered.getvalue().hex(), # Método simples de conversão
            src=None,
            width=self.width / 2, # Ajuste de escala para tela
            height=self.height / 2,
            fit=ft.ImageFit.CONTAIN,
        )