import flet as ft
import time
import traceback
import warnings
import os  # Necessário para ler a porta do servidor

# --- 1. SILENCIADOR DE AVISOS ---
warnings.filterwarnings("ignore")

# --- IMPORTAÇÕES SEGURAS ---
try:
    from src.config import COLOR_PRIMARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_SECONDARY
    from src.services import firebase_service
    from src.views.login_view import LoginView
    from src.views.dashboard_view import DashboardView
    from src.views.inventory_view import InventoryView
    from src.views.budget_view import BudgetView
    from src.views.production_view import ProductionView
    from src.views.financial_view import FinancialView
except ImportError as e:
    print(f"⚠️ Erro de importação crítico: {e}")
    class LoginView(ft.Container): pass
    class DashboardView(ft.Container): pass

def main(page: ft.Page):
    # --- CONFIGURAÇÃO INICIAL ---
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F5F5F5" # Valor padrão caso a variável falhe
    
    # Gerenciamento de Rotas
    def route_change(route):
        try:
            page.views.clear()
            
            # Rota de Login (Padrão)
            if page.route == "/" or page.route == "/login":
                page.views.append(ft.View(route="/login", controls=[LoginView(page)]))
            
            # Outras Rotas
            elif page.route == "/dashboard":
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)]))
            elif page.route == "/estoque":
                page.views.append(ft.View(route="/estoque", controls=[InventoryView(page)]))
            elif page.route == "/orcamentos":
                page.views.append(ft.View(route="/orcamentos", controls=[BudgetView(page)]))
            elif page.route == "/producao":
                page.views.append(ft.View(route="/producao", controls=[ProductionView(page)]))
            elif page.route == "/financeiro":
                page.views.append(ft.View(route="/financeiro", controls=[FinancialView(page)]))
            
            page.update()
        except Exception as e:
            print(f"🔥 ERRO NA ROTA: {e}")
            traceback.print_exc()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # --- INICIALIZAÇÃO FIREBASE ---
    def iniciar_servicos():
        try:
            firebase_service.initialize_firebase()
        except Exception as e:
            print(f"⚠️ Erro Firebase: {e}")

    iniciar_servicos()
    page.go(page.route)

# --- EXECUÇÃO PARA WEB (CONFIGURAÇÃO RENDER) ---
if __name__ == "__main__":
    # O Render usa a porta 10000 por padrão, mas fornecida via variável de ambiente
    port = int(os.getenv("PORT", 8000))
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER, # Força o modo navegador
        host="0.0.0.0",               # Permite conexões externas
        port=port                    # Usa a porta do Render
    )