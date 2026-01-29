import flet as ft
from src.config import COLOR_PRIMARY, COLOR_TEXT, COLOR_WHITE


class Sidebar(ft.Container):
    def __init__(self, page: ft.Page, is_mobile: bool = False):
        super().__init__()

        self._page_ref = page

        # =========================
        # CONFIGURAÇÃO BASE
        # =========================
        self.bgcolor = COLOR_WHITE
        self.padding = 20

        if not is_mobile:
            self.width = 260
            self.border = ft.Border(
                right=ft.BorderSide(1, "#F0F0F0")
            )

        # Papel do usuário
        user_role = getattr(self._page_ref, "user_role", None)

        # =========================
        # LOGO / CABEÇALHO
        # =========================
        logo = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        border_radius=10,
                        bgcolor=COLOR_PRIMARY,
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            "precision_manufacturing",
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
                self.criar_item_menu("Dashboard", "grid_view", "/dashboard"),
                self.criar_item_menu("Estoque", "inventory_2", "/estoque"),
                self.criar_item_menu("Orçamentos", "receipt_long", "/orcamentos"),
                self.criar_item_menu(
                    "Financeiro",
                    "account_balance_wallet",
                    "/financeiro",
                ),
                self.criar_item_menu(
                    "Produção",
                    "precision_manufacturing",
                    "/producao",
                ),
            ]
        else:
            menu_items = [
                self.criar_item_menu(
                    "Produção",
                    "precision_manufacturing",
                    "/producao",
                ),
            ]

        # =========================
        # RODAPÉ
        # =========================
        rodape = ft.Container(
            content=self.criar_item_menu(
                "Sair",
                "logout",
                "/login",
                estilo="danger",
            ),
            margin=ft.margin.only(top=10),
        )

        # =========================
        # CONTEÚDO FINAL
        # =========================
        self.content = ft.ListView(
            controls=[
                logo,
                ft.Column(menu_items, spacing=5),
                ft.Divider(height=1, color="#F0F0F0"),
                rodape,
            ],
            expand=True,
            spacing=10,
        )

    # ==================================================
    # NAVEGAÇÃO
    # ==================================================
    def navegar(self, e):
        rota = e.control.data

        # Fecha drawer no mobile (compatível 0.23.2)
        try:
            if self._page_ref.drawer:
                self._page_ref.close(self._page_ref.drawer)
        except Exception:
            pass

        # Logout
        if rota == "/login":
            setattr(self._page_ref, "user_role", None)

        self._page_ref.go(rota)

    # ==================================================
    # ITEM DE MENU
    # ==================================================
    def criar_item_menu(self, texto, icone, rota, estilo="normal"):
        esta_ativo = self._page_ref.route == rota

        if estilo == "danger":
            cor_item = "red600"
            bg_item = "red50" if esta_ativo else "transparent"
        else:
            cor_item = COLOR_PRIMARY if esta_ativo else "bluegrey700"
            bg_item = f"{COLOR_PRIMARY}10" if esta_ativo else "transparent"

        return ft.Container(
            data=rota,
            on_click=self.navegar,
            padding=12,
            border_radius=12,
            bgcolor=bg_item,
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icone,
                        size=22,
                        color=cor_item,
                    ),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.BOLD
                        if esta_ativo
                        else "normal",
                        color=cor_item,
                    ),
                ],
                spacing=15,
            ),
            border=(
                ft.border.only(
                    left=ft.BorderSide(3, COLOR_PRIMARY)
                )
                if esta_ativo and estilo != "danger"
                else None
            ),
        )
