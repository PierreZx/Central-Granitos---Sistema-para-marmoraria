import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY

def ProductionView(page: ft.Page):
    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Text("Linha de Produção", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Acompanhe o status de corte e acabamento", color=ft.Colors.GREY_600),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PRECISION_MANUFACTURING, size=60, color=ft.Colors.GREY_300),
                    ft.Text("Módulo de Produção em Construção", color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        ])
    )

    return ft.View(
        route="/producao",
        padding=0,
        controls=[
            ft.Row([Sidebar(page), conteudo], expand=True)
        ]
    )