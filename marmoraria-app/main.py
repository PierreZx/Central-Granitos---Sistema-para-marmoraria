import flet as ft
from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.config import COLOR_PRIMARY

def main(page: ft.Page):
    # Configurações da Janela
    page.title = "Central Granitos - Sistema de Gestão"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    
    # Aplica a cor da marca no tema global do app
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=COLOR_PRIMARY, # Cor principal do app (barras, botões ativos)
        )
    )
    
    # Sistema de Rotas
    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(LoginView(page))
        
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go(page.route)

if __name__ == "__main__":
    # IMPORTANTE: assets_dir="assets" diz para o Flet onde buscar a logo
    ft.app(target=main, assets_dir="assets")