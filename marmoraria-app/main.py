import flet as ft
import os
import sys
import traceback
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY
from src.services import firebase_service

# Garante que o Python encontre a pasta 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main(page: ft.Page):
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = COLOR_BACKGROUND
    
    # Configuração de estilo global
    page.theme = ft.Theme(
        color_scheme_seed=COLOR_PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # --- AJUSTE APK: Sincronização em segundo plano ---
    def inicializar_sincronizacao():
        """Sincroniza sem travar a abertura do app"""
        try:
            if firebase_service.verificar_conexao():
                # Sincroniza em background
                firebase_service.sync_offline_data()
                # Faz o cache sem bloquear a UI
                firebase_service.get_collection("estoque")
        except Exception as e:
            print(f"Erro silencioso na sincronização inicial: {e}")

    def route_change(e):
        page.views.clear()
        rota_atual = page.route

        # 1. VERIFICAÇÃO DE SEGURANÇA
        user_role = page.session.get("user_role")
        
        # Se não houver sessão, força Login exceto se já estiver indo para lá
        if not user_role and rota_atual not in ["/login", "/", ""]:
            page.go("/login")
            return

        # 2. CONSTRUÇÃO DE VIEWS COM TRATAMENTO DE ERRO
        def construir_view(view_func, route_name):
            try:
                # O segredo: Pegar as propriedades especiais de LayoutBase que injetamos
                layout_result = view_func(page)
                
                # Se o layout_result for um Container com metadados do AppBar/Drawer
                appbar = None
                drawer = None
                
                if hasattr(layout_result, "data") and isinstance(layout_result.data, dict):
                    appbar = layout_result.data.get("appbar")
                    drawer = layout_result.data.get("drawer")

                page.views.append(
                    ft.View(
                        route_name,
                        [layout_result],
                        appbar=appbar, # Injeta nativamente no APK
                        drawer=drawer, # Injeta nativamente no APK
                        padding=0,
                        bgcolor=COLOR_BACKGROUND
                    )
                )
            except Exception as ex:
                page.views.append(
                    ft.View("/erro", [ft.Text(f"Erro na tela {route_name}:\n{ex}", color="red")])
                )

        # --- MAPEAMENTO DE ROTAS ---
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
    
    # Inicialização do App: Sempre abre no Login primeiro para garantir a sessão
    page.go("/login")
    
    # Roda a sincronização APÓS o app já estar aberto e visível
    inicializar_sincronizacao()

if __name__ == "__main__":
    # assets_dir="assets" é vital para o ícone e imagens locais
    ft.app(target=main, assets_dir="assets")