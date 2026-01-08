import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_WARNING, COLOR_TEXT
from src.services import firebase_service

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos"):
    conectado = firebase_service.verificar_conexao()

    drawer_mobile = ft.NavigationDrawer(
        controls=[Sidebar(page, is_mobile=True)],
        bgcolor=ft.colors.WHITE,
    )
    
    def abrir_menu(e):
        drawer_mobile.open = True
        page.update()

    eh_mobile = page.width < 768

    if eh_mobile:
        app_bar_obj = ft.AppBar(
            leading=ft.IconButton(ft.icons.MENU, icon_color=COLOR_WHITE, on_click=abrir_menu),
            title=ft.Text(
                titulo, 
                size=18, 
                color=COLOR_WHITE,
                style=ft.TextStyle(weight="bold") # CORREÇÃO AQUI
            ),
            bgcolor=COLOR_PRIMARY,
            center_title=True,
        )
        
        barra_offline = ft.Container()
        if not conectado:
            barra_offline = ft.Container(
                content=ft.Text(
                    "MODO OFFLINE", 
                    size=11, 
                    color="black", 
                    style=ft.TextStyle(weight="bold") # CORREÇÃO AQUI
                ),
                bgcolor=COLOR_WARNING, 
                padding=5, 
                alignment=ft.alignment.center,
                width=float("inf")
            )

        return ft.Container(
            content=ft.Column([
                barra_offline,
                ft.Container(content=conteudo_principal, padding=15, expand=True)
            ], spacing=0),
            expand=True,
            bgcolor=COLOR_BACKGROUND,
            data={
                "appbar": app_bar_obj,
                "drawer": drawer_mobile
            }
        )
    else:
        return ft.Row(
            [
                Sidebar(page), 
                ft.Container(content=conteudo_principal, expand=True, padding=30)
            ],
            expand=True,
            spacing=0,
            bgcolor=COLOR_BACKGROUND
        )