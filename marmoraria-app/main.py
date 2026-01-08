import flet as ft
import os
import sys
import traceback
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY

# Garante que o Python encontre a pasta 'src' em qualquer ambiente (Local ou Render)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main(page: ft.Page):
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = COLOR_BACKGROUND
    
    # Configuração de fontes e estilo global (opcional)
    page.theme = ft.Theme(
        color_scheme_seed=COLOR_PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    def route_change(e):
        page.views.clear()
        rota_atual = page.route

        # 1. VERIFICAÇÃO DE SEGURANÇA
        # Se não houver role na sessão e não for login, manda pro login
        user_role = page.session.get("user_role")
        if not user_role and rota_atual not in ["/login", "/", ""]:
            page.go("/login")
            return

        # 2. FUNÇÃO PARA CONSTRUIR AS VIEWS
        def construir_view(view_func, route_name):
            try:
                # Carrega o conteúdo da View
                conteudo_layout = view_func(page)
                
                # Extração automática dos metadados do LayoutBase
                res_appbar = None
                res_drawer = None
                
                if hasattr(conteudo_layout, 'data') and isinstance(conteudo_layout.data, dict):
                    res_appbar = conteudo_layout.data.get("appbar")
                    res_drawer = conteudo_layout.data.get("drawer")

                page.views.append(
                    ft.View(
                        route=route_name,
                        controls=[conteudo_layout],
                        appbar=res_appbar,
                        drawer=res_drawer,
                        padding=0,
                        bgcolor=COLOR_BACKGROUND
                    )
                )
            except Exception as err:
                print(f"Erro Crítico na Rota {route_name}:")
                traceback.print_exc()
                # View de Erro Amigável
                page.views.append(
                    ft.View(
                        "/erro", 
                        [ft.SafeArea(ft.Text(f"Ops! Algo deu errado ao carregar esta tela.\n{err}", color="red"))]
                    )
                )

        # 3. MAPEAMENTO DE ROTAS (Lazy Loading)
        if rota_atual in ["/login", "/", ""]:
            from src.views.login_view import LoginView
            page.views.append(
                ft.View("/login", [LoginView(page)], padding=0, vertical_alignment="center", horizontal_alignment="center")
            )

        elif rota_atual == "/dashboard":
            from src.views.dashboard_view import DashboardView
            construir_view(DashboardView, "/dashboard")

        elif rota_atual == "/estoque":
            from src.views.inventory_view import InventoryView
            construir_view(InventoryView, "/estoque")

        elif rota_atual == "/orcamentos":
            from src.views.budget_view import BudgetView
            construir_view(BudgetView, "/orcamentos")

        elif rota_atual == "/financeiro":
            from src.views.financial_view import FinancialView
            construir_view(FinancialView, "/financeiro")

        elif rota_atual == "/producao":
            from src.views.production_view import ProductionView
            construir_view(ProductionView, "/producao")

        page.update()

    # Configuração de eventos
    page.on_route_change = route_change
    
    # Inicialização do App
    if page.route in ["/", ""]:
        page.go("/login")
    else:
        page.update()

if __name__ == "__main__":
    # Configuração específica para o RENDER.com (Porta Dinâmica)
    port = int(os.getenv("PORT", 10000))
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        assets_dir="assets"
    )