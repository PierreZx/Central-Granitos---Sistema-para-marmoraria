import flet as ft
from src.config import COLOR_PRIMARY, COLOR_TEXT

class Sidebar(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.bgcolor = ft.colors.WHITE 

    def navegar(self, e):
        rota = e.control.data
        self.page.go(rota)

    def build(self):
        # Definição dos botões do menu
        return ft.Container(
            width=250,
            bgcolor=ft.colors.WHITE,
            padding=20,
            border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.GREY_200)),
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.DASHBOARD_CUSTOMIZE, color=COLOR_PRIMARY, size=30),
                        ft.Text("Central", size=22, weight="bold", color=COLOR_PRIMARY)
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Divider(),
                
                # Itens do Menu
                self.criar_item_menu("Dashboard", ft.icons.DASHBOARD, "/dashboard"),
                self.criar_item_menu("Estoque", ft.icons.INVENTORY_2, "/estoque"),
                self.criar_item_menu("Orçamentos", ft.icons.REQUEST_QUOTE, "/orcamentos"),
                self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING, "/producao"),
                self.criar_item_menu("Financeiro", ft.icons.ATTACH_MONEY, "/financeiro"),
                
                ft.Divider(),
                ft.Container(expand=True), # Espaçador
                self.criar_item_menu("Sair", ft.icons.LOGOUT, "/", cor_icone=ft.colors.RED),
            ])
        )

    def criar_item_menu(self, texto, icone, rota, cor_icone=None):
        if cor_icone is None:
            cor_icone = ft.colors.GREY_600
            
        estilo_botao = ft.ButtonStyle(
            color=ft.colors.GREY_700,
            bgcolor={ft.MaterialState.HOVERED: ft.colors.BLUE_50},
            shape=ft.RoundedRectangleBorder(radius=10),
            # REMOVIDO: alignment=ft.alignment.center_left (Não existe na v0.22.1)
        )
        
        # Destaca o item se for a rota atual
        if self.page.route == rota:
            estilo_botao = ft.ButtonStyle(
                color=COLOR_PRIMARY,
                bgcolor=ft.colors.BLUE_50,
                shape=ft.RoundedRectangleBorder(radius=10),
                # REMOVIDO: alignment=ft.alignment.center_left
            )
            cor_icone = COLOR_PRIMARY

        return ft.Container(
            content=ft.TextButton(
                content=ft.Row([
                    ft.Icon(icone, size=20, color=cor_icone),
                    ft.Text(texto, size=16)
                ], spacing=15),
                style=estilo_botao,
                on_click=self.navegar,
                data=rota,
                width=210,
                height=50
            ),
            padding=ft.padding.only(bottom=5)
        )