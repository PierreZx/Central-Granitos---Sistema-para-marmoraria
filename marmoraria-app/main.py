import flet as ft
from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.views.inventory_view import InventoryView
from src.views.budget_view import BudgetView
from src.views.production_view import ProductionView
# from src.views.financial_view import FinancialView 

def main(page: ft.Page):
    # Configurações iniciais
    page.title = "Central Granitos - Sistema de Gestão"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Tema
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BROWN_700,
            secondary=ft.colors.ORANGE_600,
        )
    )

    def route_change(route):
        # Limpa views anteriores
        page.views.clear()
        
        # ROTEAMENTO
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
            page.views.append(ft.View("/financeiro", [
                ft.AppBar(title=ft.Text("Financeiro"), bgcolor=ft.colors.BROWN_700), 
                ft.Container(content=ft.Text("Módulo Financeiro em Breve...", size=20), alignment=ft.alignment.center, expand=True)
            ]))
            
        else:
            page.views.append(LoginView(page))
            
        page.update()

    def view_pop(view):
        # AQUI ESTAVA O PROBLEMA
        # Se tiver histórico, volta normal
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            # Se NÃO tiver histórico (ex: limpamos ao trocar de menu), NÃO FAZ NADA!
            # Ou, se preferir, manda pro Dashboard:
            # if page.route != "/dashboard": page.go("/dashboard")
            pass 

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")