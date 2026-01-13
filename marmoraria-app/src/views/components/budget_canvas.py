# src/views/components/budget_canvas.py
import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        # Escala ajustada para o ecrã do telemóvel (1 metro = 150 pixels)
        self.scale = 150 

    def build(self):
        shapes = []
        
        # Se não houver peças configuradas, não desenha nada
        if not self.composition.pecas:
            return ft.Container(height=100)

        # Para esta versão, focamos na peça principal (índice 0)
        p = self.composition.pecas[0]
        
        # Ponto de origem do desenho (margem para as cotas aparecerem)
        x0, y0 = 60, 60
        w_px = p.largura * self.scale
        h_px = p.profundidade * self.scale

        # --- 1. CORPO DA PEDRA ---
        # Preenchimento cinza claro (pedra)
        shapes.append(
            cv.Rect(x0, y0, w_px, h_px, paint=ft.Paint(color="#E8E8E8", style=ft.PaintingStyle.FILL))
        )
        # Contorno sólido preto
        shapes.append(
            cv.Rect(x0, y0, w_px, h_px, paint=ft.Paint(color="black", stroke_width=2, style=ft.PaintingStyle.STROKE))
        )

        # --- 2. ACABAMENTOS POR LADO (SAIA - AZUL) ---
        # Desenha uma linha azul grossa apenas nos lados selecionados
        if p.saia:
            paint_saia = ft.Paint(color="blue", stroke_width=6)
            if "frente" in p.saia.lados:
                shapes.append(cv.Line(x0, y0 + h_px, x0 + w_px, y0 + h_px, paint_saia))
            if "fundo" in p.saia.lados:
                shapes.append(cv.Line(x0, y0, x0 + w_px, y0, paint_saia))
            if "esquerda" in p.saia.lados:
                shapes.append(cv.Line(x0, y0, x0, y0 + h_px, paint_saia))
            if "direita" in p.saia.lados:
                shapes.append(cv.Line(x0 + w_px, y0, x0 + w_px, y0 + h_px, paint_saia))

        # --- 3. ACABAMENTOS POR LADO (RODOBANCA - VERMELHO) ---
        # Desenha uma linha vermelha nos lados selecionados (parede)
        if p.rodobanca:
            paint_rodo = ft.Paint(color="red", stroke_width=4)
            if "fundo" in p.rodobanca.lados:
                shapes.append(cv.Line(x0, y0 - 3, x0 + w_px, y0 - 3, paint_rodo))
            if "esquerda" in p.rodobanca.lados:
                shapes.append(cv.Line(x0 - 3, y0, x0 - 3, y0 + h_px, paint_rodo))
            if "direita" in p.rodobanca.lados:
                shapes.append(cv.Line(x0 + w_px + 3, y0, x0 + w_px + 3, y0 + h_px, paint_rodo))

        # --- 4. FUROS TÉCNICOS COM LINHA DE EIXO ---
        # Implementa as aberturas (Bojo/Cooktop) com eixos azuis
        for ab in p.aberturas:
            ab_w_px = ab.largura * self.scale
            ab_h_px = ab.profundidade * self.scale
            # Posição central baseada nos eixos definidos
            centro_x = x0 + (ab.distancia_esquerda * self.scale)
            centro_y = y0 + (ab.distancia_fundo * self.scale)
            
            # Caixa do furo (Tracejado vermelho)
            ax0, ay0 = centro_x - ab_w_px/2, centro_y - ab_h_px/2
            shapes.append(
                cv.Rect(ax0, ay0, ab_w_px, ab_h_px, 
                       paint=ft.Paint(color="red", stroke_width=1.5, style=ft.PaintingStyle.STROKE))
            )
            
            # Linha de Eixo (Azul tracejada - Padrão técnico)
            shapes.append(
                cv.Line(centro_x, y0 - 30, centro_x, y0 + h_px + 20, 
                       paint=ft.Paint(color="blue", stroke_width=1))
            )
            shapes.append(
                cv.Text(centro_x - 15, y0 - 50, "EIXO", style=ft.TextStyle(size=9, color="blue"))
            )

        # --- 5. COTAS DE MEDIDA (LARGURA E PROFUNDIDADE) ---
        # Texto com as medidas totais da peça
        shapes.append(
            cv.Text(x0 + w_px/2 - 20, y0 - 35, f"{p.largura}m", style=ft.TextStyle(size=12, weight="bold"))
        )
        shapes.append(
            cv.Text(x0 - 50, y0 + h_px/2 - 10, f"{p.profundidade}m", style=ft.TextStyle(size=12, weight="bold"))
        )

        return ft.Container(
            content=cv.Canvas(shapes=shapes, width=450, height=350),
            alignment=ft.alignment.center,
            padding=10,
        )