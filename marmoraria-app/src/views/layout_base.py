# src/views/layout_base.py
import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import (
    COLOR_PRIMARY, COLOR_BACKGROUND, 
    COLOR_WHITE, COLOR_WARNING
)
from src.services import firebase_service

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos", subtitulo=None):
    """
    Layout base unificado e adaptado para APK. 
    Gerencia a barra de status offline e a navegação mobile.
    """
    conectado = firebase_service.verificar_conexao() #

    # --- CONFIGURAÇÃO DRAWER (Menu Lateral) ---
    # No APK, o Drawer precisa ser definido para a página
    drawer_mobile = ft.NavigationDrawer(
        controls=[Sidebar(page, is_mobile=True)],
        bgcolor=COLOR_WHITE,
    )
    
    def abrir_menu(e):
        page.drawer = drawer_mobile
        page.drawer.open = True
        page.update()

    # Identifica se é mobile baseado na largura ou na plataforma
    # Para o APK, costuma ser True na maioria dos dispositivos
    eh_mobile = page.width < 768 

    # --- WRAPPER DE CONTEÚDO ---
    view_wrapper = ft.Container(
        content=conteudo_principal,
        padding=ft.padding.all(15) if eh_mobile else ft.padding.all(30),
        expand=True,
    )

    if eh_mobile:
        # AppBar Estilizada para Android
        app_bar_obj = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.icons.MENU_ROUNDED, 
                icon_color=COLOR_WHITE, 
                on_click=abrir_menu
            ),
            title=ft.Column([
                ft.Text(titulo, size=16, weight="bold", color=COLOR_WHITE),
                ft.Text(subtitulo, size=10, color=COLOR_WHITE) if subtitulo else ft.Container()
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COLOR_PRIMARY,
            center_title=True,
            elevation=2, # Sombra leve para destacar no celular
        )
        
        # Barra de Status Offline (Vital para a Central Granitos saber se o dado subiu)
        barra_status = ft.Container()
        if not conectado:
            barra_status = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.WIFI_OFF_ROUNDED, size=14, color=ft.colors.BLACK87),
                    ft.Text("MODO OFFLINE ATIVO", size=10, weight="bold", color=ft.colors.BLACK87),
                ], alignment="center", spacing=5),
                bgcolor=COLOR_WARNING, 
                padding=5,
                width=float("inf")
            )

        # Atualiza as propriedades da página para o Flet renderizar corretamente no APK
        page.appbar = app_bar_obj
        page.drawer = drawer_mobile

        return ft.Column([
                barra_status,
                view_wrapper
            ], spacing=0, expand=True)
    
    else:
        # --- LAYOUT DESKTOP (SIDEBAR FIXA) ---
        # Reseta elementos mobile se estiver em tela grande
        page.appbar = None
        page.drawer = None
        
        return ft.Row(
            [
                Sidebar(page),
                ft.Column([view_wrapper], expand=True, spacing=0)
            ],
            expand=True,
            spacing=0,
            bgcolor=COLOR_BACKGROUND
        )