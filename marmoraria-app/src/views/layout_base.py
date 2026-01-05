import flet as ft
from src.views.components.sidebar import Sidebar

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos"):
    """
    Cria um layout que se adapta automaticamente:
    - Desktop: Menu fixo na esquerda.
    - Mobile: Menu 'Hambúrguer' (Drawer) escondido.
    """
    
    # Configura o Menu para ser usado na Gaveta (Mobile)
    # Precisamos de uma instância do Sidebar
    sidebar_conteudo = Sidebar(page)
    
    # Criamos o Drawer (Gaveta Lateral)
    # Usamos o conteúdo do Sidebar dentro dele
    drawer_mobile = ft.NavigationDrawer(
        controls=[
            ft.Container(padding=10, content=sidebar_conteudo)
        ],
        bgcolor=ft.colors.WHITE,
    )

    def abrir_drawer(e):
        page.open_end_drawer() # Abre a gaveta

    # Define a estrutura baseada na largura (Responsividade)
    # Nota: No Flet, para reagir ao redimensionamento em tempo real, precisaríamos de um evento on_resize complexo.
    # Aqui vamos fazer uma verificação na hora de CARREGAR a tela, que resolve 90% dos casos mobile.
    
    eh_mobile = page.width < 768 # Padrão tablet/celular

    if eh_mobile:
        # --- MODO MOBILE ---
        # Barra superior com botão de menu
        app_bar = ft.AppBar(
            title=ft.Text(titulo, size=20, weight="bold", color=ft.colors.WHITE),
            leading=ft.IconButton(ft.icons.MENU, icon_color=ft.colors.WHITE, on_click=lambda e: page.open_drawer()),
            bgcolor=ft.colors.BROWN_700,
            center_title=True
        )
        
        # Registra o drawer na página
        page.drawer = drawer_mobile
        
        return ft.View(
            route=page.route,
            padding=0,
            appbar=app_bar,
            controls=[conteudo_principal],
            drawer=drawer_mobile
        )
        
    else:
        # --- MODO DESKTOP ---
        # Sem AppBar, Menu Fixo na Esquerda
        page.drawer = None # Garante que não tem drawer residual
        return ft.View(
            route=page.route,
            padding=0,
            controls=[
                ft.Row(
                    [
                        Sidebar(page), # Menu Fixo
                        ft.Container(content=conteudo_principal, expand=True)
                    ],
                    expand=True
                )
            ]
        )