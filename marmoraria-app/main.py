import flet as ft
import time
import traceback
import warnings
import os

warnings.filterwarnings("ignore")

print("--- 🚀 INICIANDO APLICAÇÃO ---")

# --- TESTE DE IMPORTAÇÕES ---
try:
    print("Tentando importar configurações e views...")
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
    print(f"❌ ERRO NAS IMPORTAÇÕES: {e}")
    traceback.print_exc()

def main(page: ft.Page):
    print(f"--- 👤 Nova sessão iniciada (Rota atual: {page.route}) ---")
    
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    try:
        page.bgcolor = COLOR_BACKGROUND
    except:
        page.bgcolor = "#F5F5F5"

    def route_change(route):
        print(f"🛣️ Mudança de rota detectada: {page.route}")
        try:
            page.views.clear()
            
            if page.route == "/" or page.route == "/login":
                print("Exibindo tela de LOGIN")
                page.views.append(ft.View(route="/login", controls=[LoginView(page)]))
            
            elif page.route == "/dashboard":
                print("Exibindo tela de DASHBOARD")
                page.views.append(ft.View(route="/dashboard", controls=[DashboardView(page)]))
            
            # Adicione aqui as outras rotas se necessário...
            
            page.update()
            print("✅ Página atualizada com sucesso")
        except Exception as e:
            print(f"🔥 ERRO DENTRO DA ROTA: {e}")
            traceback.print_exc()

    page.on_route_change = route_change
    
    # --- INICIALIZAÇÃO FIREBASE ---
    try:
        print("Iniciando Firebase Service...")
        firebase_service.initialize_firebase()
        print("✅ Firebase iniciado!")
    except Exception as e:
        print(f"⚠️ Erro Firebase: {e}")

    # Força a ida para a tela inicial
    print("Redirecionando para rota inicial...")
    page.go(page.route)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        assets_dir="assets" # Garante que o Flet saiba onde as imagens estão
    )