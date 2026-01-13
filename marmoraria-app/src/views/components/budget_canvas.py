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
        # Resolução interna alta para garantir nitidez no telemóvel
        self.canvas_w = 1500 
        self.canvas_h = 1000
        self.scale = 450  # 1 metro = 450 pixels

    def build(self):
        # Se não houver peças, retorna um container vazio
        if not self.composition.pecas:
            return ft.Container(height=100)

        # Criar imagem com fundo branco
        img = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        draw = ImageDraw.Draw(img)
        
        # Tentar carregar uma fonte mais legível, se falhar usa a padrão
        try:
            # Em alguns sistemas o caminho pode variar, o default resolve
            font_grande = ImageFont.load_default() 
            font_eixo = ImageFont.load_default()
        except:
            font_grande = ImageFont.load_default()
            font_eixo = ImageFont.load_default()

        # Margens para as cotas não cortarem
        offset_x, offset_y = 250, 250

        for peca in self.composition.pecas:
            w_px = int(peca.largura * self.scale)
            h_px = int(peca.profundidade * self.scale)
            
            x0, y0 = offset_x, offset_y
            x1, y1 = x0 + w_px, y0 + h_px

            # 1. DESENHO DO CORPO DA PEDRA
            # Cinza muito claro com borda preta sólida
            draw.rectangle([x0, y0, x1, y1], fill="#F9F9F9", outline="black", width=4)

            # 2. COTAS EXTERNAS (Medidas da Pedra)
            # Cota de Largura (Superior)
            draw.line([x0, y0 - 80, x1, y0 - 80], fill="black", width=2) # Linha horizontal
            draw.line([x0, y0 - 95, x0, y0 - 65], fill="black", width=2) # Traço esquerdo
            draw.line([x1, y0 - 95, x1, y0 - 65], fill="black", width=2) # Traço direito
            draw.text((x0 + w_px/2 - 40, y0 - 130), f"{peca.largura:.2f} m", fill="black")

            # Cota de Profundidade (Esquerda)
            draw.line([x0 - 80, y0, x0 - 80, y1], fill="black", width=2) # Linha vertical
            draw.line([x0 - 95, y0, x0 - 65, y0], fill="black", width=2) # Traço topo
            draw.line([x0 - 95, y1, x0 - 65, y1], fill="black", width=2) # Traço base
            draw.text((x0 - 200, y0 + h_px/2 - 10), f"{peca.profundidade:.2f} m", fill="black")

            # 3. ACABAMENTOS (SAIA E RODOBANCA)
            # Saia: Azul Escuro (Geralmente bordas externas)
            if peca.saia:
                p_saia = peca.saia.lados
                if "frente" in p_saia: draw.line([x0, y1, x1, y1], fill="#0000FF", width=12)
                if "esquerda" in p_saia: draw.line([x0, y0, x0, y1], fill="#0000FF", width=12)
                if "direita" in p_saia: draw.line([x1, y0, x1, y1], fill="#0000FF", width=12)
                if "fundo" in p_saia: draw.line([x0, y0, x1, y0], fill="#0000FF", width=12)

            # Rodobanca: Vermelho (Geralmente encostado à parede)
            if peca.rodobanca:
                p_rodo = peca.rodobanca.lados
                if "fundo" in p_rodo: draw.line([x0, y0, x1, y0], fill="#FF0000", width=8)
                if "esquerda" in p_rodo: draw.line([x0, y0, x0, y1], fill="#FF0000", width=8)
                if "direita" in p_rodo: draw.line([x1, y0, x1, y1], fill="#FF0000", width=8)
                if "frente" in p_rodo: draw.line([x0, y1, x1, y1], fill="#FF0000", width=8)

            # 4. ABERTURAS (BOJO / COOKTOP) COM EIXO
            for ab in peca.aberturas:
                ab_w_px = int(ab.largura * self.scale)
                ab_h_px = int(ab.profundidade * self.scale)
                
                # Ponto central (eixo) baseado na distância da esquerda e do fundo
                centro_x = x0 + int(ab.distancia_esquerda * self.scale)
                centro_y = y0 + int(ab.distancia_fundo * self.scale)
                
                # Caixa do Furo (Tracejado Vermelho ou sólido fino)
                ax0, ay0 = centro_x - ab_w_px//2, centro_y - ab_h_px//2
                ax1, ay1 = ax0 + ab_w_px, ay0 + ab_h_px
                draw.rectangle([ax0, ay0, ax1, ay1], outline="red", width=3)
                
                # LINHA DE EIXO (Azul - Identificando o centro para o pedreiro/marmorista)
                # Linha vertical cruzando a peça
                draw.line([centro_x, y0 - 150, centro_x, y1 + 50], fill="blue", width=2)
                draw.text((centro_x - 30, y0 - 180), "EIXO", fill="blue")

        # CONVERSÃO FINAL PARA FLET (Base64)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return ft.Container(
            content=ft.Image(
                src_base64=img_str,
                fit=ft.ImageFit.CONTAIN,
                border_radius=10,
            ),
            alignment=ft.alignment.center,
            padding=10,
            expand=True
        )