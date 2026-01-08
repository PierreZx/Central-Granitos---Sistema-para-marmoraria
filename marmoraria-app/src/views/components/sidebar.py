import flet as ft
from src.config import COLOR_PRIMARY, COLOR_TEXT

class Sidebar(ft.Container):
    def __init__(self, page, is_mobile=False):
        super().__init__()
        self.page = page
        
        if is_mobile:
            self.width = None
            self.expand = True
            self.bgcolor = ft.colors.WHITE
            padding_bottom = 20
        else:
            self.width = 280
            self.expand = True 
            self.bgcolor = ft.colors.WHITE
            self.border = ft.border.only(right=ft.border.BorderSide(1, "#00000008"))
            self.shadow = ft.BoxShadow(blur_radius=20, spread_radius=-5, color="#00000005", offset=ft.Offset(5, 0))
            padding_bottom = 5
        
        self.padding = ft.padding.only(left=20, right=20, top=20, bottom=padding_bottom)
        user_role = self.page.session.get("user_role")
        
        logo = ft.Row([
            ft.Container(
                width=40, height=40, border_radius=10, bgcolor=COLOR_PRIMARY,
                content=ft.Icon(ft.icons.PRECISION_MANUFACTURING_ROUNDED, color=ft.colors.WHITE, size=20)
            ),
            ft.Text("CENTRAL", size=20, weight="bold", color=COLOR_PRIMARY, letter_spacing=1),
        ], spacing=12)

        menu_items = []
        if user_role == "admin":
            menu_items = [
                self.criar_item_menu("Dashboard", ft.icons.DASHBOARD_ROUNDED, "/dashboard"),
                self.criar_item_menu("Estoque", ft.icons.INVENTORY_2_ROUNDED, "/estoque"),
                self.criar_item_menu("Orçamentos", ft.icons.DESCRIPTION_ROUNDED, "/orcamentos"),
                self.criar_item_menu("Financeiro", ft.icons.PAYMENTS_ROUNDED, "/financeiro"),
                self.criar_item_menu("Produção", ft.icons.CHAIR_ALT_ROUNDED, "/producao"),
            ]
        elif user_role == "producao":
            menu_items = [
                self.criar_item_menu("Produção", ft.icons.CHAIR_ALT_ROUNDED, "/producao"),
            ]

        rodape = self.criar_item_menu("Sair", ft.icons.LOGOUT_ROUNDED, "/login", estilo="danger")

        self.content = ft.Column(
            [
                logo,
                ft.Container(height=20),
                ft.Column(menu_items, spacing=8, expand=True),
                ft.Divider(color="#00000008"),
                rodape
            ], 
            spacing=0, 
            expand=True
        )

    def navegar(self, e):
        rota = e.control.data
        if self.page.drawer:
            self.page.drawer.open = False
        self.page.go(rota)

    def criar_item_menu(self, texto, icone, rota, cor_icone=None, estilo="normal"):
        cor_base = ft.colors.GREY_700 if estilo != "danger" else ft.colors.RED_600
        esta_ativo = self.page.route == rota
        
        return ft.Container(
            content=ft.TextButton(
                content=ft.Row([
                    ft.Icon(icone, size=22, color=COLOR_PRIMARY if esta_ativo else cor_base),
                    ft.Text(texto, size=15, weight=ft.FontWeight.W_500 if esta_ativo else ft.FontWeight.W_400),
                ], spacing=12),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    color=COLOR_PRIMARY if esta_ativo else cor_base,
                    bgcolor="#6A1B1B10" if esta_ativo else "transparent",
                ),
                data=rota,
                on_click=self.navegar
            ),
            margin=ft.margin.only(bottom=2)
        )