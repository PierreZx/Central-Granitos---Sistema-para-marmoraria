import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, 
    COLOR_WHITE, COLOR_WARNING, COLOR_TEXT
)
from src.services import firebase_service

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos", subtitulo=None):
    """
    Layout base unificado. 
    Retorna um Container (Mobile) com metadados ou uma Row (Desktop).
    """
    conectado = firebase_service.verificar_conexao()

    # --- CONFIGURAÇÃO MOBILE (DRAWER) ---
    drawer_mobile = ft.NavigationDrawer(
        controls=[Sidebar(page, is_mobile=True)],
        bgcolor=COLOR_WHITE,
    )
    
    def abrir_menu(e):
        drawer_mobile.open = True
        page.update()

    eh_mobile = page.width < 768

    # --- ELEMENTO DE CONTEÚDO COM ANIMAÇÃO ---
    # Envolvemos o conteúdo em um container para dar um padding padrão e animação
    view_wrapper = ft.Container(
        content=conteudo_principal,
        padding=ft.padding.all(20) if eh_mobile else ft.padding.all(30),
        expand=True,
        animate_opacity=300, # Suaviza a troca de telas
    )

    if eh_mobile:
        # AppBar Mobile com estilo moderno
        app_bar_obj = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.icons.MENU_ROUNDED, 
                icon_color=COLOR_WHITE, 
                on_click=abrir_menu
            ),
            title=ft.Column([
                ft.Text(titulo, size=16, weight="bold", color=COLOR_WHITE),
                ft.Text(subtitulo, size=11, color=COLOR_WHITE) if subtitulo else ft.Container()
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COLOR_PRIMARY,
            center_title=True,
            elevation=0,
        )
        
        # Alerta de Conexão
        barra_status = ft.Container()
        if not conectado:
            barra_status = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.WIFI_OFF, size=14, color=ft.colors.BLACK87),
                    ft.Text("TRABALHANDO OFFLINE", size=11, weight="bold", color=ft.colors.BLACK87),
                ], alignment="center", spacing=5),
                bgcolor=COLOR_WARNING, 
                padding=8,
                width=float("inf")
            )

        # O segredo para o Main ler o AppBar e o Drawer no Mobile
        return ft.Container(
            content=ft.Column([
                barra_status,
                view_wrapper
            ], spacing=0),
            expand=True,
            bgcolor=COLOR_BACKGROUND,
            data={
                "appbar": app_bar_obj,
                "drawer": drawer_mobile
            }
        )
    
    else:
        # --- LAYOUT DESKTOP (SIDEBAR FIXA) ---
        return ft.Row(
            [
                # Sidebar fixa à esquerda
                Sidebar(page),
                
                # Área de conteúdo à direita
                ft.Column([
                    # Barra superior opcional para Desktop se desejar (ou apenas o wrapper)
                    view_wrapper
                ], expand=True, spacing=0)
            ],
            expand=True,
            spacing=0,
            bgcolor=COLOR_BACKGROUND
        )