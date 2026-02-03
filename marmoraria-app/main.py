import flet as ft
import os
import sys
import traceback

from src.config import COLOR_BACKGROUND, COLOR_PRIMARY

# =========================================================
# Garante que o Python encontre a pasta 'src'
# (Funciona em ambiente local e no Render)
# =========================================================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main(page: ft.Page):
    # -----------------------------------------------------
    # CONFIGURAÇÕES BÁSICAS DA PÁGINA
    # -----------------------------------------------------
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = COLOR_BACKGROUND

    page.theme = ft.Theme(
        color_scheme_seed=COLOR_PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # -----------------------------------------------------
    # FUNÇÃO DE CONTROLE DE ROTAS
    # -----------------------------------------------------
    def route_change(e):
        page.views.clear()
        rota_atual = page.route

        # ------------------ AUTH GUARD --------------------
        # Se não estiver logado e tentar acessar rota protegida
        user_role = page.session.get("user_role")
        if not user_role and rota_atual not in ["/login", "/", ""]:
            page.go("/login")
            return

        # ------------------ BUILDER DE VIEW ----------------
        def construir_view(view_func, route_name):
            try:
                conteudo_layout = view_func(page)

                appbar = None
                drawer = None

                # Extração automática de appbar e drawer
                if hasattr(conteudo_layout, "data") and isinstance(conteudo_layout.data, dict):
                    appbar = conteudo_layout.data.get("appbar")
                    drawer = conteudo_layout.data.get("drawer")

                page.views.append(
                    ft.View(
                        route=route_name,
                        controls=[conteudo_layout],
                        appbar=appbar,
                        drawer=drawer,
                        padding=0,
                        bgcolor=COLOR_BACKGROUND,
                    )
                )

            except Exception as err:
                print(f"Erro crítico na rota {route_name}:")
                traceback.print_exc()

                page.views.append(
                    ft.View(
                        "/erro",
                        [
                            ft.SafeArea(
                                ft.Text(
                                    f"Ops! Algo deu errado ao carregar esta tela.\n{err}",
                                    color="red",
                                )
                            )
                        ],
                    )
                )

        # ------------------ MAPEAMENTO DE ROTAS ----------------
        if rota_atual in ["/", "", "/login"]:
            from src.views.login_view import LoginView

            page.views.append(
                ft.View(
                    route="/login",
                    controls=[LoginView(page)],
                    padding=0,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        elif rota_atual == "/dashboard":
            from src.views.dashboard_view import DashboardView
            construir_view(DashboardView, "/dashboard")

        elif rota_atual == "/estoque":
            from src.views.inventory_view import InventoryView
            construir_view(InventoryView, "/estoque")

        elif rota_atual == "/orcamentos":
            try:
                # Importação local para evitar problemas de dependência circular
                from src.views.budget_view import BudgetView
                construir_view(BudgetView, "/orcamentos")
            except AttributeError as e:
                print(f"ERRO DE ATRIBUTO DETECTADO: {e}")
                # Isso confirma se o problema é o UserControl
                traceback.print_exc()

        elif rota_atual == "/financeiro":
            from src.views.financial_view import FinancialView
            construir_view(FinancialView, "/financeiro")

        elif rota_atual == "/producao":
            from src.views.production_view import ProductionView
            construir_view(ProductionView, "/producao")

        page.update()

    # -----------------------------------------------------
    # EVENTOS
    # -----------------------------------------------------
    page.on_route_change = route_change

    # -----------------------------------------------------
    # INICIALIZAÇÃO
    # -----------------------------------------------------
    if page.route in ["", "/"]:
        page.go("/login")
    else:
        page.update()


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))

    ft.app(
        target=main,
        assets_dir="assets",
    )