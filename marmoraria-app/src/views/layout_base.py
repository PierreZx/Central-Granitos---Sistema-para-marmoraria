import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_WARNING, COLOR_TEXT
from src.services import firebase_service
from src.services import notification_service

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos"):
    conectado = firebase_service.verificar_conexao()
    perfil = page.session.get("user_role")
    
    # --- MENU LATERAL PARA CELULAR (DRAWER) ---
    drawer_mobile = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            ft.Container(
                content=ft.Text("MENU", weight="bold", size=16, color=COLOR_PRIMARY),
                padding=20
            ),
            ft.Divider(thickness=1, color=ft.colors.GREY_200),
            ft.NavigationDrawerDestination(label="Dashboard", icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD),
            ft.NavigationDrawerDestination(label="Estoque", icon=ft.icons.INVENTORY_2_OUTLINED, selected_icon=ft.icons.INVENTORY_2),
            ft.NavigationDrawerDestination(label="Orçamentos", icon=ft.icons.DESCRIPTION_OUTLINED, selected_icon=ft.icons.DESCRIPTION),
            ft.NavigationDrawerDestination(label="Financeiro", icon=ft.icons.ATTACH_MONEY_OUTLINED, selected_icon=ft.icons.ATTACH_MONEY),
            ft.Divider(),
            ft.NavigationDrawerDestination(label="Sair", icon=ft.icons.LOGOUT),
        ],
        on_change=lambda e: (
            page.go("/dashboard") if e.control.selected_index == 2 else 
            page.go("/estoque") if e.control.selected_index == 3 else
            page.go("/orcamentos") if e.control.selected_index == 4 else
            page.go("/financeiro") if e.control.selected_index == 5 else
            page.go("/login") if e.control.selected_index == 7 else None
        )
    )

    def show_drawer(e):
        page.drawer = drawer_mobile
        drawer_mobile.open = True
        page.update()

    eh_mobile = page.width < 768

    if eh_mobile:
        # BARRA SUPERIOR (Onde fica o botão de menu)
        app_bar = ft.AppBar(
            leading=ft.IconButton(ft.icons.MENU, icon_color=COLOR_WHITE, on_click=show_drawer),
            title=ft.Text(titulo, size=18, weight="bold", color=COLOR_WHITE),
            bgcolor=COLOR_PRIMARY,
            center_title=True,
        )
        
        # BARRA OFFLINE
        barra_offline = ft.Container()
        if not conectado:
            barra_offline = ft.Container(
                content=ft.Text("MODO OFFLINE", size=11, color="black", weight="bold"),
                bgcolor=COLOR_WARNING, padding=5, alignment=ft.alignment.center
            )

        # RETORNO DO CELULAR COM PADDING (MARGEM NAS LATERAIS)
        return ft.Container(
            content=ft.Column([
                app_bar,
                barra_offline,
                ft.Container(content=conteudo_principal, padding=20, expand=True) # Padding aqui dá o respiro nas bordas
            ], spacing=0),
            expand=True,
            bgcolor=COLOR_BACKGROUND
        )
        
    else:
        # RETORNO DESKTOP (SIDEBAR FIXA)
        return ft.Row(
            [
                Sidebar(page), 
                ft.Container(content=conteudo_principal, expand=True, padding=30)
            ],
            expand=True,
            spacing=0
        )