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
        
        # Função auxiliar para montar a View com AppBar e Drawer extraídos do LayoutBase
        def append_view(route_name, view_function):
            try:
                conteudo_layout = view_function(page)
                
                appbar_final = None
                drawer_final = None
                
                if hasattr(conteudo_layout, 'data') and conteudo_layout.data:
                    # Se for o dicionário que configuramos no LayoutBase
                    if isinstance(conteudo_layout.data, dict):
                        appbar_final = conteudo_layout.data.get("appbar")
                        drawer_final = conteudo_layout.data.get("drawer")
                    # Caso seja só o AppBar (backup)
                    elif isinstance(conteudo_layout.data, ft.AppBar):
                        appbar_final = conteudo_layout.data

                page.views.append(
                    ft.View(
                        route=route_name,
                        controls=[conteudo_layout],
                        appbar=appbar_final,
                        drawer=drawer_final, # Agora o Drawer será injetado na View!
                        padding=0
                    )
                )
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro em {route_name}: {err}")]))

        # --- MAPEAMENTO DE ROTAS ---
        if page.route == "/login" or page.route == "/" or page.route == "":
            from src.views.login_view import LoginView
            page.views.append(ft.View(route="/login", controls=[LoginView(page)], padding=0))

        elif page.route == "/dashboard":
            from src.views.dashboard_view import DashboardView
            append_view("/dashboard", DashboardView)

        elif page.route == "/estoque":
            from src.views.inventory_view import InventoryView
            append_view("/estoque", InventoryView)

        elif page.route == "/orcamentos":
            from src.views.budget_view import BudgetView
            append_view("/orcamentos", BudgetView)

        elif page.route == "/financeiro":
            from src.views.financial_view import FinancialView
            append_view("/financeiro", FinancialView)

        elif page.route == "/producao":
            from src.views.production_view import ProductionView
            append_view("/producao", ProductionView)
        
        page.update()

    page.on_route_change = route_change
    
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