import flet as ft
import time
import traceback
import warnings

# --- 1. SILENCIADOR DE AVISOS (O "Cala Boca" pro Terminal) ---
# Isso remove todos os textos amarelos de DeprecationWarning
warnings.filterwarnings("ignore")

# --- IMPORTAÇÕES SEGURAS (Auto-Reparo na Importação) ---
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
    # Cria classes vazias para o app não fechar se faltar arquivo
    class LoginView(ft.Container): pass
    class DashboardView(ft.Container): pass

def main(page: ft.Page):
    # --- CONFIGURAÇÃO INICIAL ---
    page.title = "Marmoraria Central"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = COLOR_BACKGROUND
    page.fonts = {"Roboto": "https://fonts.gstatic.com/s/roboto/v20/KFOmCnqEu92Fr1Mu4mxK.woff2"}

    # --- SISTEMA DE AUTO-REPARO (Função Auxiliar) ---
    def executar_seguro(funcao, nome_acao="Ação desconhecida"):
        """Tenta executar algo. Se der erro, loga e segue a vida sem travar."""
        try:
            funcao()
        except Exception as e:
            print(f"❌ Erro recuperado em '{nome_acao}': {e}")
            traceback.print_exc()

    # --- LÓGICA DO TUTORIAL (ONBOARDING) ---
    def executar_tutorial():
        # Verifica se o tutorial já foi visto de forma segura
        try:
            # CORREÇÃO: O método correto é contains_key
            if page.client_storage.contains_key("tutorial_v1_visto"):
                return
        except Exception:
            # Se der erro no storage, assume que já viu e aborta para não travar
            print("⚠️ Erro no ClientStorage, pulando tutorial.")
            return

        passo_atual = [0]
        
        # CORREÇÃO DO ERRO VERMELHO:
        # Removemos 'clickable=True' (que não existe mais) e usamos on_click vazio
        overlay = ft.Container(
            expand=True, 
            bgcolor="#cc000000", 
            padding=20, 
            on_click=lambda _: None # Isso torna o container "clicável" sem dar erro
        )

        def fechar_tutorial(e=None):
            try:
                page.overlay.remove(overlay)
                page.client_storage.set("tutorial_v1_visto", True)
                page.update()
            except: pass

        def proximo_passo(e=None):
            passo_atual[0] += 1
            idx = passo_atual[0]
            overlay.content = None
            
            try:
                if idx == 1:
                    overlay.content = ft.Stack([
                        ft.Container(left=5, top=5, width=50, height=50, border=ft.border.all(2, COLOR_WHITE), border_radius=50),
                        ft.Container(top=70, left=20, content=ft.Column([
                            ft.Text("Menu Principal", size=24, weight="bold", color=COLOR_WHITE),
                            ft.Text("Navegue por aqui.", color="white70"),
                            ft.ElevatedButton("Próximo", on_click=proximo_passo)
                        ]))
                    ])
                elif idx == 2:
                    overlay.content = ft.Container(alignment=ft.alignment.center, content=ft.Column([
                        ft.Icon(ft.icons.ROCKET_LAUNCH, size=50, color=COLOR_WHITE),
                        ft.Text("Vamos começar!", size=30, weight="bold", color=COLOR_WHITE),
                        ft.ElevatedButton("OK", on_click=fechar_tutorial)
                    ], horizontal_alignment="center"))
                else: fechar_tutorial()
                page.update()
            except Exception as e:
                print(f"Erro no passo {idx} do tutorial: {e}")
                fechar_tutorial() # Fecha se der erro visual

        page.overlay.append(overlay)
        proximo_passo()

    # --- ROTAS (Navegação Protegida) ---
    def route_change(route):
        print(f"Navegando para: {page.route}")
        page.views.clear()
        
        try:
            if page.route == "/":
                page.views.append(LoginView(page))
            
            elif page.route == "/dashboard":
                page.views.append(DashboardView(page))
                # Executa tutorial protegido
                executar_seguro(executar_tutorial, "Tutorial Inicial")

            elif page.route == "/estoque": page.views.append(InventoryView(page))
            elif page.route == "/orcamentos": page.views.append(BudgetView(page))
            elif page.route == "/producao": page.views.append(ProductionView(page))
            elif page.route == "/financeiro": page.views.append(FinancialView(page))
            
            page.update()
        
        except Exception as e:
            print(f"🔥 ERRO CRÍTICO NA ROTA {page.route}: {e}")
            traceback.print_exc()
            # AUTO-REPARO: Se a tela falhar, volta pro Login ou mostra erro amigável
            page.views.clear()
            page.views.append(ft.View(route="/erro", controls=[
                ft.Text("Ocorreu um erro ao carregar esta tela.", color="red", size=20),
                ft.Text(f"Detalhe: {str(e)}"),
                ft.ElevatedButton("Voltar ao Início", on_click=lambda _: page.go("/"))
            ]))
            page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # --- INICIALIZAÇÃO FIREBASE (Protegida) ---
    def iniciar_servicos():
        try:
            print("Iniciando Firebase...")
            firebase_service.initialize_firebase()
        except Exception as e:
            print(f"⚠️ Erro ao iniciar Firebase (App continuará offline): {e}")

    iniciar_servicos()

    # Força a tela inicial
    page.go(page.route)

# --- PROTEÇÃO CONTRA DUPLA EXECUÇÃO ---
if __name__ == "__main__":
    # Tenta abrir no navegador. Se o navegador falhar, não crasha o script.
    try:
        ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER)
    except Exception as e:
        print(f"Erro fatal ao iniciar Flet: {e}")
        input("Pressione ENTER para sair...")