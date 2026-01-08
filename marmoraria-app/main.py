import flet as ft
import os
import traceback

def main(page: ft.Page):
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F5F5F5" 

    def route_change(route):
        page.views.clear()
        try:
            if page.route == "/login" or page.route == "/":
                from src.views.login_view import LoginView
                page.views.append(ft.View(route="/login", controls=[LoginView(page)]))
            elif page.route == "/dashboard":
                from src.views.dashboard_view import DashboardView
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)]))
            
            page.update()
        except Exception as e:
            print(f"Erro na rota: {e}")
            traceback.print_exc()

    page.on_route_change = route_change
    
    # Corrigido: usando push_route e garantindo caminho correto
    if page.route == "/" or page.route == "":
        page.push_route("/login")
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