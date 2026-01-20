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
    
    # Configuração de fontes e estilo global
    page.theme = ft.Theme(
        color_scheme_seed=COLOR_PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # --- INICIALIZAÇÃO APK (OFFLINE/SYNC) ---
    def inicializar_sincronizacao():
        """Tenta sincronizar os dados assim que o app abre"""
        if firebase_service.verificar_conexao():
            # Mostra um aviso discreto que está sincronizando
            page.snack_bar = ft.SnackBar(
                ft.Text("Sincronizando dados com a nuvem..."),
                bgcolor=ft.colors.BLUE_700,
                duration=2000
            )
            page.snack_bar.open = True
            page.update()
            
            # Chama a função de sincronização bidirecional do serviço
            firebase_service.sync_offline_data()
            
            # Atualiza as coleções principais para o cache local
            # Isso garante que o app não fique "feio" ou vazio
            firebase_service.get_collection("estoque")
            firebase_service.get_collection("orcamentos")
            firebase_service.get_collection("financeiro")
            
    # Executa a sincronização inicial
    inicializar_sincronizacao()

    def route_change(e):
        page.views.clear()
        rota_atual = page.route

        # Sempre que mudar de tela, tenta empurrar mudanças pendentes se houver net
        if firebase_service.verificar_conexao():
            firebase_service.sync_offline_data()

        # 1. VERIFICAÇÃO DE SEGURANÇA
        user_role = page.session.get("user_role")
        if not user_role and rota_atual not in ["/login", "/", ""]:
            page.go("/login")
            return

        # 2. FUNÇÃO PARA CONSTRUIR AS VIEWS
        def construir_view(view_func, route_name):
            try:
                conteudo_layout = view_func(page)
                
                # Se a view retornar um LayoutBase, o Flet precisa do .content
                # (Ajuste caso suas views retornem o objeto LayoutBase diretamente)
                page.views.append(
                    ft.View(
                        route_name,
                        [conteudo_layout],
                        padding=0,
                        bgcolor=COLOR_BACKGROUND
                    )
                )
            except Exception as e:
                print(f"Erro ao construir view {route_name}: {e}")
                traceback.print_exc()
                page.views.append(
                    ft.View(
                        "/erro",
                        [ft.Text(f"Erro Crítico na Rota {route_name}:\n{e}", color="red")],
                        padding=20
                    )
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
    
    # Inicialização do App
    if page.route in ["/", ""]:
        page.go("/login")
    else:
        # Força o trigger da rota atual caso o app seja reiniciado em uma tela específica
        page.go(page.route)

if __name__ == "__main__":
    # Para o APK, usamos o flet.app normal
    # O parâmetro assets_dir é importante se você tiver imagens locais
    ft.app(target=main, assets_dir="assets")