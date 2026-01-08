import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_WARNING, COLOR_TEXT
from src.services import firebase_service

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos"):
    conectado = firebase_service.verificar_conexao()
    
    def abrir_menu(e):
        # 1. Criamos o drawer se ele não existir ou para garantir atualização
        page.drawer = ft.NavigationDrawer(
            controls=[Sidebar(page, is_mobile=True)],
            bgcolor=ft.colors.WHITE,
        )
        # 2. Mudamos o estado para aberto
        page.drawer.open = True
        # 3. Damos o update na PÁGINA inteira para o Flet processar a abertura
        page.update()

    eh_mobile = page.width < 768

    if eh_mobile:
        # Criamos o AppBar
        app_bar_obj = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.icons.MENU, 
                icon_color=COLOR_WHITE, 
                on_click=abrir_menu
            ),
            title=ft.Text(titulo, size=18, weight="bold", color=COLOR_WHITE),
            bgcolor=COLOR_PRIMARY,
            center_title=True,
        )
        
        barra_offline = ft.Container()
        if not conectado:
            barra_offline = ft.Container(
                content=ft.Text("MODO OFFLINE", size=11, color="black", weight="bold"),
                bgcolor=COLOR_WARNING, 
                padding=5, 
                alignment=ft.alignment.center,
                width=float("inf")
            )

        # IMPORTANTE: No Flet Web moderno, retornamos um Column que contém a lógica,
        # Mas o AppBar nós vamos tratar de forma que o Main possa ler.
        # Para resolver o erro "Unknown control", o segredo está em como o Container é montado:
        
        return ft.Container(
            content=ft.Column([
                # Removi o app_bar de dentro dos controls da Column
                barra_offline,
                ft.Container(
                    content=conteudo_principal, 
                    padding=ft.padding.only(left=15, right=15, top=20, bottom=20), 
                    expand=True
                )
            ], spacing=0),
            expand=True,
            bgcolor=COLOR_BACKGROUND,
            # Passamos o appbar como uma propriedade do objeto que retorna (se possível) 
            # ou garantimos que o Main o adicione.
            data=app_bar_obj # Guardamos o objeto appbar aqui para o main buscar
        )
        
    else:
        return ft.Row(
            [
                Sidebar(page), 
                ft.Container(content=conteudo_principal, expand=True, padding=30)
            ],
            expand=True,
            spacing=0
        )