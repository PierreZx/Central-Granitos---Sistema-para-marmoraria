import flet as ft
# Importando todas as views
from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.views.inventory_view import InventoryView
from src.views.budget_view import BudgetView       # <--- NOVO
from src.views.production_view import ProductionView # <--- NOVO
from src.views.financial_view import FinancialView   # <--- NOVO

from src.config import COLOR_PRIMARY
from src.services import firebase_service

def main(page: ft.Page):
    page.title = "Central Granitos - Sistema de Gestão"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=COLOR_PRIMARY))
    
    # Inicializa Firebase
    try:
        firebase_service.initialize_firebase()
    except Exception as e:
        print(f"Erro inicial: {e}")

    def route_change(route):
        page.views.clear()
        
        # --- ROTEAMENTO ---
        
        if page.route == "/":
            page.views.append(LoginView(page))
        
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page))
        
        elif page.route == "/estoque":
            page.views.append(InventoryView(page))
            
        elif page.route == "/orcamentos":
            page.views.append(BudgetView(page))
            
        elif page.route == "/producao":
            page.views.append(ProductionView(page))
            
        elif page.route == "/financeiro":
            page.views.append(FinancialView(page))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")