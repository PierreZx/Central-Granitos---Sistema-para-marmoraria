import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY

def FinancialView(page: ft.Page):
    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Text("Controle Financeiro", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Fluxo de caixa, entradas e saídas", color=ft.Colors.GREY_600),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ATTACH_MONEY, size=60, color=ft.Colors.GREY_300),
                    ft.Text("Módulo Financeiro em Construção", color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        ])
    )

    return ft.View(
        route="/financeiro",
        padding=0,
        controls=[
            ft.Row([Sidebar(page), conteudo], expand=True)
        ]
    )