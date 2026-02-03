import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_PRIMARY,
    COLOR_WHITE,
    COLOR_SECONDARY,
    COLOR_TEXT
)
from src.services import firebase_service


def ProductionView(page: ft.Page):

    conteudo_dinamico = ft.Container(expand=True)

    # ======================================================
    # ================== DESENHO DAS PEÇAS =================
    # ======================================================

    def desenhar_explosao(canvas, item):
        canvas.shapes.clear()

        pecas = item.get("pecas") or {}
        furos = item.get("furos") or {}

        if not pecas:
            return

        w1 = float(pecas.get("p1", {}).get("l", 0))
        h1 = float(pecas.get("p1", {}).get("p", 0))

        w2 = float(pecas.get("p2", {}).get("l", 0)) if "p2" in pecas else 0
        w3 = float(pecas.get("p3", {}).get("l", 0)) if "p3" in pecas else 0

        total_w = w1 + w2 + w3
        max_h = max(
            h1,
            float(pecas.get("p2", {}).get("p", 0)) if "p2" in pecas else 0,
            float(pecas.get("p3", {}).get("p", 0)) if "p3" in pecas else 0,
        )

        W, H = 300, 150
        scale = min((W - 40) / max(0.1, total_w), (H - 30) / max(0.1, max_h))

        x = (W - total_w * scale) / 2
        y = (H - h1 * scale) / 2

        def draw(w, h, px, py, nome, p1=False):
            wp, hp = w * scale, h * scale

            canvas.shapes.append(
                ft.canvas.Rect(
                    px, py, wp, hp,
                    paint=ft.Paint(
                        color=COLOR_PRIMARY,
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=2
                    )
                )
            )

            canvas.shapes.append(
                ft.canvas.Text(
                    px + 5,
                    py - 14,
                    f"{nome}: {w}x{h}",
                    style=ft.TextStyle(size=9, weight="bold", color=COLOR_TEXT)
                )
            )

            if p1:
                if furos.get("bojo", {}).get("check"):
                    canvas.shapes.append(
                        ft.canvas.Rect(
                            px + wp * 0.3,
                            py + hp * 0.2,
                            wp * 0.4,
                            hp * 0.6,
                            paint=ft.Paint(
                                color=ft.Colors.RED_400,
                                style=ft.PaintingStyle.STROKE
                            )
                        )
                    )

                if furos.get("cooktop", {}).get("check"):
                    canvas.shapes.append(
                        ft.canvas.Rect(
                            px + wp * 0.6,
                            py + hp * 0.2,
                            wp * 0.3,
                            hp * 0.5,
                            paint=ft.Paint(
                                color=ft.Colors.BLUE_400,
                                style=ft.PaintingStyle.STROKE
                            )
                        )
                    )

        if "p2" in pecas and pecas["p2"].get("lado") == "esquerda":
            draw(w2, float(pecas["p2"]["p"]), x, y, "P2")
            x += w2 * scale

        draw(w1, h1, x, y, "P1", p1=True)
        x += w1 * scale

        for k in ("p2", "p3"):
            if k in pecas and pecas[k].get("lado") == "direita":
                draw(
                    float(pecas[k]["l"]),
                    float(pecas[k]["p"]),
                    x,
                    y,
                    k.upper()
                )
                x += float(pecas[k]["l"]) * scale

        canvas.update()

    # ======================================================
    # =================== VISUALIZADOR =====================
    # ======================================================

    def abrir_visualizador(orc):
        itens = orc.get("itens") or []

        lista = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=15)

        for item in itens:
            canvas = ft.canvas.Canvas(width=300, height=150)

            lista.controls.append(
                ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10,
                    content=ft.Column([
                        ft.Text(item.get("nome", "Peça"), weight="bold"),
                        canvas
                    ])
                )
            )

            desenhar_explosao(canvas, item)

        dlg = ft.AlertDialog(
            title=ft.Text(f"O.S. - {orc.get('cliente_nome', '')}"),
            content=ft.Container(content=lista, width=450, height=600),
            actions=[
                ft.ElevatedButton(
                    "Fechar",
                    bgcolor=COLOR_PRIMARY,
                    color=COLOR_WHITE,
                    on_click=lambda e: page.close(dlg)
                )
            ]
        )

        page.open(dlg)

    # ======================================================
    # ==================== COLUNAS =========================
    # ======================================================

    def render_coluna(status_firebase, titulo, cor):
        orcs = firebase_service.get_orcamentos_by_status(status_firebase)
        grid = ft.ResponsiveRow(spacing=20, run_spacing=20)

        if not orcs:
            return ft.Container(
                padding=50,
                alignment=ft.alignment.center,
                content=ft.Text("Nenhum pedido nesta fase")
            )

        for orc in orcs:
            grid.controls.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    padding=20,
                    bgcolor=COLOR_WHITE,
                    border_radius=15,
                    content=ft.Column([
                        ft.Text(orc.get("cliente_nome", ""), weight="bold", size=18),
                        ft.Text(titulo, color=cor),
                        ft.ElevatedButton(
                            "VER O.S.",
                            bgcolor=COLOR_SECONDARY,
                            color=COLOR_WHITE,
                            on_click=lambda e, o=orc: abrir_visualizador(o)
                        )
                    ], spacing=10)
                )
            )

        return grid

    # ======================================================
    # ===================== TABS ===========================
    # ======================================================

    STATUS = [
        ("PENDENTE", "Fila de Espera", ft.Colors.ORANGE_700),
        ("PRODUZINDO", "Na Bancada", ft.Colors.BLUE_700),
        ("PRONTO", "Concluídos", ft.Colors.GREEN_700),
    ]

    def mudar_aba(e):
        s, t, c = STATUS[e.control.selected_index]
        conteudo_dinamico.content = render_coluna(s, t, c)
        page.update()

    conteudo_dinamico.content = render_coluna(*STATUS[0])

    layout = ft.Column([
        ft.Tabs(
            selected_index=0,
            on_change=mudar_aba,
            tabs=[
                ft.Tab(text="Fila de Espera"),
                ft.Tab(text="Na Bancada"),
                ft.Tab(text="Concluídos"),
            ]
        ),
        conteudo_dinamico
    ], expand=True)

    return LayoutBase(
        page,
        layout,
        titulo="Área de Produção",
        subtitulo="Gestão de Ordens de Serviço"
    )
