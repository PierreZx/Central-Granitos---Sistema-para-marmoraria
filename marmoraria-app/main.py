import flet as ft
import os
import traceback

def main(page: ft.Page):
    # Configurações brutas (sem depender de src.config)
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F5F5F5" 
    
    # Removendo fontes personalizadas temporariamente para evitar erro de download
    page.fonts = {}

    def route_change(route):
        print(f"Rota alterada: {page.route}")
        page.views.clear()
        
        try:
            if page.route == "/login" or page.route == "/":
                from src.views.login_view import LoginView
                # Passamos a página para a view
                page.views.append(ft.View(route="/login", controls=[LoginView(page)]))
            elif page.route == "/dashboard":
                from src.views.dashboard_view import DashboardView
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)]))
            # Se precisar de outras rotas agora, use o mesmo padrão acima
            
            page.update()
        except Exception as e:
            print(f"Erro fatal na rota: {e}")
            traceback.print_exc()
            page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro: {str(e)}")]))
            page.update()

    page.on_route_change = route_change
    
    # Inicialização direta
    if page.route == "/" or page.route == "":
        page.go("/login")
    else:
        page.go(page.route)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port
    )