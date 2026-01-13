import flet as ft
import flet.canvas as cv
from src.views.components.budget_composition import CompositionManager

class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.scale = 180  # Escala aumentada para melhor visibilidade no mobile
        self.padding = 50

    def build(self):
        shapes = []
        x_off, y_off = self.padding, self.padding

        for peca in self.composition.pecas:
            w_px = peca.largura * self.scale
            h_px = peca.profundidade * self.scale

            # 1. CORPO DA PEDRA
            shapes.append(cv.Rect(x_off, y_off, w_px, h_px, paint=ft.Paint(color="#e0e0e0", style="fill")))
            shapes.append(cv.Rect(x_off, y_off, w_px, h_px, paint=ft.Paint(color="black", stroke_width=1, style="stroke")))

            # 2. DESENHO DAS ABERTURAS (Bojo/Cooktop)
            for ab in peca.aberturas:
                ab_w = ab.largura * self.scale
                ab_h = ab.profundidade * self.scale
                # Posicionamento centralizado simplificado ou via offset
                ab_x = x_off + (w_px - ab_w) / 2 
                ab_y = y_off + (h_px - ab_h) / 2
                
                # Retângulo tracejado para o furo
                shapes.append(cv.Rect(ab_x, ab_y, ab_w, ab_h, border_radius=2,
                    paint=ft.Paint(color="red", stroke_width=1.5, style="stroke", stroke_dash_pattern=[5, 5])))
                shapes.append(cv.Text(ab_x + 5, ab_y + 5, ab.tipo.upper(), size=9, color="red"))

            # 3. ACABAMENTOS POR LADO (SAIA)
            if peca.saia:
                paint_saia = ft.Paint(color=ft.colors.BLUE_700, stroke_width=4)
                if "frente" in peca.saia.lados:
                    shapes.append(cv.Line(x_off, y_off + h_px, x_off + w_px, y_off + h_px, paint_saia))
                if "fundo" in peca.saia.lados:
                    shapes.append(cv.Line(x_off, y_off, x_off + w_px, y_off, paint_saia))
                if "esquerda" in peca.saia.lados:
                    shapes.append(cv.Line(x_off, y_off, x_off, y_off + h_px, paint_saia))
                if "direita" in peca.saia.lados:
                    shapes.append(cv.Line(x_off + w_px, y_off, x_off + w_px, y_off + h_px, paint_saia))

            # 4. RODOBANCAS (INDICADAS POR LINHA DUPLA OU COR DIFERENTE)
            if peca.rodobanca:
                paint_rodo = ft.Paint(color=ft.colors.RED_700, stroke_width=3)
                if "fundo" in peca.rodobanca.lados:
                    shapes.append(cv.Line(x_off, y_off-3, x_off + w_px, y_off-3, paint_rodo))
                if "esquerda" in peca.rodobanca.lados:
                    shapes.append(cv.Line(x_off-3, y_off, x_off-3, y_off + h_px, paint_rodo))

            # 5. COTAS (MEDIDAS)
            shapes.append(cv.Text(x_off + w_px/2 - 15, y_off - 20, f"{peca.largura}m", weight="bold"))
            shapes.append(cv.Text(x_off - 40, y_off + h_px/2 - 10, f"{peca.profundidade}m", weight="bold"))

        return cv.Canvas(shapes=shapes, width=500, height=300)