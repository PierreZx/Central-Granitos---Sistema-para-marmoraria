import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY

def BudgetView(page: ft.Page):
    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Text("Gestão de Orçamentos", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Crie e gerencie propostas para clientes", color=ft.Colors.GREY_600),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.REQUEST_QUOTE, size=60, color=ft.Colors.GREY_300),
                    ft.Text("Módulo de Orçamentos em Construção", color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        ])
    )

    return ft.View(
        route="/orcamentos",
        padding=0,
        controls=[
            ft.Row([Sidebar(page), conteudo], expand=True)
        ]
    )