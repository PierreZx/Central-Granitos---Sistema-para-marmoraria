import flet as ft
from src.config import COLOR_PRIMARY, COLOR_TEXT, COLOR_WHITE, SHADOW_MD

class Sidebar(ft.Container):
    def __init__(self, page, is_mobile=False):
        super().__init__()
        self.page = page
        
        # Configuração de Estrutura
        if is_mobile:
            self.width = None
            self.expand = True
            self.bgcolor = COLOR_WHITE
            padding_bottom = 20
        else:
            self.width = 260
            self.expand = True 
            self.bgcolor = COLOR_WHITE
            # Linha sutil de separação à direita
            self.border = ft.border.only(right=ft.border.BorderSide(1, "#F0F0F0"))
            padding_bottom = 10
        
        self.padding = ft.padding.only(left=15, right=15, top=25, bottom=padding_bottom)
        user_role = self.page.session.get("user_role")
        
        # --- CABEÇALHO ---
        logo = ft.Container(
            content=ft.Row([
                ft.Container(
                    width=38, height=38, border_radius=10, bgcolor=COLOR_PRIMARY,
                    content=ft.Icon(ft.icons.PRECISION_MANUFACTURING_ROUNDED, color=COLOR_WHITE, size=20)
                ),
                ft.Text("CENTRAL", size=20, weight="bold", color=COLOR_PRIMARY, letter_spacing=1)
            ], spacing=12),
            margin=ft.margin.only(bottom=30, left=5)
        )

        # --- ITENS DE MENU ---
        menu_items = []
        if user_role == "admin":
            menu_items = [
                self.criar_item_menu("Dashboard", ft.icons.GRID_VIEW_ROUNDED, "/dashboard"),
                self.criar_item_menu("Estoque", ft.icons.INVENTORY_2_OUTLINED, "/estoque"),
                self.criar_item_menu("Orçamentos", ft.icons.RECEIPT_LONG_ROUNDED, "/orcamentos"),
                self.criar_item_menu("Financeiro", ft.icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "/financeiro"),
                self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING_OUTLINED, "/producao"),
            ]
        else:
            menu_items = [
                self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING_OUTLINED, "/producao"),
            ]

        # Botão de Sair destacado no rodapé
        rodape = ft.Container(
            content=self.criar_item_menu("Sair do Sistema", ft.icons.LOGOUT_ROUNDED, "/login", estilo="danger"),
            margin=ft.margin.only(top=10)
        )

        self.content = ft.Column(
            [
                logo,
                ft.Column(menu_items, spacing=5, expand=True),
                ft.Divider(height=1, color="#F0F0F0"),
                rodape
            ], 
            spacing=0, 
            expand=True
        )

    def navegar(self, e):
        rota = e.control.data
        if self.page.drawer:
            self.page.drawer.open = False
        # Se for sair, limpa a sessão
        if rota == "/login":
            self.page.session.clear()
        self.page.go(rota)

    def criar_item_menu(self, texto, icone, rota, estilo="normal"):
        esta_ativo = self.page.route == rota
        
        # Definição de Cores Baseada no Estado
        if estilo == "danger":
            cor_item = ft.colors.RED_600
            bg_hover = ft.colors.RED_50
        else:
            cor_item = COLOR_PRIMARY if esta_ativo else ft.colors.BLUE_GREY_700
            bg_hover = f"{COLOR_PRIMARY}10" # Vinho com 10% de opacidade

        return ft.Container(
            data=rota,
            on_click=self.navegar,
            padding=ft.padding.symmetric(vertical=12, horizontal=15),
            border_radius=12,
            bgcolor=bg_hover if esta_ativo else ft.colors.TRANSPARENT,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            content=ft.Row([
                ft.Icon(
                    icone, 
                    size=22, 
                    color=cor_item,
                    weight="bold" if esta_ativo else "normal"
                ),
                ft.Text(
                    texto, 
                    size=14, 
                    weight="bold" if esta_ativo else "w500",
                    color=cor_item
                ),
            ], spacing=15),
            # Efeito visual de "selecionado"
            border=ft.border.only(left=ft.border.BorderSide(3, COLOR_PRIMARY)) if esta_ativo and estilo != "danger" else None
        )