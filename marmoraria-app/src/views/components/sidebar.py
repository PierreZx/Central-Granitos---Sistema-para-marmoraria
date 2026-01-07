import flet as ft
from src.config import COLOR_PRIMARY, COLOR_TEXT

class Sidebar(ft.Container):
    def __init__(self, page, is_mobile=False):
        super().__init__()
        self.page = page
        
        # Configurações de layout
        if is_mobile:
            self.width = None
            self.expand = False # Mobile: Não expande (deixa o conteúdo ditar a altura)
            self.border = None
            self.shadow = None
            self.bgcolor = ft.colors.TRANSPARENT
            padding_bottom = 20
        else:
            self.width = 280
            self.expand = True # Desktop: Expande para fixar rodapé embaixo
            self.bgcolor = ft.colors.WHITE
            self.padding = 25
            self.border = ft.border.only(right=ft.border.BorderSide(1, "#00000008"))
            self.shadow = ft.BoxShadow(blur_radius=20, spread_radius=-5, color="#00000005", offset=ft.Offset(5, 0))
            padding_bottom = 5
        
        self.padding = ft.padding.only(left=20, right=20, top=20, bottom=padding_bottom)
        
        # Lógica de menus
        user_role = self.page.session.get("user_role")
        menu_items = []
        
        # --- TOPO: LOGO ---
        logo = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Image(src="logo.jpg", width=36, height=36, fit=ft.ImageFit.CONTAIN),
                    ft.Column([
                        ft.Text("CENTRAL", size=16, weight=ft.FontWeight.W_900, color="#8B4513"),
                        ft.Text("GRANITOS", size=10, weight=ft.FontWeight.W_600, color="#D2691E", style=ft.TextStyle(letter_spacing=1)),
                    ], spacing=0)
                ], spacing=12),
                ft.Divider(height=25, color="#00000008")
            ]),
            padding=ft.padding.only(bottom=10)
        )
        
        if user_role == "producao":
            menu_items = [self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING, "/producao")]
        else:
            menu_items = [
                self.criar_item_menu("Dashboard", ft.icons.DASHBOARD, "/dashboard"),
                self.criar_item_menu("Estoque", ft.icons.INVENTORY_2, "/estoque"),
                self.criar_item_menu("Orçamentos", ft.icons.REQUEST_QUOTE, "/orcamentos"),
                self.criar_item_menu("Produção", ft.icons.PRECISION_MANUFACTURING, "/producao"),
                self.criar_item_menu("Financeiro", ft.icons.PIE_CHART, "/financeiro"),
            ]

        # --- ÁREA DE MENUS ---
        # CORREÇÃO: No mobile, expand=False para não empurrar o rodapé para o além
        area_menus = ft.Column(
            controls=[logo] + menu_items,
            spacing=8,
            scroll=None, 
            expand=not is_mobile # Só expande no Desktop
        )

        # --- RODAPÉ: PERFIL + SAIR ---
        user_profile = ft.Container(
            content=ft.Row([
                ft.Container(
                    width=40, height=40, border_radius=12,
                    gradient=ft.LinearGradient(colors=["#8B451320", "#D2691E10"]),
                    content=ft.Icon(ft.icons.ACCOUNT_CIRCLE if user_role != "producao" else ft.icons.BUILD_CIRCLE, color="#8B4513", size=22),
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text("Produção" if user_role == "producao" else "Admin", size=14, weight=ft.FontWeight.W_600),
                    ft.Text("Logado", size=11, color=ft.colors.GREY_600)
                ], spacing=2)
            ], spacing=15),
            padding=ft.padding.symmetric(vertical=15),
            border=ft.border.only(top=ft.border.BorderSide(1, "#00000008"))
        )

        btn_sair = self.criar_item_menu("Sair", ft.icons.LOGOUT, "/", cor_icone=ft.colors.RED_500, estilo="danger")

        # Container do Rodapé
        rodape = ft.Column([
            ft.Divider(height=20, color="transparent"), # Espaço extra visual
            user_profile,
            ft.Container(height=5),
            btn_sair
        ], spacing=0)

        # --- ESTRUTURA FINAL ---
        self.content = ft.Column(
            controls=[
                area_menus, 
                # Spacer dinâmico: No desktop empurra pra baixo, no mobile não existe
                ft.Container(expand=True) if not is_mobile else ft.Container(height=20),
                rodape
            ], 
            spacing=0, 
            expand=True # O container principal pode expandir, mas o recheio controla o fluxo
        )

    def navegar(self, e):
        rota = e.control.data
        self.page.go(rota)

    def criar_item_menu(self, texto, icone, rota, cor_icone=None, estilo="normal"):
        if cor_icone is None: cor_icone = ft.colors.GREY_600
        
        estilo_btn = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            overlay_color="#00000005",
            color=ft.colors.GREY_700 if estilo != "danger" else ft.colors.RED_600
        )
        
        bg_color = "transparent"
        if self.page.route == rota and estilo != "danger":
            bg_color = "#8B451315" 
            cor_icone = "#8B4513"
        
        return ft.Container(
            content=ft.TextButton(
                content=ft.Row([
                    ft.Icon(icone, size=20, color=cor_icone),
                    ft.Text(texto, size=15),
                ], spacing=15),
                style=estilo_btn,
                on_click=self.navegar,
                data=rota,
            ),
            bgcolor=bg_color,
            border_radius=12,
            padding=ft.padding.only(bottom=5)
        )