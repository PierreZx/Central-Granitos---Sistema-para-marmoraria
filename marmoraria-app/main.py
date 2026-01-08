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
        
        # ROTA DE LOGIN
        if page.route == "/login" or page.route == "/" or page.route == "":
            try:
                from src.views.login_view import LoginView
                page.views.append(ft.View(route="/login", controls=[LoginView(page)], padding=0))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro ao carregar Login: {err}")]))

        # ROTA DASHBOARD
        elif page.route == "/dashboard":
            try:
                from src.views.dashboard_view import DashboardView
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)], padding=0))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro Dashboard: {err}")]))

        # ROTA ESTOQUE
        elif page.route == "/estoque":
            try:
                from src.views.inventory_view import InventoryView
                page.views.append(ft.View(route="/estoque", controls=[InventoryView(page)], padding=0))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro Estoque: {err}")]))

        # ROTA ORÇAMENTOS
        elif page.route == "/orcamentos":
            try:
                from src.views.budget_view import BudgetView
                page.views.append(ft.View(route="/orcamentos", controls=[BudgetView(page)], padding=0))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro Orçamentos: {err}")]))

        # ROTA FINANCEIRO
        elif page.route == "/financeiro":
            try:
                from src.views.financial_view import FinancialView
                page.views.append(ft.View(route="/financeiro", controls=[FinancialView(page)], padding=0))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro Financeiro: {err}")]))

        # ROTA PRODUÇÃO
        elif page.route == "/producao":
            try:
                from src.views.production_view import ProductionView
                page.views.append(ft.View(route="/producao", controls=[ProductionView(page)], padding=0))
            except Exception as err:
                traceback.print_exc()
                page.views.append(ft.View(route="/erro", controls=[ft.Text(f"Erro Produção: {err}")]))
        
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