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
        # Verifica quem está logado
        user_role = self.page.session.get("user_role")
        
        # Lista de itens do menu
        menu_items = []
        
        if user_role == "producao":
            # MENU RESTRITO DA PRODUÇÃO
            menu_items.append(self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING, "/producao"))
        else:
            # MENU COMPLETO (ADMIN)
            menu_items.append(self.criar_item_menu("Dashboard", ft.icons.DASHBOARD, "/dashboard"))
            menu_items.append(self.criar_item_menu("Estoque", ft.icons.INVENTORY_2, "/estoque"))
            menu_items.append(self.criar_item_menu("Orçamentos", ft.icons.REQUEST_QUOTE, "/orcamentos"))
            menu_items.append(self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING, "/producao"))
            menu_items.append(self.criar_item_menu("Financeiro", ft.icons.ATTACH_MONEY, "/financeiro"))

        return ft.Container(
            width=250,
            bgcolor=ft.colors.WHITE,
            padding=20,
            border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.GREY_200)),
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        # Logo pequena
                        ft.Image(src="logo.jpg", width=40, height=40, fit=ft.ImageFit.CONTAIN),
                        ft.Text("Central", size=22, weight="bold", color=COLOR_PRIMARY)
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Divider(),
                
                # Renderiza os itens permitidos
                ft.Column(menu_items, spacing=5),
                
                ft.Divider(),
                ft.Container(expand=True), # Espaçador para jogar o Sair pro fundo
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
        )
        
        # Destaca o item se for a rota atual
        if self.page.route == rota:
            estilo_botao = ft.ButtonStyle(
                color=COLOR_PRIMARY,
                bgcolor=ft.colors.BLUE_50,
                shape=ft.RoundedRectangleBorder(radius=10),
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