import flet as ft
import flet.canvas as cv

from src.views.components.budget_composition import BancadaPiece, CompositionManager


class BudgetCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition

        self.canvas_width = 500
        self.canvas_height = 320

        self.margin = 20
        self.scale = 100  # 1 metro = 100px (ajustado dinamicamente)

    def build(self):
        return ft.Column(
            spacing=10,
            controls=[
                ft.Text("Vista superior (planta)", weight="bold"),
                self._build_top_view(),
                ft.Divider(),
                ft.Text("Vista lateral (saia / rodobanca)", weight="bold"),
                self._build_side_view(),
            ]
        )

    # =========================
    # VISTA SUPERIOR
    # =========================
    def _build_top_view(self):
        shapes = []

        x_cursor = self.margin
        y_cursor = self.margin

        for p in self.composition.pecas:
            w = p.largura * self.scale
            d = p.profundidade * self.scale

            # Bancada
            shapes.append(
                cv.Rect(
                    x_cursor,
                    y_cursor,
                    w,
                    d,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=2,
                        color=ft.colors.BLACK
                    )
                )
            )

            # Medidas
            shapes.append(self._text(f"{p.largura:.2f} m", x_cursor + w / 2 - 18, y_cursor - 14))
            shapes.append(self._text(f"{p.profundidade:.2f} m", x_cursor - 45, y_cursor + d / 2 - 6))

            # Próxima peça (encaixe simples visual)
            x_cursor += w + 10

        return cv.Canvas(
            width=self.canvas_width,
            height=self.canvas_height,
            shapes=shapes
        )

    # =========================
    # VISTA LATERAL
    # =========================
    def _build_side_view(self):
        shapes = []

        x_cursor = self.margin
        base_y = self.canvas_height - self.margin

        for p in self.composition.pecas:
            largura_px = p.largura * self.scale
            espessura = 20  # espessura visual da pedra

            # Pedra
            shapes.append(
                cv.Rect(
                    x_cursor,
                    base_y - espessura,
                    largura_px,
                    espessura,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.FILL,
                        color=ft.colors.GREY_300
                    )
                )
            )

            # Saia
            if getattr(p, "saia", None):
                saia_px = p.saia.altura * self.scale
                shapes.append(
                    cv.Rect(
                        x_cursor,
                        base_y,
                        largura_px,
                        saia_px,
                        paint=ft.Paint(
                            style=ft.PaintingStyle.STROKE,
                            stroke_width=2,
                            color=ft.colors.BLACK
                        )
                    )
                )
                shapes.append(
                    self._text(f"Saia {p.saia.altura:.2f} m", x_cursor + 5, base_y + saia_px / 2 - 6)
                )

            # Rodobanca
            if getattr(p, "rodobanca", None):
                rb_px = p.rodobanca.altura * self.scale
                shapes.append(
                    cv.Rect(
                        x_cursor,
                        base_y - espessura - rb_px,
                        largura_px,
                        rb_px,
                        paint=ft.Paint(
                            style=ft.PaintingStyle.STROKE,
                            stroke_width=2,
                            color=ft.colors.BLACK
                        )
                    )
                )
                shapes.append(
                    self._text(
                        f"Rodobanca {p.rodobanca.altura:.2f} m",
                        x_cursor + 5,
                        base_y - espessura - rb_px / 2 - 6
                    )
                )

            x_cursor += largura_px + 10

        return cv.Canvas(
            width=self.canvas_width,
            height=self.canvas_height,
            shapes=shapes
        )

    # =========================
    # TEXTO AUXILIAR
    # =========================
    def _text(self, value, x, y):
        return cv.Text(
            x=x,
            y=y,
            text=value,
            style=ft.TextStyle(size=10),
            color=ft.colors.BLACK
        )
