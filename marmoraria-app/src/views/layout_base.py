import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_WARNING, COLOR_TEXT
from src.services import firebase_service

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos"):
    # Verifica status de conexão
    conectado = firebase_service.verificar_conexao()
    
    # --- FUNÇÃO PARA ABRIR O MENU NO CELULAR ---
    def abrir_menu(e):
        # Usamos a sua Sidebar customizada dentro do Drawer
        page.drawer = ft.NavigationDrawer(
            controls=[
                Sidebar(page, is_mobile=True)
            ],
            bgcolor=ft.colors.WHITE,
        )
        page.drawer.open = True
        page.update()

    eh_mobile = page.width < 768

    if eh_mobile:
        # BARRA SUPERIOR (Botão de Menu + Título)
        app_bar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.icons.MENU, 
                icon_color=COLOR_WHITE, 
                on_click=abrir_menu
            ),
            title=ft.Text(titulo, size=18, weight="bold", color=COLOR_WHITE),
            bgcolor=COLOR_PRIMARY,
            center_title=True,
            elevation=2,
        )
        
        # BARRA DE AVISO OFFLINE
        barra_offline = ft.Container()
        if not conectado:
            barra_offline = ft.Container(
                content=ft.Text("MODO OFFLINE", size=11, color="black", weight="bold"),
                bgcolor=COLOR_WARNING, 
                padding=5, 
                alignment=ft.alignment.center,
                width=float("inf")
            )

        # LAYOUT MOBILE: AppBar + Conteúdo com Padding Lateral
        return ft.Container(
            content=ft.Column([
                app_bar,
                barra_offline,
                ft.Container(
                    content=conteudo_principal, 
                    padding=ft.padding.only(left=15, right=15, top=20, bottom=20), 
                    expand=True
                )
            ], spacing=0),
            expand=True,
            bgcolor=COLOR_BACKGROUND
        )
        
    else:
        # LAYOUT DESKTOP: Sidebar Fixa + Conteúdo
        return ft.Row(
            [
                Sidebar(page), 
                ft.Container(
                    content=conteudo_principal, 
                    expand=True, 
                    padding=30
                )
            ],
            expand=True,
            spacing=0
        )