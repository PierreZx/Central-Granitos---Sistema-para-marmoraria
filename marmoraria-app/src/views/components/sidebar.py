import flet as ft
from src.config import COLOR_PRIMARY, COLOR_TEXT, COLOR_WHITE


class Sidebar(ft.Container):
    def __init__(self, page: ft.Page, is_mobile: bool = False):
        super().__init__()

        self.page = page

        # =========================
        # CONFIGURAÇÃO BASE
        # =========================
        self.bgcolor = COLOR_WHITE
        self.padding = 20

        if not is_mobile:
            self.width = 260
            self.border = ft.border.only(
                right=ft.BorderSide(1, "#F0F0F0")
            )

        # Papel do usuário
        user_role = getattr(self.page, "user_role", None)

        # =========================
        # LOGO / CABEÇALHO
        # =========================
        logo = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=38,
                        height=38,
                        border_radius=10,
                        bgcolor=COLOR_PRIMARY,
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            ft.Icons.PRECISION_MANUFACTURING,
                            color=COLOR_WHITE,
                            size=20,
                        ),
                    ),
                    ft.Text(
                        "CENTRAL",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_PRIMARY,
                    ),
                ],
                spacing=12,
            ),
            margin=ft.margin.only(bottom=30, left=5),
        )

        # =========================
        # ITENS DE MENU
        # =========================
        if user_role == "admin":
            menu_items = [
                self.criar_item_menu("Dashboard", ft.Icons.GRID_VIEW, "/dashboard"),
                self.criar_item_menu("Estoque", ft.Icons.INVENTORY_2, "/estoque"),
                self.criar_item_menu("Orçamentos", ft.Icons.RECEIPT_LONG, "/orcamentos"),
                self.criar_item_menu(
                    "Financeiro",
                    ft.Icons.ACCOUNT_BALANCE_WALLET,
                    "/financeiro",
                ),
                self.criar_item_menu(
                    "Produção",
                    ft.Icons.PRECISION_MANUFACTURING,
                    "/producao",
                ),
            ]
        else:
            menu_items = [
                self.criar_item_menu(
                    "Produção",
                    ft.Icons.PRECISION_MANUFACTURING,
                    "/producao",
                ),
            ]

        # =========================
        # RODAPÉ
        # =========================
        rodape = ft.Container(
            content=self.criar_item_menu(
                "Sair",
                ft.Icons.LOGOUT,
                "/login",
                estilo="danger",
            ),
            margin=ft.margin.only(top=10),
        )

        # =========================
        # CONTEÚDO FINAL
        # =========================
        self.content = ft.ListView(
            expand=True,
            spacing=10,
            controls=[
                logo,
                ft.Column(menu_items, spacing=5),
                ft.Divider(height=1, color="#F0F0F0"),
                rodape,
            ],
        )

    # ==================================================
    # NAVEGAÇÃO
    # ==================================================
    def navegar(self, e):
        rota = e.control.data

        # Fecha drawer no mobile
        if self.page.drawer:
            try:
                self.page.drawer.open = False
            except Exception:
                pass

        # Logout
        if rota == "/login":
            self.page.user_role = None

        self.page.go(rota)

    # ==================================================
    # ITEM DE MENU
    # ==================================================
    def criar_item_menu(self, texto, icone, rota, estilo="normal"):
        rota_atual = self.page.route
        esta_ativo = rota_atual == rota

        if estilo == "danger":
            cor_item = ft.Colors.RED_600
            bg_item = ft.Colors.RED_50 if esta_ativo else "transparent"
        else:
            cor_item = COLOR_PRIMARY if esta_ativo else ft.Colors.BLUE_GREY_700
            bg_item = f"{COLOR_PRIMARY}10" if esta_ativo else "transparent"

        return ft.Container(
            data=rota,
            on_click=self.navegar,
            padding=12,
            border_radius=12,
            bgcolor=bg_item,
            border=(
                ft.border.only(left=ft.BorderSide(3, COLOR_PRIMARY))
                if esta_ativo and estilo != "danger"
                else None
            ),
            content=ft.Row(
                [
                    ft.Icon(icone, size=22, color=cor_item),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.BOLD if esta_ativo else ft.FontWeight.NORMAL,
                        color=cor_item,
                    ),
                ],
                spacing=15,
            ),
        )
