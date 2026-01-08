import flet as ft
import os
import traceback

# Configurações de cores padrão caso o import falhe (evita o erro 'Null')
COLOR_BG = "#F5F5F5"
COLOR_PR = "#722F37" # Vinho

def main(page: ft.Page):
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = COLOR_BG

    def route_change(route):
        page.views.clear()
        
        try:
            # Rota de Login
            if page.route == "/" or page.route == "/login":
                from src.views.login_view import LoginView
                page.views.append(ft.View(route="/login", controls=[LoginView(page)]))
            
            # Rota Dashboard
            elif page.route == "/dashboard":
                from src.views.dashboard_view import DashboardView
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)]))
            
            # Outras rotas (Estoque, etc) seguem o mesmo padrão
            # Adiciona aqui conforme necessário...

            page.update()
        except Exception as e:
            print(f"ERRO DE ROTA: {e}")
            page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro: {e}")]))
            page.update()

    page.on_route_change = route_change
    
    # Inicialização segura
    if page.route == "/":
        page.go("/login")
    else:
        page.go(page.route)

if __name__ == "__main__":
    # Render usa porta 10000
    port = int(os.getenv("PORT", 10000))
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        assets_dir="assets"
    )