import flet as ft
import os
import sys
import traceback

# Garante que o Python encontre a pasta 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main(page: ft.Page):
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F5F5F5"

    def route_change(e):
        page.views.clear()
        
        # Rota de Login (Raiz)
        if page.route == "/login" or page.route == "/" or page.route == "":
            try:
                from src.views.login_view import LoginView
                # Usamos um try/except interno para capturar erro na View
                page.views.append(ft.View(route="/login", controls=[LoginView(page)]))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro ao carregar Login: {err}")]))

        # Rota Dashboard
        elif page.route == "/dashboard":
            try:
                from src.views.dashboard_view import DashboardView
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)]))
            except Exception as err:
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro Dashboard: {err}")]))
        
        # Adicione aqui as outras rotas (estoque, financeiro...) conforme for testando
        
        page.update()

    page.on_route_change = route_change
    
    # Redirecionamento inicial
    if page.route == "/" or page.route == "":
        page.go("/login")
    else:
        page.update()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        assets_dir="assets"
    )