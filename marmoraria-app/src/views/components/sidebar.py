import flet as ft
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TEXT

class Sidebar(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.width = 250  # Largura fixa para Desktop
        self.bgcolor = ft.colors.WHITE
        self.padding = 20
        self.border_right = ft.border.only(right=ft.BorderSide(1, ft.colors.GREY_300))
        
        # Conteúdo do Menu
        self.content = ft.Column(
            controls=[
                # Cabeçalho do Menu com Logo Pequena
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DIAMOND, color=COLOR_PRIMARY),
                        ft.Text("CENTRAL", weight="bold", size=20, color=COLOR_TEXT)
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                ft.Divider(),

                # Botões de Navegação
                self.criar_botao("Dashboard", ft.Icons.DASHBOARD, "/dashboard"),
                self.criar_botao("Estoque", ft.Icons.INVENTORY_2, "/estoque"),
                self.criar_botao("Orçamentos", ft.Icons.REQUEST_QUOTE, "/orcamentos"),
                self.criar_botao("Produção", ft.Icons.PRECISION_MANUFACTURING, "/producao"),
                self.criar_botao("Financeiro", ft.Icons.ATTACH_MONEY, "/financeiro"),
                
                ft.Divider(),
                
                self.criar_botao("Sair", ft.Icons.EXIT_TO_APP, "/", is_logout=True),
            ]
        )

    def criar_botao(self, text, icon, route, is_logout=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=COLOR_SECONDARY if not is_logout else ft.colors.RED),
                ft.Text(text, size=16, color=COLOR_TEXT if not is_logout else ft.colors.RED)
            ]),
            padding=10,
            border_radius=10,
            on_click=lambda e: self.navegar(route),
            ink=True, # Efeito de clique
        )

    def navegar(self, route):
        self.page.go(route)