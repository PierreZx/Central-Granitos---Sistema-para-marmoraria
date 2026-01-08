import flet as ft
import traceback
import warnings
import os

# --- 1. SILENCIADOR DE AVISOS ---
warnings.filterwarnings("ignore")

print("--- 🚀 INICIANDO APLICAÇÃO (MODO PRODUÇÃO) ---")

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
    print("✅ Todas as importações feitas com sucesso!")
except Exception as e:
    print(f"❌ ERRO CRÍTICO NAS IMPORTAÇÕES: {e}")
    traceback.print_exc()

def main(page: ft.Page):
    # Configuração de Layout
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Tenta definir cor de fundo das variáveis, se falhar usa padrão
    try:
        page.bgcolor = COLOR_BACKGROUND
    except:
        page.bgcolor = "#F5F5F5"

    def route_change(route):
        print(f"🛣️ Mudança de rota para: {page.route}")
        page.views.clear()
        
        try:
            # Rota Raiz ou Login
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
        except Exception as err:
            print(f"🔥 Erro ao carregar view: {err}")
            traceback.print_exc()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Inicialização do Firebase
    try:
        firebase_service.initialize_firebase()
        print("✅ Firebase pronto.")
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

    # Forçar rota inicial se estiver na raiz
    if page.route == "/":
        page.go("/login")
    else:
        page.go(page.route)

if __name__ == "__main__":
    # O Render usa a porta 10000 por padrão
    port = int(os.getenv("PORT", 10000))
    
    print(f"🌐 Iniciando servidor na porta {port}...")
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        assets_dir="assets" # Importante para carregar imagens da pasta assets
    )